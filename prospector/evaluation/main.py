import signal
import sys
from typing import Callable, Dict
from omegaconf import OmegaConf
from evaluation.analyse import (
    analyse_category_flows,
    analyse_prospector_reports,
    count_existing_reports,
    generate_checkmarks_table,
    generate_sankey_diagram,
)
from evaluation.analyse_statistics import (
    analyse_statistics,
    overall_execution_time,
)
from evaluation.dispatch_jobs import dispatch_prospector_jobs, empty_queue
from evaluation.utils import config


class CommandRegistry:
    def __init__(self):
        self.commands: Dict[str, Callable] = {}

    def register(self, name: str):
        def decorator(func: Callable):
            self.commands[name] = func
            return func

        return decorator

    def execute(self, name: str, *args, **kwargs):
        if name not in self.commands:
            raise ValueError(f"Command '{name}' not found")
        return self.commands[name](*args, **kwargs)


registry = CommandRegistry()


@registry.register("execute")
def execute_command(config):
    dispatch_prospector_jobs(config.input, config.cve)


@registry.register("analyse_reports")
def analyze_reports_command(config):
    analyse_prospector_reports(config.input, config.cve)


@registry.register("analyse_statistics")
def analyze_stats_command(config):
    analyse_statistics(config.input)


@registry.register("execution_time")
def execution_time_command(config):
    overall_execution_time(config.input)


@registry.register("category_flows")
def category_flows_command(config):
    analyse_category_flows()


@registry.register("checkmarks")
def checkmarks_command(config):
    generate_checkmarks_table(config.input, config.cve)


@registry.register("empty_queue")
def empty_queue_command(config):
    empty_queue()


@registry.register("count_reports")
def count_reports_command(config):
    count_existing_reports(config.input)


@registry.register("sankey_diagram")
def sankey_diagram_command(config):
    generate_sankey_diagram(
        "mvi_old_reports",
        "mvi_old_reports(new_categories)",
        "mvi_without_llm",
    )


def sig_handler(signum, frame):
    print("You pressed Ctrl+C!")
    sys.exit(0)


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <command>")
        sys.exit(1)

    command = sys.argv[1]

    try:
        registry.execute(command, config)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, sig_handler)
    main()
