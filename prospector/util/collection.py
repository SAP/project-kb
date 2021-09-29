from typing import List, Tuple, Union


def union_of(base: Union[List, Tuple], newer: Union[List, Tuple]) -> Union[List, Tuple]:
    if isinstance(base, list):
        return list(set(base) | set(newer))
    elif isinstance(base, tuple):
        return tuple(set(base) | set(newer))
