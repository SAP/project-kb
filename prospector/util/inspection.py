import inspect
from typing import Tuple


def caller_name(skip=2) -> Tuple[str, ...]:
    """Get a name of a caller in the format module.class.method
    Note: It will not work correctly for static methods in classes.

    `skip` specifies how many levels of stack to skip while getting caller
    name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.

    An empty string is returned if skipped levels exceed stack height
    """
    stack = inspect.stack()
    start = 0 + skip
    if len(stack) < start + 1:
        return tuple()
    parent_frame = stack[start][0]
    name = []
    module = inspect.getmodule(parent_frame)
    # `modname` can be None when frame is executed directly in console
    if module:
        name.extend(module.__name__.split("."))
    # detect classname
    if "self" in parent_frame.f_locals:
        # I don't know any way to detect call from the object method
        # there seems to be no way to detect static method call - it will be just a function call
        name.append(parent_frame.f_locals["self"].__class__.__qualname__)
    codename = parent_frame.f_code.co_name
    if codename != "<module>":  # top level usually
        name.append(codename)  # function or a method
    del parent_frame
    return tuple(name)
