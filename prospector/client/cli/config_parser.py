import argparse
import os
from dataclasses import dataclass

from omegaconf import OmegaConf

from log.logger import logger


def parse_cli_args(args):
    parser = argparse.ArgumentParser(description="Prospector CLI")
    parser.add_argument(
        "cve_id",
        nargs="?",
        type=str,
        help="ID of the vulnerability to analyze",
    )

    parser.add_argument("--repository", default="", type=str, help="Git repository url")

    parser.add_argument(
        "--preprocess-only",
        action="store_true",
        help="Commit preprocessing only",
    )

    parser.add_argument("--pub-date", type=str, help="Publication date of the advisory")

    parser.add_argument("--description", type=str, help="Advisory description")

    parser.add_argument(
        "--max-candidates",
        type=int,
        help="Maximum number of candidates to consider",
    )

    parser.add_argument(
        "--tag-interval",
        type=str,
        help="Tag interval (X,Y) to consider (the commit must be reachable from Y but not from X, and must not be older than X)",
    )

    parser.add_argument(
        "--version-interval",
        type=str,
        help="Version interval (X,Y) to consider (the corresponding tags will be inferred automatically, and the commit must be reachable from Y but not from X, and must not be older than X)",
    )

    parser.add_argument(
        "--modified-files",
        type=str,
        help="Names (or partial names) comma separated that the commits are supposed to modify",
    )

    parser.add_argument(
        "--filter-extensions",
        type=str,
        help="Filter out commits that do not modify at least one file with this extension",
    )

    parser.add_argument(
        "--keywords",
        type=str,
        help="Consider these specific keywords",
    )

    parser.add_argument(
        "--use-nvd",
        action=argparse.BooleanOptionalAction,
        help="Get data from NVD",
    )

    parser.add_argument(
        "--fetch-references",
        action="store_true",
        help="Fetch content of references linked from the advisory",
    )

    parser.add_argument("--backend", type=str, help="URL of the backend server")

    parser.add_argument(
        "--use-backend",
        default="always",
        choices=["always", "never", "optional"],
        type=str,
        help="Use the backend server",
    )

    parser.add_argument(
        "--report",
        choices=["html", "json", "console", "allfiles"],
        type=str,
        help="Format of the report (options: console, json, html)",
    )

    parser.add_argument(
        "--report-filename",
        type=str,
        help="File where to save the report",
    )

    parser.add_argument(
        "-c", "--config", default="config.yaml", help="Configuration file"
    )

    parser.add_argument(
        "-p",
        "--ping",
        help="Ping the server to check if it's online",
        action="store_true",
    )

    parser.add_argument(
        "-l",
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )

    return parser.parse_args()


def parse_config_file(filename: str = "config.yaml"):
    if os.path.isfile(filename):
        logger.info(f"Loading configuration from {filename}")
        config = OmegaConf.load(filename)
        return config

    return None


@dataclass
class Config:
    def __init__(
        self,
        cve_id: str,
        repository: str,
        preprocess_only: bool,
        pub_date: str,
        description: str,
        max_candidates: int,
        tag_interval: str,
        version_interval: str,
        modified_files: str,
        filter_extensions: str,
        keywords: str,
        use_nvd: bool,
        fetch_references: bool,
        backend: str,
        use_backend: str,
        report: str,
        report_filename: str,
        ping: bool,
        log_level: str,
        git_cache: str,
    ):
        self.cve_id = cve_id
        self.repository = repository
        self.preprocess_only = preprocess_only
        self.pub_date = pub_date
        self.description = description
        self.max_candidates = max_candidates
        self.tag_interval = tag_interval
        self.version_interval = version_interval
        self.modified_files = modified_files
        self.filter_extensions = filter_extensions
        self.keywords = keywords
        self.use_nvd = use_nvd
        self.fetch_references = fetch_references
        self.backend = backend
        self.use_backend = use_backend
        self.report = report
        self.report_filename = report_filename
        self.ping = ping
        self.log_level = log_level
        self.git_cache = git_cache


def get_configuration(argv):
    args = parse_cli_args(argv)
    conf = parse_config_file(args.config)
    if conf is None:
        return False
    return Config(
        cve_id=args.cve_id,
        repository=args.repository,
        preprocess_only=args.preprocess_only or conf.preprocess_only,
        pub_date=args.pub_date or conf.advisory.pub_date,
        description=args.description or conf.advisory.description,
        modified_files=args.modified_files or conf.advisory.modified_files,
        keywords=args.keywords or conf.advisory.keywords,
        max_candidates=args.max_candidates or conf.max_candidates,
        tag_interval=args.tag_interval or conf.tag_interval,
        version_interval=args.version_interval or conf.version_interval,
        filter_extensions=args.filter_extensions or conf.filter_extensions,
        use_nvd=args.use_nvd or conf.use_nvd,
        fetch_references=args.fetch_references or conf.fetch_references,
        backend=args.backend or conf.backend,
        use_backend=args.use_backend or conf.use_backend,
        report=args.report or conf.report.format,
        report_filename=args.report_filename or conf.report.name,
        ping=args.ping,
        git_cache=conf.git_cache,
        log_level=args.log_level or conf.log_level,
    )
