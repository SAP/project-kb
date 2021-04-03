from .git import Git


def test_get_commits_in_time_interval():
    repo = Git("https://github.com/apache/struts")
    repo.clone()

    results = repo.get_commits(since="1615441712", until="1617441712",)

    print("Found %d commits" % len(results))
    assert len(results) == 20
