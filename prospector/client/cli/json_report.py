from datamodel.advisory import AdvisoryRecord
from datamodel.commit_features import CommitWithFeatures


def report_as_json(
    results: "list[CommitWithFeatures]", advisory_record: AdvisoryRecord
):
    filename = "prospector-report.json"
    print("Writing results to " + filename)
    print("WARNING: UNIMPLEMENTED!")
