import difflib
import re
import sys
from typing import List, Optional

from log.logger import logger


def clean_tag(tag: str, digits_only: bool = True) -> str:
    """Clean a tag name returning only the numeric part separated by dots."""
    if digits_only:
        return ".".join(re.findall(r"\d+", tag))
    else:
        return re.sub(r"[^0-9a-zA-Z]+", ".", tag, flags=re.IGNORECASE)
    re.sub(r"^[^0-9]+|[^0-9]+$", "", tag, flags=re.IGNORECASE)


def is_rc_or_date(tag: str) -> bool:
    return bool(re.search(r"[^a-z]?rc[^a-z]|\d{9,}", tag, flags=re.IGNORECASE))


def get_possible_missing_tag(
    tags: list[str],
    prev_tag: Optional[str] = None,
    next_tag: Optional[str] = None,
):
    """Given the tag list and a tag, return either the previous or the next tag candidates."""
    if next_tag is None:
        return [
            tag
            for tag in tags[tags.index(prev_tag) + 1 :]
            if difflib.SequenceMatcher(None, tag, prev_tag).ratio() > 0.8
        ][:3]

    if prev_tag is None:
        return [
            tag
            for tag in tags[: tags.index(next_tag)][::-1]
            if difflib.SequenceMatcher(None, tag, next_tag).ratio() > 0.8
        ][:3]


def handle_tag_or_substring(version: str, tags: list[str]) -> List[str]:
    """Given a tag and a list of tags, return True if the tag is in the list or is a substring of one of the tags."""
    if version in tags:
        return [version]
    elif (
        len(
            [
                t
                for t in tags
                if t.endswith(version)
                or (
                    version in t
                    and ends_with_zero(t)
                    or (t in version and ends_with_zero(version))
                )
            ]
        )
        == 1
    ):
        return [
            t
            for t in tags
            if t.endswith(version)
            or (version in t and ends_with_zero(t))
            or (t in version and ends_with_zero(version))
        ]
    else:
        return []


def ends_with_zero(version: str):
    """Given a version string, return True if the last digit is zero."""
    return bool(re.search(r"[\.-_]0$", version))


# flake8: noqa: C901
def get_possible_tags(
    tags: list[str], versions: str, unsupervised: bool = True
):
    """Given a list of tags and a version interval, return the possible tag interval that matches."""
    prev_version, next_version = versions.replace("None", "").split(":")
    prev_tag = handle_tag_or_substring(prev_version, tags)
    # print(f"prev_tag: {prev_tag}, prev_version: {prev_version}")
    if len(prev_tag) == 0 and len(prev_version) > 0:
        prev_tag = [
            tag
            for tag in tags
            if prev_version == clean_tag(tag) and not is_rc_or_date(tag)
        ]
    next_tag = handle_tag_or_substring(next_version, tags)
    # print(f"next_tag: {next_tag}, next_version: {next_version}")
    if len(next_tag) == 0 and len(next_version) > 0:
        next_tag = [
            tag
            for tag in tags
            if next_version == clean_tag(tag) and not is_rc_or_date(tag)
        ]

    if len(prev_tag) == 1 and len(next_tag) == 1:
        return prev_tag[0], next_tag[0]
    elif len(prev_tag) == 1 and len(next_tag) > 1:
        next_tag = [
            tag
            for tag in next_tag
            if tag != prev_tag[0] or tag not in prev_tag[0]
        ]  # this may lead to empty list
        logger.info(f"Possible tags are:{prev_tag}:{next_tag}")
        return (
            prev_tag[0],
            next_tag[
                0
            ],  # difflib.get_close_matches(prev_tag[0], next_tag, n=1)[0],
        )
    elif len(prev_tag) > 1 and len(next_tag) == 1:
        prev_tag = [
            tag
            for tag in prev_tag
            if tag != next_tag[0] or next_tag[0] not in tag
        ]
        logger.info(f"Possible tags are:{prev_tag}:{next_tag}")
        return (
            prev_tag[
                -1
            ],  # difflib.get_close_matches(next_tag[0], prev_tag, n=1)[0],
            next_tag[0],
        )
    # If there is one exact match but no candidates for the other tag, exit and hint the user with possible candidates
    elif len(prev_tag) == 0 and len(next_tag) == 1:
        prev_candidates = get_possible_missing_tag(tags, next_tag=next_tag[0])
        if len(prev_version) == 0 and len(prev_candidates) == 0:
            return "", next_tag[0]
        logger.info(f"Previous tag can be: {','.join(prev_candidates)}")
    elif len(prev_tag) == 1 and len(next_tag) == 0:
        next_candidates = get_possible_missing_tag(tags, prev_tag=prev_tag[0])
        if len(next_version) == 0 and len(next_candidates) == 0:
            return prev_tag[0], ""
        logger.info(f"Next tag can be: {','.join(next_candidates)}")
    elif len(prev_tag) > 1 and len(next_tag) > 1:
        logger.info("Multiple tag candidates found.")
    else:
        prev_tag = [
            tag for tag in tags if prev_version in clean_tag(tag, False)
        ]
        next_tag = [
            tag for tag in tags if next_version in clean_tag(tag, False)
        ]
        # print(f"Possible tags are:\n\t{prev_tag}\n\t{next_tag}")
        if len(prev_tag) == 1 and len(next_tag) == 1:
            return prev_tag[0], next_tag[0]
        elif len(prev_tag) == 1 and len(next_tag) == 0 and next_version == "":
            return prev_tag[0], None
        elif len(prev_tag) == 0 and len(next_tag) == 1 and prev_version == "":
            return None, next_tag[0]
        elif len(prev_tag) == 0 and len(next_tag) == 0:
            return None, None
        elif prev_version == "" and next_version == "":
            return None, None
    # return "","" to trigger tag mismatch
    return None, None


