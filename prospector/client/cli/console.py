HEADER = "\033[95m"
OKBLUE = "\033[94m"
OKCYAN = "\033[96m"
OKGREEN = "\033[92m"
WARNING = "\033[93m"
FAIL = "\033[91m"
ENDC = "\033[0m"
BOLD = "\033[1m"
LIGHT = "\033[97m"
UNDERLINE = "\033[4m"


def msg(text: str, code: str):
    indent = False
    right = ""
    if code == "ok":
        color = OKGREEN
        right = f"[{color}OK{ENDC}]"
    elif code == "warn" or code == "warning":
        color = WARNING
        right = f"[{color}??{ENDC}]"
    elif code == "err" or code == "error":
        color = FAIL
        right = f"[{color}!!{ENDC}]"
    elif code == "note":
        indent = True
        text = f"{ENDC}{text}{ENDC}"

    if indent:
        print("  ", end="")
    print(f"{text:<70}{right}", end=None)
