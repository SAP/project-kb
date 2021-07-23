import json

import log.util
from datamodel.advisory import AdvisoryRecord
from datamodel.commit_features import CommitWithFeatures

_logger = log.util.init_local_logger()


def report_as_json(
    results: "list[CommitWithFeatures]", advisory_record: AdvisoryRecord
):

    data = {
        "advisory_record": advisory_record.dict(),
        "commits": [r.dict() for r in results],
    }
    filename = "prospector-report.json"
    _logger.info("Writing results to " + filename)
    with open(filename, "w", encoding="utf8") as json_file:
        json.dump(data, json_file, ensure_ascii=True, indent=4)
    return filename