def get_tag_candidates(
    prev_version: str,
    next_version: str,
    tag_version_map: dict,
    find_prev: bool,
):
    candidates = (
        [
            tag_version_map[key]
            for key in difflib.get_close_matches(
                prev_version, tag_version_map.keys(), n=5
            )
            if key < next_version
        ]
        if find_prev
        else [
            tag_version_map[key]
            for key in difflib.get_close_matches(
                next_version, tag_version_map.keys(), n=5
            )
            if key > prev_version
        ]
    )
    return [tag for tags in candidates for tag in tags]


# def recursively_split_version_string(input_version: str, output_version: list = []):
#     """
#     Splits a version/tag string into a list with integers and strings
#         i.e. "8.0.0.RC10" --> [8, '.', 0, '.', 0, '.RC', 10]
#     Input:
#         input_version (str): a version or tag i.e. "8.0.0.RC10"
#         output_version (list): an empty list, which will be filled iteratively
#     Returns:
#         list: the version/tag string in a list with integers and strings i.e. [8, '.', 0, '.', 0, '.RC', 10]
#     """
#     if type(input_version) != str:
#         raise TypeError(
#             "The provided version should be a str data type but is of type {}.".format(
#                 type(input_version)
#             )
#         )

#     # when the part to split is only digits or no digits at all, the process is finished
#     if (
#         input_version.isdigit()
#         or any(char.isdigit() for char in input_version) == False
#     ):
#         version = output_version + [input_version]
#         return [int(segment) if segment.isdigit() else segment for segment in version]

#     # otherwise check until what position it is a digit (since we want to keep i.e. a multiple digits number as one integer)
#     pos = 0
#     while (
#         input_version[pos].isdigit() == input_version[pos + 1].isdigit()
#         and pos != len(input_version) - 2
#     ):  #
#         pos += 1

#     return recursively_split_version_string(
#         input_version[pos + 1 :], output_version + [input_version[: pos + 1]]
#     )


# def get_tag_for_version(tags, version):
#     """
#     Map a version onto an existing tag
#     Input:
#         tags (list): a list of tags to map version onto
#         version (str): the version
#     Returns:
#         list: list with tags that could be the version
#         @TODO: only return the most relevant tag i.e. for key 8 version 4.1 returns ['version-3.4.1', 'version-4.1', 'version-4.4.1']
#     """
#     if isinstance(tags, tuple):
#         tags = list(tags)
#     if type(tags) != list or len(tags) == 0:
#         raise ValueError(
#             "tags should be a list of tags to map the version onto, is a {} of length {}".format(
#                 type(tags), len(tags)
#             )
#         )

#     # stripped_tags = [tag[len(tag)-len(version):] for tag in tags]
#     stripped_tags = [
#         tag[
#             tag.index(
#                 [
#                     str(value)
#                     for value in recursively_split_version_string(tag)
#                     if type(value) == int
#                 ][0]
#             ) :
#         ]
#         if any(char.isdigit() for char in tag)
#         else tag
#         for tag in tags
#     ]
# print(stripped_tags)
# stripped_tags = []
# stripped_version = (
#     version[
#         version.index(
#             [
#                 str(value)
#                 for value in recursively_split_version_string(version)
#                 if type(value) == int
#             ][0]
#         ) :
#     ]
#     if any(char.isdigit() for char in version)
#     else version
# )
# print(stripped_version)

# if version in tags and tags.count(version) == 1:
#     tag = version
# elif version in stripped_tags and stripped_tags.count(version) == 1:
#     tag = tags[stripped_tags.index(version)]
# elif version in stripped_tags and stripped_tags.count(version) > 1:
#     return [
#         tags[index] for index, tag in enumerate(stripped_tags) if tag == version
#     ]
# elif (
#     stripped_version in stripped_tags and stripped_tags.count(stripped_version) == 1
# ):
#     tag = tags[stripped_tags.index(stripped_version)]
# elif (
#     stripped_version in stripped_tags and stripped_tags.count(stripped_version) > 1
# ):
#     return [
#         tags[index]
#         for index, tag in enumerate(stripped_tags)
#         if tag == stripped_version
#     ]

# else:
#     version = re.sub("[^0-9]", "", version)
#     best_match = ("", 0.0)
#     for tag in tags:
#         t_strip = re.sub("[^0-9]", "", tag)
#         match_score = difflib.SequenceMatcher(None, t_strip, version).ratio()
#         if match_score > best_match[1]:
#             best_match = (tag, match_score)
#     tag = best_match[0]
# return [tag]


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
