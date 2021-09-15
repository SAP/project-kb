import re
from typing import Tuple


def split_by_non_word(*texts: str) -> Tuple[str, ...]:
    for text in texts:
        yield from [part for part in re.split(r"[\W_]", text) if part != ""]


def split_by_upper_cases(*texts: str) -> Tuple[str, ...]:
    for text in texts:
        yield from [
            part
            for part in re.sub(r"([A-Z])", r" \1", text).split(sep=" ")
            if part != ""
        ]


def lower_all(*texts: str) -> Tuple[str, ...]:
    return tuple(text.lower() for text in texts)


def tokenize_non_nl_term(term: str) -> Tuple[str, ...]:
    return lower_all(*split_by_non_word(*split_by_upper_cases(term)))
