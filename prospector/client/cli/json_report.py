import json

import log.util
from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit

_logger = log.util.init_local_logger()


def report_as_json(
    results: "list[Commit]",
    advisory_record: AdvisoryRecord,
    filename: str = "prospector-report.json",
):

    data = {
        "advisory_record": advisory_record.dict(),
        "commits": [r.dict() for r in results],
    }
    _logger.info("Writing results to " + filename)
    with open(filename, "w", encoding="utf8") as json_file:
        json.dump(data, json_file, ensure_ascii=True, indent=4)
    return filename
