import json
import os
import jinja2
from typing import List
from log.logger import logger
from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit

from stats.execution import execution_statistics

# Handles Set setialization
class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def as_json(
    results: List[Commit],
    advisory_record: AdvisoryRecord,
    filename: str = "prospector-report.json",
):
    data = {
        "advisory_record": advisory_record.dict(),
        "commits": [r.dict() for r in results],
    }
    logger.info("Writing results to " + filename)
    with open(filename, "w", encoding="utf8") as json_file:
        json.dump(data, json_file, ensure_ascii=True, indent=4, cls=SetEncoder)
    return filename


def as_html(
    results: List[Commit],
    advisory_record: AdvisoryRecord,
    filename: str = "prospector-report.html",
    statistics=None,
):
    annotations_count = {}
    # annotation: Commit
    # Match number per rules
    for commit in results:
        for rule in commit.matched_rules:
            id = rule.get("id")
            annotations_count[id] = annotations_count.get(id, 0) + 1
        # for annotation in commit.annotations.keys():
        #     annotations_count[annotation] = annotations_count.get(annotation, 0) + 1

    logger.info("Writing results to " + filename)
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
