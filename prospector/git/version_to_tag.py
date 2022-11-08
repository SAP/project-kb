# LEGACY CODE
#
# The following functions implement the heuristic to map a string version
# such as "2.3.35" onto a tag such as "STRUTS_2_3_35"

# flake8: noqa

import difflib

# pylint: disable=singleton-comparison,unidiomatic-typecheck, dangerous-default-value
import re


def recursively_split_version_string(input_version: str, output_version: list = []):
    """
    Splits a version/tag string into a list with integers and strings
        i.e. "8.0.0.RC10" --> [8, '.', 0, '.', 0, '.RC', 10]
    Input:
        input_version (str): a version or tag i.e. "8.0.0.RC10"
        output_version (list): an empty list, which will be filled iteratively
    Returns:
        list: the version/tag string in a list with integers and strings i.e. [8, '.', 0, '.', 0, '.RC', 10]
    """
    if type(input_version) != str:
        raise TypeError(
            "The provided version should be a str data type but is of type {}.".format(
                type(input_version)
            )
        )

    # when the part to split is only digits or no digits at all, the process is finished
    if (
        input_version.isdigit()
        or any(char.isdigit() for char in input_version) == False
    ):
        version = output_version + [input_version]
        return [int(segment) if segment.isdigit() else segment for segment in version]

    # otherwise check until what position it is a digit (since we want to keep i.e. a multiple digits number as one integer)
    pos = 0
    while (
        input_version[pos].isdigit() == input_version[pos + 1].isdigit()
        and pos != len(input_version) - 2
    ):  #
        pos += 1

    return recursively_split_version_string(
        input_version[pos + 1 :], output_version + [input_version[: pos + 1]]
    )


def get_tag_for_version(tags, version):
    """
    Map a version onto an existing tag
    Input:
        tags (list): a list of tags to map version onto
        version (str): the version
    Returns:
        list: list with tags that could be the version
        @TODO: only return the most relevant tag i.e. for key 8 version 4.1 returns ['version-3.4.1', 'version-4.1', 'version-4.4.1']
    """
    if isinstance(tags, tuple):
        tags = list(tags)
    if type(tags) != list or len(tags) == 0:
        raise ValueError(
            "tags should be a list of tags to map the version onto, is a {} of length {}".format(
                type(tags), len(tags)
            )
        )

    # stripped_tags = [tag[len(tag)-len(version):] for tag in tags]
    stripped_tags = [
        tag[
            tag.index(
                [
                    str(value)
                    for value in recursively_split_version_string(tag)
                    if type(value) == int
                ][0]
            ) :
        ]
        if any(char.isdigit() for char in tag)
        else tag
        for tag in tags
    ]
    stripped_version = (
        version[
            version.index(
                [
                    str(value)
                    for value in recursively_split_version_string(version)
                    if type(value) == int
                ][0]
            ) :
        ]
        if any(char.isdigit() for char in version)
        else version
    )

    if version in tags and tags.count(version) == 1:
        tag = version
    elif version in stripped_tags and stripped_tags.count(version) == 1:
        tag = tags[stripped_tags.index(version)]
    elif version in stripped_tags and stripped_tags.count(version) > 1:
        return [
            tags[index] for index, tag in enumerate(stripped_tags) if tag == version
        ]
    elif (
        stripped_version in stripped_tags and stripped_tags.count(stripped_version) == 1
    ):
        tag = tags[stripped_tags.index(stripped_version)]
    elif (
        stripped_version in stripped_tags and stripped_tags.count(stripped_version) > 1
    ):
        return [
            tags[index]
            for index, tag in enumerate(stripped_tags)
            if tag == stripped_version
        ]

    else:
        version = re.sub("[^0-9]", "", version)
        best_match = ("", 0.0)
        for tag in tags:
            t_strip = re.sub("[^0-9]", "", tag)
            match_score = difflib.SequenceMatcher(None, t_strip, version).ratio()
            if match_score > best_match[1]:
                best_match = (tag, match_score)
        tag = best_match[0]
    return [tag]


