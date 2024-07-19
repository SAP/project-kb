from typing import List


def save_to_json():
    pass


def save_to_csv():
    pass


def update_latex_table(mode: str, data: List[List[str, str]], file_path: str) -> None:
    """Updates the latex table at {ANALYSIS_RESULTS_PATH}/`file_path`. For this to work, the table latex code from D6.3 for tracer_dataset_results table must be saved in the file.

    Params:
        data (List(List(int, int))): The list of data, each item should be another list of two integers: the total and percentage.

    Saves:
        The newly updated latex table at `file_path`

    Disclaimer: Partly generated with Claude Opus 3.
    """
    # Read the existing LaTeX table from the file
    with open(file_path, 'r') as file:
        table_lines = file.readlines()

        # Find the line numbers to edit; CHANGE if table changes!
        lines_to_edit = [5, 8, 11, 14, 17, 18, 19, 20, 21, 22]

        # Update the corresponding columns based on the mode
        if mode == 'MVI':
            col_indices = [1, 2]
        elif mode == 'AVI':
            col_indices = [3, 4]
        elif mode == 'NVI':
            col_indices = [5, 6]
        else:
            raise ValueError('Invalid mode. Please choose from MVI, AVI, or NVI.')

        try:
            for i, line_number in enumerate(lines_to_edit):
                row_data = table_lines[line_number].split('&')
                for j, col_index in enumerate(col_indices):
                    row_data[col_index] = str(data[i][j])

                table_lines[line_number] = ' & '.join(row_data)
        except IndexError:
            raise IndexError(f"Invalid data structure at row {line_number}, column {j}")

        # Write the updated table back to the file
        with open(file_path, 'w') as file:
            file.writelines(table_lines)
