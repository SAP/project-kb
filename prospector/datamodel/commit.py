from collections import namedtuple

BaseCommit = namedtuple("BaseCommit", ["id", "repository", "feature_1", "feature_2"])


class Commit(BaseCommit):
    pass
