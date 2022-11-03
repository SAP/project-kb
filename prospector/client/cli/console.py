from enum import Enum
from typing import Optional

from colorama import Fore, Style


class MessageStatus(Enum):
    OK = Fore.GREEN
    WARNING = Fore.YELLOW
    ERROR = Fore.RED


class ConsoleWriter(object):
    indent: str = "  "

    def __init__(self, message: str):
        self._message = message
        self.status: MessageStatus = MessageStatus.OK

    def __enter__(self):
        print(f"{Fore.LIGHTWHITE_EX}{self._message}{Style.RESET_ALL}", end=" ")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            self.status = MessageStatus.ERROR
        print(
            f"{ConsoleWriter.indent}[{self.status.value}{self.status.name}{Style.RESET_ALL}]",
            end="\n",
        )
        if exc_val is not None:
            raise exc_val

    def set_status(self, status: MessageStatus):
        self.status = status

    def print(self, note: str, status: Optional[MessageStatus] = None):
        print(f"{ConsoleWriter.indent}{Fore.WHITE}{note}", end="\n")
        if isinstance(status, MessageStatus):
            self.set_status(status)
