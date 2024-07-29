from evaluation.utils import load_dataset
from git.git import clone_repo_multiple


# Get the URLs from d63.csv -> set
urls = set()
dataset = load_dataset(
    "/home/i748376/prospector/project-kb/prospector/evaluation/data/input/d63.csv"
)

for cve_record in dataset:
    urls.add(cve_record[1])

# urls = list(urls)
# urls = [
#     "https://github.com/Turistforeningen/node-im-resize",  # CVE-2019-10787
#     "https://github.com/remy/undefsafe",  # CVE-2019-10795
#     "https://github.com/Froxlor/Froxlor",  # CVE-2020-10236
#     "https://github.com/jnunemaker/crack",
#     "https://github.com/django-tastypie/django-tastypie",
#     "https://github.com/pyinstaller/pyinstaller",
#     "https://github.com/rails/rails-html-sanitizer",
#     "https://github.com/scipy/scipy",
#     "https://github.com/parcel-bundler/parcel",
#     "https://github.com/javamelody/javamelody",
# ]

print(f"Retrieved {len(urls)} distinct repositories from the dataset.")

# Call clone_repo_multiple() on this set
results = clone_repo_multiple(
    urls,
    output_folder="/home/i748376/data/gitcache",
    skip_existing=False,
    shallow=False,
    concurrent=1,
)

print("Cloning completed. Results: ", results)
