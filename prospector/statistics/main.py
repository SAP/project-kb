from typing import Tuple, Union


class ForbiddenDuplication(ValueError):
    ...


LEVEL_DELIMITER = "."


class StatisticCollection(dict):
    def record(self, name: Union[str, Tuple[str, ...]], value):
        if isinstance(name, str):
            if LEVEL_DELIMITER in name:
                raise ValueError(
                    f"do not use level delimiter {LEVEL_DELIMITER} in names,"
                    " hierarchical entries should be specified by tuples"
                )
            elif name not in self:
                self[name] = value
            else:
                raise ForbiddenDuplication(f"{name} already added")
        elif isinstance(name, tuple):
            if len(name) == 1:
                self.record(name[0], value)
            elif len(name) > 1:
                current_name = name[0]
                if current_name not in self:
                    self[current_name] = StatisticCollection()
                    self[current_name].record(name[1:], value)
                else:
                    raise ForbiddenDuplication(f"{name} already added")
        else:
            raise ValueError("only string or tuple keys are enabled")
