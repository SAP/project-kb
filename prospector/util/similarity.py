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
    """Calculates the Levenshtein distance between a and b.
    https://en.wikipedia.org/wiki/Levenshtein_distance"""
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


# Credit to: https://www.guyrutenberg.com/2008/12/15/damerau-levenshtein-distance-in-python/
def damerau_levenshtein_edit_distance(s1: Tuple, s2: Tuple) -> int:
    """
    Compute the Damerau-Levenshtein distance between two given
    strings (s1 and s2)
    https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance
    """
    d = {}
    lenstr1 = len(s1)
    lenstr2 = len(s2)
    for i in range(-1, lenstr1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, lenstr2 + 1):
        d[(-1, j)] = j + 1

    for i in range(lenstr1):
        for j in range(lenstr2):
            if s1[i] == s2[j]:
                cost = 0
            else:
                cost = 1
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,  # deletion
                d[(i, j - 1)] + 1,  # insertion
                d[(i - 1, j - 1)] + cost,  # substitution
            )
            if i and j and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[i - 2, j - 2] + cost)  # transposition

    return d[lenstr1 - 1, lenstr2 - 1]
