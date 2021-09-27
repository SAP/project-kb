import log.util
from datamodel.advisory import AdvisoryRecord
from datamodel.commit_features import CommitWithFeatures

_logger = log.util.init_local_logger()


def report_on_console(
    results: "list[CommitWithFeatures]", advisory_record: AdvisoryRecord, verbose=False
):
    def format_annotations(commit: CommitWithFeatures) -> str:
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
            f"\n----------\n{commit.commit.repository}/commit/{commit.commit.commit_id}\n"
            + "\n".join(commit.commit.changed_files)
            + f"{commit.commit.message}\n{format_annotations(commit)}"
        )

    print(f"Found {count} candidates\nAdvisory record\n{advisory_record}")