# def get_timestamp_for_tag(tag, git_repo):
#     """
#     Retreive the timestamp the tag was created.
#     Input:
#         repo_url (str): the repository where the tag can be found
#         tag (str): the tag
#     Return:
#         int: timestamp (use datetime.fromtimestamp(timestamp) for datetime)
#     """
#     if type(git_repo) != Git:
#         raise TypeError(
#             "git-repo should be of type git_explorer.core.Git, not {}".format(
#                 type(git_repo)
#             )
#         )
#     if type(tag) != str:
#         raise TypeError("tag must be str, not {}".format(type(tag)))
#     if tag not in git_repo.get_tags():
#         raise ValueError("tag {} not found in git_repo".format(tag))

#     commit_id = git_repo.get_commit_id_for_tag(tag)
#     commit = Commit(git_repo, commit_id)
#     return commit.get_timestamp()


# def find_next_tag(tag, tags, tag_timestamp, git_repo, digit_indices=None, loop=-1):
#     """
#     Tries to find the next tag by means of incrementing digits in the tag
#     Input:
#         tag (str): the tag
#         tags (list): all tags
#         (digit_indices should not be provided, is used for the recursion)
#         (loop does not have to be provided, is used for the recursion)
#     Returns:
#         str: the next tag
#     """
#     if type(tags) != list or len(tags) == 0:
#         raise ValueError(
#             "tags should be a list of tags to map the version onto, is a {} of length {}".format(
#                 type(tags), len(tags)
#             )
#         )
#     if type(git_repo) != Git:
#         raise TypeError(
#             "git-repo should be of type git_explorer.core.Git, not {}".format(
#                 type(git_repo)
#             )
#         )

#     # splits the tag into a list of integers and strings
#     splitted_tag = recursively_split_version_string(tag, [])

#     # determines which indices in the list correspond to digits of the version number
#     if digit_indices == None:
#         if tag_timestamp == None:
#             tag_timestamp = get_timestamp_for_tag(tag, git_repo)
#         digit_indices = list(
#             reversed(
#                 [index for index, val in enumerate(splitted_tag) if type(val) == int]
#             )
#         )
#         loop = 0

#     # searching for valid tags: recursively to evaluate different
#     tried_indices = []
#     for index in digit_indices:

#         # as we're looking for the next tag, it is unlikely that there will be a gap of more than 10
#         for i in range(10):
#             splitted_tag[index] += 1

#             possible_tag = "".join([str(x) for x in splitted_tag])

#             if possible_tag in tags:
#                 possible_tag_timestamp = get_timestamp_for_tag(possible_tag, git_repo)
#                 if tag_timestamp < possible_tag_timestamp:
#                     return possible_tag

#             if len(tried_indices) != 0:
#                 result = find_next_tag(
#                     possible_tag, tags, tag_timestamp, git_repo, tried_indices, loop + 1
#                 )
#                 if result:
#                     return result

#         # when i.e. current tag is 4.5.0 the next tag to evaluate is 4.4.9
#         splitted_tag[index] = 0
#         tried_indices.append(index)

#     # when every combination is tried, chop off the last part of the tag
#     if loop == 0 and len(tag) > 1:
#         shortened_tag = "".join(
#             [str(x) for x in recursively_split_version_string(tag, [])[:-1]]
#         )
#         return find_next_tag(shortened_tag, tags, tag_timestamp, git_repo)

#     # None is returned when there is no match
#     return


# def find_previous_tag(tag, tags, tag_timestamp, git_repo, digit_indices=None, loop=-1):
#     """
#     Tries to find the previous tag by means of decrementing digits in the tag,
#         and checking whether the new tag exists. It starts at the last digit and works it way back.
#         When all digits have become 0, the last element of tag is removed and the process is tried again.
#     Input:
#         tag (str): the tag
#         tags (list): all tags
#         (digit_indices should not be provided, is used for the recursion)
#     Returns:
#         str: the previous tag
#     """
#     if type(tags) != list or len(tags) == 0:
#         raise ValueError(
#             "tags should be a list of tags to map the version onto, is a {} of length {}".format(
#                 type(tags), len(tags)
#             )
#         )
#     if type(git_repo) != Git:
#         raise TypeError(
#             "git-repo should be of type git_explorer.core.Git, not {}".format(
#                 type(git_repo)
#             )
#         )

