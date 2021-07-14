from datamodel.commit_features import CommitWithFeatures


def report_as_json(results: "list[CommitWithFeatures]"):
    filename = "prospector-report.json"
    print("Writing results to " + filename)
