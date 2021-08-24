import math
from typing import Set, Tuple


def jaccard_set_similarity(a: Set, b: Set) -> float:
    """https://en.wikipedia.org/wiki/Jaccard_index"""
    return len(a & b) / len(a | b)


def sorensen_dice_set_similarity(a: Set, b: Set) -> float:
    """https://en.wikipedia.org/wiki/S%C3%B8rensen%E2%80%93Dice_coefficient"""
    return (2 * len(a & b)) / (len(a) + len(b))


def otsuka_ochiai_set_similarity(a: Set, b: Set) -> float:
    """https://en.wikipedia.org/wiki/Cosine_similarity"""
    return len(a & b) / math.sqrt(len(a) * len(b))


# Credit to https://folk.idi.ntnu.no/mlh/hetland_org/coding/python/levenshtein.py
# Accessed: 2021-8-24
# This is a straightforward implementation of a well-known algorithm, and thus
# probably shouldn't be covered by copyright to begin with. But in case it is,
# the author (Magnus Lie Hetland) has, to the extent possible under law,
# dedicated all copyright and related and neighboring rights to this software
# to the public domain worldwide, by distributing it under the CC0 license,
# version 1.0. This software is distributed without any warranty. For more
# information, see <http://creativecommons.org/publicdomain/zero/1.0>


def levenshtein_edit_distance(a: Tuple, b: Tuple) -> int:
    """Calculates the Levenshtein distance between a and b."""
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    current = range(n + 1)
    for i in range(1, m + 1):
        previous, current = current, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete = previous[j] + 1, current[j - 1] + 1
            change = previous[j - 1]
            if a[j - 1] != b[i - 1]:
                change = change + 1
            current[j] = min(add, delete, change)

    return current[n]


def normalized_levenshtein_edit_distance(a: Tuple, b: Tuple) -> float:
    return levenshtein_edit_distance(a, b) / max(len(a), len(b))
