import re

from evaluation.utils import (
    INPUT_DATA_PATH,
    ANALYSIS_RESULTS_PATH,
    load_dataset,
)


def extract_crash_lines(log_file_path, output_file_path):
    crash_pattern = re.compile(r".*prospector\(\) crashed at.*")

    with open(log_file_path, "r") as log_file, open(
        output_file_path, "a"
    ) as output_file:
        for line in log_file:
            if crash_pattern.match(line):
                output_file.write(line)


# Usage
log_file_path = f"evaluation.log"
output_file_path = f"{ANALYSIS_RESULTS_PATH}error_lines.log"

extract_crash_lines(log_file_path, output_file_path)
print(f"Error lines have been extracted to {output_file_path}")
