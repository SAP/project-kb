from enum import Enum
from typing import Optional

from colorama import Fore, Style


class MessageStatus(Enum):
    OK = Fore.GREEN
    WARNING = Fore.YELLOW
    ERROR = Fore.RED


class MessageWriter(object):
    indent: str = "  "

    def __init__(self, message: str):
        self._message = message
        self.status: MessageStatus = MessageStatus.OK

    def __enter__(self):
        print(f"{Fore.LIGHTWHITE_EX}{self._message}{Style.RESET_ALL} ...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            self.status = MessageStatus.ERROR
        print(
            f"{MessageWriter.indent}[{self.status.value}{self.status.name}{Style.RESET_ALL}]"
        )
        if exc_val is not None:
            raise exc_val

    def print_note(self, note: str, new_status: Optional[MessageStatus] = None):
        print(f"{MessageWriter.indent}{Fore.WHITE}{note}")
        if isinstance(new_status, MessageStatus):
            self.status = new_status
