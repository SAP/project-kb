import csv


def load_dataset(path: str):
    with open(path, "r") as file:
        reader = csv.reader(file, delimiter=";")
        return [row for row in reader if "CVE" in row[0] and row[3] != "True"]
