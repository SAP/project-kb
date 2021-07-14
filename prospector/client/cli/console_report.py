from datamodel.commit_features import CommitWithFeatures


def report_on_console(results: "list[CommitWithFeatures]", verbose=False):
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
            "\n----------\n{}/commit/{}\n".format(
                commit.commit.repository, commit.commit.commit_id
            )
        )
        print(commit.commit.changed_files)
        print(commit.commit.message + "\n")
        print(format_annotations(commit))

    print("-----")
    print("Found {} candidates".format(count))