#     # splits the tag into a list of integers and strings
#     splitted_tag = recursively_split_version_string(tag, [])

#     # determines which indices in the list correspond to digits of the version number
#     if digit_indices == None:
#         if tag_timestamp == None:
#             tag_timestamp = get_timestamp_for_tag(tag, git_repo)
#         loop = 0
#         digit_indices = list(
#             reversed(
#                 [index for index, val in enumerate(splitted_tag) if type(val) == int]
#             )
#         )

#     # searching for valid tags: recursively to evaluate different
#     tried_indices = []
#     for index in digit_indices:

#         i = 0
#         # sometimes a date is used (thus takes a long time)
#         if splitted_tag[index] < 100:
#             while splitted_tag[index] > 0:
#                 i += 1
#                 splitted_tag[index] -= 1

#                 possible_tag = "".join([str(x) for x in splitted_tag])

#                 if possible_tag in tags:
#                     possible_tag_timestamp = get_timestamp_for_tag(
#                         possible_tag, git_repo
#                     )
#                     if tag_timestamp > possible_tag_timestamp:
#                         return possible_tag

#                 if len(tried_indices) != 0:
#                     result = find_previous_tag(
#                         possible_tag,
#                         tags,
#                         tag_timestamp,
#                         git_repo,
#                         tried_indices,
#                         loop + 1,
#                     )
#                     if result:
#                         return result

#         # when i.e. current tag is 4.5.0 the next tag to evaluate is 4.4.99
#         splitted_tag[index] = 99
#         tried_indices.append(index)

#     # when every combination is tried, chop off the last part of the tag
#     if loop == 0 and len(tag) > 1:
#         shortened_tag = "".join(
#             [str(x) for x in recursively_split_version_string(tag, [])[:-1]]
#         )
#         # print(shortened_tag)
#         return find_previous_tag(shortened_tag, tags, tag_timestamp, git_repo)
#     return


# def version_to_wide_interval_tags(version, git_repo, tag_margin=1):
#     """
#     A version is mapped onto a tag, and a tuple of a wide version interval is returned
#         [0] corresponds to the previous tag
#         [1] corresponds to the next tag
#     Input:
#         tags (list): a list of tags to map version onto
#         version (str): the version
#         git_repo (git_explorer.GIT):
#         tag_margin (int): how wide the interval can be
#     Returns:
#         # tuple: previous tag, next tag
#         list: for every tag, returns a tuple with previous tag, current next tag
#         @TODO: return only one tuple: previous tag, next tag
#     """
#     result = list()
#     tags = git_repo.get_tags()
#     # can return multiple tags now, as matching is not perfect
#     for tag in get_tag_for_version(tags, version):

#         tag_timestamp = get_timestamp_for_tag(tag, git_repo)

#         previous_tag = find_previous_tag(tag, tags, tag_timestamp, git_repo)
#         if previous_tag == None:
#             if tags.index(tag) != 0:
#                 previous_tag = tags[tags.index(tag) - 1]
#             else:
#                 previous_tag = tags[tags.index(tag)]

#         for i in range(tag_margin - 1):
#             # when no valid new version has been found but the current version is in the tags
#             possible_previous_tag = find_previous_tag(
#                 previous_tag, tags, tag_timestamp, git_repo
#             )
#             if possible_previous_tag == None:
#                 break
#             else:
#                 previous_tag = possible_previous_tag

#         next_tag = find_next_tag(tag, tags, tag_timestamp, git_repo)
#         if next_tag == None:
#             if tags.index(tag) != len(tags) - 1:
#                 next_tag = tags[tags.index(tag) + 1]
#             else:
#                 next_tag = tags[tags.index(tag)]

#         for i in range(tag_margin - 1):
#             possible_next_tag = find_next_tag(next_tag, tags, tag_timestamp, git_repo)
#             if possible_next_tag == None:
#                 break
#             else:
#                 next_tag = possible_next_tag

#         if (previous_tag, tag) not in result:
#             result.append((previous_tag, tag))
#         if (tag, next_tag) not in result:
#             result.append((tag, next_tag))
#     return result
