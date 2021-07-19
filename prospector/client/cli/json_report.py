import log.util
from datamodel.advisory import AdvisoryRecord
from datamodel.commit_features import CommitWithFeatures

_logger = log.util.init_local_logger()


def report_as_json(
    results: "list[CommitWithFeatures]", advisory_record: AdvisoryRecord
):
    filename = "prospector-report.json"
    _logger.info("Writing results to " + filename)
    _logger.warning("UNIMPLEMENTED!")
    assert False
