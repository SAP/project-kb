from __future__ import annotations

from statistics import mean, median, stdev
from typing import Optional, Tuple, Union

from util.inspection import caller_name
from util.type_safety import is_instance_of_either


class ForbiddenDuplication(ValueError):
    """Custom Error for Collections"""

    ...


LEVEL_DELIMITER = "."


class SubCollectionWrapper:
    def __init__(self, collection: StatisticCollection):
        self.collection = collection


class TransparentWrapper(SubCollectionWrapper):
    def __getattr__(self, item):
        return self.collection.__getattribute__(item)

    def __getitem__(self, key):
        return self.collection.__getitem__(key)

    def __enter__(self) -> TransparentWrapper:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            raise exc_val


def _summarize_list(collection, unit: Optional[str] = None):
    if unit is None:
        return (
            f"average = {mean(collection)}",
            f"deviation = {stdev(collection)}",
            f"median = {median(collection)}",
            f"count = {len(collection)}",
            f"sum = {sum(collection)}",
        )
    else:
        return (
            f"average = {mean(collection)} {unit}",
            f"deviation = {stdev(collection)} {unit}",
            f"median = {median(collection)} {unit}",
            f"count = {len(collection)}",
            f"sum = {sum(collection)} {unit}",
        )


class StatisticCollection(dict):
    """The StatisticCollection can contain nested sub-collections, and each entry in the
    collection can hold a list of values along with an optional unit.
    """

    def __init__(self):
        super().__init__()
        self.units = {}

    def drop_all(self):
        for item in self.values():
            if isinstance(item, StatisticCollection):
                item.drop_all()
        self.clear()
        self.units.clear()

    def record(
        self,
        name: Union[str, Tuple[str, ...]],
        value,
        unit: Optional[str] = None,
        overwrite=False,
    ):
        """Adds a new statistic to the collection."""
        if isinstance(name, str):
            if not overwrite and name in self:
                raise ForbiddenDuplication(f"{name} already added")

            if LEVEL_DELIMITER in name:
                raise ValueError(
                    f"do not use level delimiter {LEVEL_DELIMITER} in names,"
                    " hierarchical entries should be specified by tuples"
                )
            else:
                self[name] = value
                if unit is not None:
                    self.units[name] = unit
        elif isinstance(name, tuple):
            if len(name) == 1:
                self.record(name[0], value, unit=unit)
            elif len(name) > 1:
                current_name = name[0]
                if current_name not in self:
                    self[current_name] = StatisticCollection()
                current_collection = self[current_name]
                if not isinstance(current_collection, StatisticCollection):
                    raise ForbiddenDuplication(
                        f"{name} already added as a single value"
                    )
                else:
                    current_collection.record(name[1:], value, unit=unit)
        else:
            raise ValueError("only string or tuple keys are enabled")

    def sub_collection(
        self,
        name: Optional[Union[str, Tuple[str, ...]]] = None,
    ) -> StatisticCollection:
        """Creates a nested `StatisticCollection` as the value of `name`. Returns
        and existing collection if there already exists one under `name`.
        """
        if name is None:
            name = caller_name()

        if name not in self:
            self.record(name, StatisticCollection())

        return self[name]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            raise exc_val

    def __getitem__(self, key: Union[str, Tuple[str, ...]]):
        if isinstance(key, str):
            return super().__getitem__(key)
        elif isinstance(key, tuple):
            if len(key) == 1:
                return self[key[0]]
            elif len(key) > 1:
                current_collection = self[key[0]]
                if isinstance(current_collection, StatisticCollection):
                    return current_collection[key[1:]]
                else:
                    raise KeyError(f"{key[0]} is a single value")
            else:
                raise KeyError("empty key are not allowed")
        else:
            raise KeyError("only string ot tuple keys allowed")

    def __contains__(self, key):
        if isinstance(key, str):
            return super().__contains__(key)
        elif isinstance(key, tuple):
            if len(key) == 1:
                return key[0] in self
            elif len(key) > 1:
                if key[0] not in self:
                    return False
                current_collection = self[key[0]]
                if isinstance(current_collection, StatisticCollection):
                    return key[1:] in current_collection
                else:
                    raise KeyError(f"{key[0]} is a single value")
            else:
                raise KeyError("empty key are not allowed")
        else:
            raise KeyError("only string ot tuple keys allowed")

    def collect(
        self,
        name: Union[str, Tuple[str, ...]],
        value,
        unit: Optional[str] = None,
    ):
        """Adds a value to the list at key `name`."""
        if name not in self:
            self.record(name, [], unit=unit)

        if isinstance(self[name], list):
            self[name].append(value)
            if unit is not None:
                if name in self.units and self.units[name] != unit:
                    raise ValueError(
                        f"{self.units[name]} is not compatible with {unit}"
                    )
                else:
                    self.units[unit] = unit
        else:
            raise KeyError(f"can not collect into {name}, because it is not a list")

    def collect_unique(
        self,
        name: Union[str, Tuple[str, ...]],
        value,
        ensure_uniqueness: bool = False,
    ):
        if name not in self:
            self.record(name, set())

        if isinstance(self[name], set):
            if not ensure_uniqueness or not (value in self[name]):
                self[name].add(value)
        else:
            raise KeyError(f"can not collect into {name}, because it is not a set")

    def get_descants(self, leaf_only=False, ascents=()):
        """Return the unsorted collection of all its sub collections and their sub collections and so forth."""
        for child_key, child in self.items():
            unit = self.units.get(child_key, None)
            if isinstance(child, StatisticCollection):
                if not leaf_only:
                    yield ascents + (child_key,), child, unit
                yield from child.get_descants(ascents=ascents + (child_key,))
            else:
                yield ascents + (child_key,), child, unit

    def generate_console_tree(self) -> str:
        """Generate a visual representation of the collection."""
        descants = sorted(
            list(self.get_descants()), key=lambda e: LEVEL_DELIMITER.join(e[0])
        )
        lines = ["+--+[root]"]
        for key, descant, unit in descants:
            indent = "|  " * len(key)
            if isinstance(descant, StatisticCollection):
                lines.append(f"{indent}+--+[{LEVEL_DELIMITER.join(key)}]")
            else:
                last_key = key[-1]
                if (
                    isinstance(descant, list)
                    and len(descant) > 1
                    and is_instance_of_either(descant, int, float)
                ):
                    formatted_node = f"+---[{last_key}]"
                    lines.append(f"{indent}{formatted_node} is a list of numbers with")
                    summary = _summarize_list(descant, unit=unit)
                    for property in summary:
                        lines.append(f"{indent}{' ' * len(formatted_node)} {property}")
                else:
                    if unit is not None:
                        lines.append(f"{indent}+---[{last_key}] = {descant} {unit}")
                    else:
                        lines.append(f"{indent}+---[{last_key}] = {descant}")

        return "\n".join(lines)

    def as_html_ul(self) -> str:
        ul = '<ul class="statistics-list">'
        for key, child in self.items():
            unit = self.units.get(key, None)
            if isinstance(child, StatisticCollection):
                ul += f'<li><i class="fas fa-sitemap"></i> <strong>{key}</strong> {child.as_html_ul()}</li>'
            else:
                if "time" in key:
                    icon = '<i class="fas fa-hourglass-half"></i>'
                else:
                    icon = '<i class="fas fa-info-circle"></i>'
                if (
                    isinstance(child, list)
                    and len(child) > 1
                    and is_instance_of_either(child, int, float)
                ):
                    summary = _summarize_list(child, unit=unit)
                    ul += (
                        f"<li>{icon} <strong>{key}</strong>"
                        f' is a list of numbers<ul class="statistics-list property-list">'
                    )
                    for property in summary:
                        ul += f'<li class="property">{property}</li>'
                    ul += "</ul></li>"
                else:
                    ul += f"<li>{icon} <strong>{key}</strong> = "
                    if isinstance(child, list) and len(child) == 1:
                        child = child[0]
                    if isinstance(child, float):
                        ul += f"{child:.4}"
                    else:
                        ul += str(child)
                    if unit is not None:
                        ul += f" {unit}"
                    ul += "</li>"
        ul += "</ul>"
        return ul

    def as_json(self) -> dict:
        for key, child in self.items():
            print(f"key: {key}, child: {child}")
