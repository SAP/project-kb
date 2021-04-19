#!/usr/bin/env python3

# flake8: noqa

import subprocess
import sys

# from pprint import pprint

project_slug = "sap/project-kb"

commit_types = {
    "new": "New features",
    "feat": "New features",
    "feature": "New features",
    "fix": "Bugfixes",
    "change": "Changes",
    "refactor": "Changes",
    "refactoring": "Changes",
    "chore": "Misc",
    "misc": "Misc",
    "docs": "Docs",
}


def exec(cmdline):
    return (
        subprocess.run(cmdline.split(), stdout=subprocess.PIPE)
        .stdout.decode("utf-8")
        .splitlines()
    )


def get_commit_for_last_tag():
    return exec("git rev-list --tags --skip=0 --max-count=1")[0]


def get_commit_for_second_last_tag():
    return exec("git rev-list --tags --max-count=1 --skip=1 --no-walk")[0]


def tag_at_commit(c):
    return exec("git describe --tags " + c)[0]


def parse_commit_msg(msg):
    split_msg = msg.split()
    id = split_msg[0]

    commit_type = split_msg[1].split(":")[0]
    if commit_type not in commit_types:
        # print("ignoring commit " + msg)
        return None
    else:
        msg = " ".join(split_msg[2:])

    return {"id": id, "type": commit_type, "msg": msg}


def get_commits():
    results = []

    since = get_commit_for_second_last_tag()
    until = get_commit_for_last_tag()

    # print(since, until)

    commits = exec("git log " + since + ".." + until + " --oneline")
    for c in commits:
        commit_obj = parse_commit_msg(c)
        if commit_obj:
            results.append(commit_obj)
    return results


def render_changelog_header():
    since = get_commit_for_second_last_tag()
    until = get_commit_for_last_tag()

    prev_tag = tag_at_commit(since)
    curr_tag = tag_at_commit(until)

    print('<a name="' + curr_tag + '"></a>')
    print(
        "## ["
        + curr_tag
        + "](https://github.com/"
        + project_slug
        + "/compare/"
        + prev_tag
        + "..."
        + curr_tag
        + ")"
    )


def render_link_to_detailed_changes():
    since = get_commit_for_second_last_tag()
    until = get_commit_for_last_tag()

    prev_tag = tag_at_commit(since)
    curr_tag = tag_at_commit(until)

    print(
        "\n\n:mag: [View detailed changes since the previous release]"
        + "(https://github.com/"
        + project_slug
        + "/compare/"
        + prev_tag
        + "..."
        + curr_tag
        + ")"
    )


def render_changelog(log):
    changes_by_type = dict()

    for entry in log:
        if commit_types[entry["type"]] in changes_by_type:
            changes_by_type[commit_types[entry["type"]]].append(entry)
        else:
            changes_by_type[commit_types[entry["type"]]] = [entry]

    for t in changes_by_type:
        print("\n### " + t)
        for c in changes_by_type[t]:
            print(
                " * "
                + c["msg"]
                + " (["
                + c["id"]
                + "](https://github.com/"
                + project_slug
                + "/commit/"
                + c["id"]
                + "))"
            )


def main(args):
    if len(args) > 1:
        since = args[1]
        log = get_commits(since)
    else:
        log = get_commits()

    #   render_changelog_header()
    render_changelog(log)
    render_link_to_detailed_changes()


if __name__ == "__main__":
    main(sys.argv)
