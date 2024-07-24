from evaluation.utils import load_dataset
from git.git import clone_repo_multiple


# Get the URLs from d63.csv -> set
urls = set()
dataset = load_dataset(
    "/home/i748376/prospector/project-kb/prospector/evaluation/data/input/d63.csv"
)

for cve_record in dataset:
    urls.add(cve_record[1])

urls = list(urls)[:10]

print(f"Retrieved {len(urls)} distinct repositories from the dataset.")

# Call clone_repo_multiple() on this set
results = clone_repo_multiple(
    urls,
    output_folder="/home/i748376/data/gitcache",
    skip_existing=False,
    shallow=False,
)

print("Cloning completed. Results: ", results)
