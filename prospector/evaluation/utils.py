import csv
import json

from omegaconf import OmegaConf
from log.logger import create_logger

config = OmegaConf.load("evaluation/config.yaml")

logger = create_logger("evaluation.log")
logger.setLevel(config.debug_level)


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


def update_summary_execution_table(results: dict, total: str) -> None:
    """Updates the LaTeX table at {ANALYSIS_RESULTS_PATH}/summary_execution_
    [mvi|nvi]_table.tex.

    Params:
        results (dict): Dictionary with result counts.
        total (str): The total amount of reports, to be inserted in the last row of the table.

    Saves:
        The newly updated LaTeX table at `filepath`.
    """
    # Combine the two Cross Reference rules into one count
    if config.batch in ["regular", "old_code"]:
        results["XREF_BUG"] += results["XREF_GH"]
        results.pop("XREF_GH")
    else:
        results["CROSS_REFERENCED_JIRA_LINK"] += results[
            "CROSS_REFERENCED_GH_LINK"
        ]
        results.pop("CROSS_REFERENCED_GH_LINK")

    table_data = []
    for i, (key, v) in enumerate(results.items()):
        v = len(v)
        logger.info(f"\t{v}\t{key}")

        if i > 0 and i < 5:
            total_high_confidence = len(results.get("high"))
            table_data.append([v, round(v / total_high_confidence * 100, 2)])
        else:
            table_data.append([v, round(v / total * 100, 2)])

    # Choose which column to update:
    if config.version_interval:
        filepath = ANALYSIS_RESULTS_PATH + "summary_execution_mvi_table.tex"
        col_indices = [1, 2] if not config.llm_support else [3, 4]

    else:
        filepath = ANALYSIS_RESULTS_PATH + "summary_execution_nvi_table.tex"
        col_indices = [1, 2] if not config.llm_support else [3, 4]

    with open(filepath, "r") as file:
        table_lines = file.readlines()

        # Find the row numbers to edit; CHANGE if table changes!
        lines_to_edit = [5, 8, 11, 14, 17, 20, 21, 22, 23, 24, 25, 26]

        # Update the corresponding columns based on the mode
        try:
            # For every index and line to edit
            for i, line_number in enumerate(lines_to_edit):
                # split the row into parts/sections (at every &)
                columns = table_lines[line_number].split("&")
                # for every index and column in this line (each part is a column, since it's split at &)
                for j, col_index in enumerate(col_indices):
                    # make the text gray if it's the prior eval column
                    if config.batch == "old_reports":
                        columns[col_index] = (
                            f"\\color{{gray}} {table_data[i][j]} "
                        )
                    # else just regular black
                    else:
                        columns[col_index] = f" {table_data[i][j]} "

                # Preserve everything after the last column we're updating
                last_updated_col = max(col_indices)
                end_part = " & ".join(columns[last_updated_col + 1 :]).strip()

                # Reconstruct the line, preserving formatting
                updated_parts = columns[: last_updated_col + 1]
                if end_part:
                    updated_parts.append(end_part)
                table_lines[line_number] = " & ".join(updated_parts)

                # Ensure the line ends with \\ and a newline
                if not table_lines[line_number].strip().endswith("\\\\"):
                    table_lines[line_number] = (
                        table_lines[line_number] + " \\\\\n"
                    )
                elif not table_lines[line_number].endswith("\n"):
                    table_lines[line_number] += "\n"

        except IndexError:
            raise IndexError(
                f"Invalid data structure at row {line_number}, column {j}"
            )

        # Add the last row showing the total count
        last_row = table_lines[27]
        last_row_parts = last_row.split("&")
        if config.batch == "old_reports":
            last_row_parts[col_indices[0]] = (
                f"\\color{{gray}} \\textbf{{{total}}} "
            )
        else:
            last_row_parts[col_indices[0]] = f" \\textbf{{{total}}} "
        table_lines[27] = "&".join(last_row_parts)

        # Write the updated table back to the file
        with open(filepath, "w") as file:
            file.writelines(table_lines)

    print(f"Updated latex table at {filepath}")


def select_reports_path_host(
    version_interval: bool, llm_support: bool, batch: str
):
    """Select where to store generated reports, or where to find reports for
    analysis."""
    if version_interval and batch == "old_code":
        return f"{config.reports_directory}mvi_old_code/"
    if version_interval and batch == "old_reports":
        return f"{config.reports_directory}mvi_old_reports/"
    if version_interval and not llm_support:
        return f"{config.reports_directory}mvi_without_llm/"
    if version_interval and llm_support:
        return f"{config.reports_directory}mvi_with_llm/"

    if not version_interval and batch == "old_code":
        return f"{config.reports_directory}nvi_old_code/"
    if not version_interval and not llm_support:
        return f"{config.reports_directory}nvi_without_llm/"
    if not version_interval and llm_support:
        return f"{config.reports_directory}nvi_with_llm/"


INPUT_DATA_PATH = config.input_data_path
# Select the folder depending whether LLMs are used or not
PROSPECTOR_REPORTS_PATH_HOST = select_reports_path_host(
    config.version_interval, config.llm_support, config.batch
)
BATCH = config.batch
PROSPECTOR_REPORTS_PATH_CONTAINER = "/app/evaluation/data/reports/"
ANALYSIS_RESULTS_PATH = "evaluation/data/results/"
# Comparison dirs
COMPARISON_DIRECTORY = config.compare_directory
