import os
from typing import List

import jinja2

import log.util
from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from simple_hierarchical_storage.execution import execution_statistics

_logger = log.util.init_local_logger()


def report_as_html(
    results: List[Commit],
    advisory_record: AdvisoryRecord,
    filename: str = "prospector-report.html",
    statistics=None,
):
    annotations_count = {}
    annotated_commit: Commit
    for annotated_commit in results:
        for annotation in annotated_commit.annotations.keys():
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
            execution_statistics=(
                execution_statistics if statistics is None else statistics
            ).as_html_ul(),
        ):
            html_file.write(content)
    return filename
