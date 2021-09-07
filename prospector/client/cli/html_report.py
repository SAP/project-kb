import os
from typing import List

import jinja2

import log.util
from datamodel.advisory import AdvisoryRecord
from datamodel.commit_features import CommitWithFeatures

_logger = log.util.init_local_logger()


def report_as_html(
    results: List[CommitWithFeatures],
    advisory_record: AdvisoryRecord,
    filename: str = "prospector-report.html",
):
    annotations_count = {}
    commit_with_feature: CommitWithFeatures
    for commit_with_feature in results:
        for annotation in commit_with_feature.annotations.keys():
            annotations_count[annotation] = annotations_count.get(annotation, 0) + 1

    _logger.info("Writing results to " + filename)
    environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join("client", "cli", "templates")),
        autoescape=jinja2.select_autoescape(),
    )
    template = environment.get_template("results.html")
    with open(filename, "w", encoding="utf8") as html_file:
        for content in template.generate(
            candidates=results,
            present_annotations=annotations_count,
            advisory_record=advisory_record,
        ):
            html_file.write(content)
    return filename
