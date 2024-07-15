import json
import logging
import os
from pathlib import Path
from typing import List

import jinja2

from cli.console import ConsoleWriter, MessageStatus
from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from log.logger import get_level, logger
from stats.execution import execution_statistics


# Handles Set setialization
class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def json_(
    results: List[Commit],
    advisory_record: AdvisoryRecord,
    params,
    filename: str = "prospector-report.json",
    no_diff: bool = False,
):
    fn = filename if filename.endswith(".json") else f"{filename}.json"

    params["enabled_rules"] = list(
        params["enabled_rules"]
    )  # Fix for OmegaConf not being JSON serializable
    data = {
        "parameters": params,
        "advisory_record": advisory_record.__dict__,
        "commits": [r.as_dict(no_hash=True, no_rules=False) for r in results],
        "processing_statistics": execution_statistics,
    }
    logger.info(f"Writing results to {fn}")
    file = Path(fn)
    file.parent.mkdir(parents=True, exist_ok=True)
    with open(fn, "w", encoding="utf8") as json_file:
        json.dump(data, json_file, ensure_ascii=True, indent=4, cls=SetEncoder)
    return fn


def html_(
    results: List[Commit],
    advisory_record: AdvisoryRecord,
    filename: str = "prospector-report.html",
    statistics=None,
):
    fn = filename if filename.endswith(".html") else f"{filename}.html"

    annotations_count = {}

    for commit in results:
        for rule in commit.matched_rules:
            id = rule.get("id")
            annotations_count[id] = annotations_count.get(id, 0) + 1

    logger.info(f"Writing results to {fn}")
    environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join("core", "templates")),
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


def console_(
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


def generate_report(
    results,
    advisory_record,
    report_type,
    report_filename,
    prospector_params,
    report_diff=False,
):
    with ConsoleWriter("Generating report\n") as console:
        match report_type:
            case "console":
                console_(results, advisory_record, get_level() < logging.INFO)
            case "json":
                json_(
                    results,
                    advisory_record,
                    prospector_params,
                    report_filename,
                    report_diff,
                )
            case "html":
                html_(results, advisory_record, report_filename)
            case "all":
                json_(
                    results,
                    advisory_record,
                    prospector_params,
                    report_filename,
                    report_diff,
                )
                html_(results, advisory_record, report_filename)
            case _:
                logger.warning("Invalid report type specified, using 'console'")
                console.set_status(MessageStatus.WARNING)
                console.print(
                    f"{report_type} is not a valid report type, 'console' will be used instead",
                )
                console_(results, advisory_record, get_level() < logging.INFO)

        logger.info("\n" + execution_statistics.generate_console_tree())
        console.print(f"Report saved in {report_filename}")
