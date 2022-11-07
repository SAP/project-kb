import json
import os
from pathlib import Path
from typing import List

import jinja2

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from log.logger import logger
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
    fn = filename if filename.endswith(".json") else f"{filename}.json"

    data = {
        "advisory_record": advisory_record.__dict__,
        "commits": [r.as_dict(no_hash=True, no_rules=False) for r in results],
    }
    logger.info(f"Writing results to {fn}")
    file = Path(fn)
    file.parent.mkdir(parents=True, exist_ok=True)
    with open(fn, "w", encoding="utf8") as json_file:
        json.dump(data, json_file, ensure_ascii=True, indent=4, cls=SetEncoder)
    return fn


def as_html(
    results: List[Commit],
    advisory_record: AdvisoryRecord,
    filename: str = "prospector-report.html",
    statistics=None,
):
    fn = filename if filename.endswith(".html") else f"{filename}.html"

    annotations_count = {}
    # annotation: Commit
    # Match number per rules
    for commit in results:
        for rule in commit.matched_rules:
            id = rule.get("id")
            annotations_count[id] = annotations_count.get(id, 0) + 1
        # for annotation in commit.annotations.keys():
        #     annotations_count[annotation] = annotations_count.get(annotation, 0) + 1

    logger.info(f"Writing results to {fn}")
    environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join("client", "cli", "templates")),
        autoescape=jinja2.select_autoescape(),
    )
    template = environment.get_template("results.html")
    file = Path(fn)
    file.parent.mkdir(parents=True, exist_ok=True)
    with open(fn, "w", encoding="utf8") as html_file:
        for content in template.generate(
            candidates=results,
            present_annotations=annotations_count,
            advisory_record=advisory_record,
            execution_statistics=(
                execution_statistics if statistics is None else statistics
            ).as_html_ul(),
        ):
            html_file.write(content)
    return fn


def report_on_console(
    results: List[Commit], advisory_record: AdvisoryRecord, verbose=False
):
    def format_annotations(commit: Commit) -> str:
        out = ""
        if verbose:
            for tag in commit.annotations:
                out += " - [{}] {}".format(tag, commit.annotations[tag])
        else:
            out = ",".join(commit.annotations.keys())

        return out

    print("-" * 80)
    print("Rule filtered results")
    print("-" * 80)
    count = 0
    for commit in results:
        count += 1
        print(
            f"\n----------\n{commit.repository}/commit/{commit.commit_id}\n"
            + "\n".join(commit.changed_files)
            + f"{commit.message}\n{format_annotations(commit)}"
        )

    print(f"Found {count} candidates\nAdvisory record\n{advisory_record}")
