import csv
import re

from omegaconf import OmegaConf
from datamodel.advisory import build_advisory_record
from urllib.parse import urlparse
from log.logger import create_logger

evaluation_config = OmegaConf.load("evaluation/config.yaml")

logger = create_logger("evaluation.log")
logger.setLevel(evaluation_config.debug_level)

INPUT_DATA_PATH = evaluation_config.input_data_path
# Select the folder depending whether LLMs are used or not
PROSPECTOR_REPORT_PATH = (
    evaluation_config.prospector_reports_llm_path
    if evaluation_config.prospector_settings.run_with_llm
    else evaluation_config.prospector_reports_no_llm_path
)
ANALYSIS_RESULTS_PATH = evaluation_config.analysis_results_path

VULN = ["version", "through", "versions"]

FIXED = [
    "before",
    "before release",
    "before version",
    "prior to",
    "upgrade to",
    "fixed in",
    "fixed in version",
    "fixed in release",
    "to version",
]


def load_dataset(path: str):
    with open(path, "r") as file:
        reader = csv.reader(file, delimiter=";")
        logger.debug(f"Loaded Dataset at {path}")
        print(f"Loaded Dataset at {path}")
        return [row for row in reader if "CVE" in row[0] and row[3] != "True"]


def is_real_version(text: str):
    return bool(re.match(r"\d+\.(?:\d+\.*)*\d", text))


def get_version_spacy(text: str, nlp):
    """This function extracts vulnerable and fixed version numbers from a given text using spaCy."""
    doc = nlp(text)
    # relevant_sentences = {}
    # relevant_sentence = ""
    fixed_version = ""
    vulnerable_version = ""
    for i in range(len(doc))[1:]:
        if is_real_version(doc[i].text):
            if doc[i - 1].text in FIXED:
                # relevant_sentence = doc[: i + 1]
                fixed_version = doc[i].text
            elif (doc[i - 2].text + " " + doc[i - 1].text) in FIXED:
                # relevant_sentence = doc[: i + 1]
                fixed_version = doc[i].text
            elif (
                doc[i - 3].text + " " + doc[i - 2].text + " " + doc[i - 1].text
            ) in FIXED:
                # relevant_sentence = doc[: i + 1]
                fixed_version = doc[i].text
            else:
                # relevant_sentence = doc[: i + 1]
                vulnerable_version = doc[i].text
    return vulnerable_version, fixed_version


def check_advisory(cve, repository=None, nlp=None):
    """This function checks the advisory for a given CVE and attempts to extract version information."""
    advisory = build_advisory_record(
        cve, nvd_rest_endpoint="http://localhost:8000/nvd/vulnerabilities/"
    )
    references = [urlparse(r).netloc for r in advisory.references]
    return references
    vuln = "None"
    if len(advisory.versions.get("affected")):
        vuln = advisory.versions.get("affected")[-1]

    fixed = "None"
    if len(advisory.versions.get("fixed")):
        fixed = advisory.versions.get("fixed")[-1]

    vuln2, fixed2 = get_version_spacy(advisory.description, nlp)
    res = [advisory.cve_id, advisory.description]
    if fixed == fixed2 and vuln == vuln2:
        res.append(f"{vuln}:{fixed}")
    if fixed == "None" and fixed2 != "":
        res.append(f"{vuln}:{fixed2}")
    if vuln == "None" and vuln2 != "":
        res.append(f"{vuln2}:{fixed}")
    if fixed != fixed2 and fixed2 != "" and fixed != "None":
        res.append(f"{vuln}:{fixed}")
        res.append(f"{vuln}:{fixed2}")

    if len(res) > 2:
        res.append("***************************************")
        print(advisory.cve_id)
        return res
    else:
        res.append(f"{vuln}:{fixed}")
        res.append("***************************************")
        print(advisory.cve_id)
        return res


def update_summary_execution_table(
    mode: str, data, data_total: str, filepath: str
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
        last_row_data[col_indices[0]] = f"\\textbf{data_total}"
        table_lines[23] = " & ".join(last_row_data)

        # Write the updated table back to the file
        with open(filepath, "w") as file:
            file.writelines(table_lines)

    print(f"Updated latex table at {filepath}")


def update_false_positives(itm):
    with open(f"{ANALYSIS_RESULTS_PATH}false_postive.txt", "a") as file:
        writer = csv.writer(file)
        writer.writerow(
            [f"{itm[0]};{itm[1]};{itm[2]};{itm[3]};{itm[4]};{itm[5]}"]
        )
