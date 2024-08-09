import csv
import json

from omegaconf import OmegaConf
from log.logger import create_logger

config = OmegaConf.load("evaluation/config.yaml")

logger = create_logger("evaluation.log")
logger.setLevel(config.debug_level)

INPUT_DATA_PATH = config.input_data_path
# Select the folder depending whether LLMs are used or not
PROSPECTOR_REPORT_PATH = config.prospector_reports_path
PROSPECTOR_REPORT_PATH_CONTAINER = config.prospector_reports_path_container
ANALYSIS_RESULTS_PATH = config.analysis_results_path
# Comparison dirs
COMPARE_DIRECTORY_1 = config.compare_directory1
COMPARE_DIRECTORY_2 = config.compare_directory2


def load_dataset(path: str):
    with open(path, "r") as file:
        reader = csv.reader(file, delimiter=";")
        logger.debug(f"Loaded Dataset at {path}")
        print(f"Loaded Dataset at {path}")
        return [row for row in reader if "CVE" in row[0] and row[3] != "True"]


def load_json_file(path: str) -> dict:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise
    except Exception:
        raise


def save_dict_to_json(dictionary: dict, path: str):
    with open(path, "w") as file:
        return json.dump(dictionary, file, indent=4)


def update_summary_execution_table(
    mode: str, data, total: str, filepath: str
) -> None:
    """Updates the latex table at {ANALYSIS_RESULTS_PATH}/`file_path`. For this to work, the table latex code from D6.3 for tracer_dataset_results table must be saved in the file.

    Params:
        data (List(List(int, int))): The list of data, each item should be another list of two integers: the total and percentage.
        data_total: The total amount of reports, to be inserted in the last row of the table.

    Saves:
        The newly updated latex table at `file_path`

    Disclaimer: Partly generated with Claude Opus 3.
    """
    # Read the existing LaTeX table from the file
    with open(filepath, "r") as file:
        table_lines = file.readlines()

        # Find the row numbers to edit; CHANGE if table changes!
        lines_to_edit = [5, 8, 11, 14, 17, 18, 19, 20, 21, 22]

        # Update the corresponding columns based on the mode
        if mode == "MVI":
            col_indices = [1, 2]
        elif mode == "AVI":
            col_indices = [3, 4]
        elif mode == "NVI":
            col_indices = [5, 6]
        else:
            raise ValueError(
                "Invalid mode. Please choose from MVI, AVI, or NVI."
            )

        try:
            for i, line_number in enumerate(lines_to_edit):
                row_data = table_lines[line_number].split("&")
                for j, col_index in enumerate(col_indices):
                    row_data[col_index] = str(data[i][j])

                table_lines[line_number] = " & ".join(row_data)
        except IndexError:
            raise IndexError(
                f"Invalid data structure at row {line_number}, column {j}"
            )

        # Add the last row showing the total count
        last_row_data = table_lines[23].split("&")
        last_row_data[col_indices[0]] = f"\\textbf{total}"
        table_lines[23] = " & ".join(last_row_data)

        # Write the updated table back to the file
        with open(filepath, "w") as file:
            file.writelines(table_lines)

    print(f"Updated latex table at {filepath}")
