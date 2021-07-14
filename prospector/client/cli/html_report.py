import os
from typing import List

import jinja2

from datamodel.commit_features import CommitWithFeatures


def report_as_html(
    results: List[CommitWithFeatures], filename: str = "prospector-report.html"
):
    annotations = set()
    for commit_with_feature in results:
        annotations = annotations.union(commit_with_feature.annotations.keys())

    print("Writing results to " + filename)
    environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join("client", "cli", "templates")),
        autoescape=jinja2.select_autoescape(),
    )
    template = environment.get_template("results.html")
    with open(filename, "w", encoding="utf8") as html_file:
        for content in template.generate(
            candidates=results, present_annotations=annotations
        ):
            html_file.write(content)
    return filename
