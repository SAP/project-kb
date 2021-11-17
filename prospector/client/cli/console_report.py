from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit


def report_on_console(
    results: "list[Commit]", advisory_record: AdvisoryRecord, verbose=False
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
