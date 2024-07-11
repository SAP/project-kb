import argparse
import os
import sys
from dataclasses import MISSING, dataclass
from typing import List, Optional

from omegaconf import OmegaConf
from omegaconf.errors import (
    ConfigAttributeError,
    ConfigKeyError,
    ConfigTypeError,
    MissingMandatoryValue,
)

from log.logger import logger


def parse_cli_args(args):
    parser = argparse.ArgumentParser(description="Prospector CLI")

    parser.add_argument(
        "vuln_id",
        nargs="?",
        type=str,
        help="ID of the vulnerability to analyze",
    )

    parser.add_argument(
        "--repository", default=None, type=str, help="Git repository url"
    )

    parser.add_argument(
        "--preprocess-only",
        action="store_true",
        help="Commit preprocessing only",
    )

    parser.add_argument("--pub-date", type=str, help="Publication date of the advisory")

    # Allow the user to manually supply advisory description
    parser.add_argument("--description", type=str, help="Advisory description")

    parser.add_argument(
        "--max-candidates",
        type=int,
        help="Maximum number of candidates to consider",
    )

    # parser.add_argument(
    #     "--tag-interval",
    #     type=str,
    #     help="Tag interval (X,Y) to consider (the commit must be reachable from Y but not from X, and must not be older than X)",
    # )

    parser.add_argument(
        "--version-interval",
        type=str,
        help="Version or tag interval X:Y to consider. ",
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
        choices=["always", "never", "optional"],
        type=str,
        help="Use the backend server",
    )

    parser.add_argument(
        "--report",
        choices=["html", "json", "console", "all"],
        type=str,
        help="Format of the report (options: console, json, html, all)",
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

    parser.add_argument(
        "--ignore-refs",
        type=bool,
        default=False,
        help="Whether to ignore the fact that the fixing commit is reachable directly from the advisory",
    )

    return parser.parse_args()


def parse_config_file(filename: str = "config.yaml"):
    if os.path.isfile(filename):
        logger.info(f"Loading configuration from {filename}")
        schema = OmegaConf.structured(ConfigSchema)
        config = OmegaConf.load(filename)
        try:
            merged_config = OmegaConf.merge(schema, config)
            return merged_config
        except ConfigAttributeError as e:
            logger.error(f"Attribute error in {filename}: {e}")
        except ConfigKeyError as e:
            logger.error(f"Key error in {filename}: {e}")
        except ConfigTypeError as e:
            logger.error(f"Type error in {filename}: {e}")
        except Exception as e:
            # General exception catch block for any other exceptions
            logger.error(f"An unexpected error occurred when parsing config.yaml: {e}")
    else:
        logger.error("No configuration file found, cannot proceed.")


# Schema class for "database" configuration
@dataclass
class DatabaseConfig:
    user: str
    password: str
    host: str
    port: int
    dbname: str


# Schema class for "report" configuration
@dataclass
class ReportConfig:
    format: str
    name: str


# Schema class for "llm_service" configuration
@dataclass
class LLMServiceConfig:
    type: str
    model_name: str
    use_llm_repository_url: bool
    ai_core_sk: str
    temperature: float = 0.0


# Schema class for config.yaml parameters
@dataclass
class ConfigSchema:
    redis_url: str = MISSING
    preprocess_only: bool = MISSING
    max_candidates: int = MISSING
    fetch_references: bool = MISSING
    use_nvd: bool = MISSING
    use_backend: str = MISSING
    backend: str = MISSING
    report: ReportConfig = MISSING
    log_level: str = MISSING
    git_cache: str = MISSING
    enabled_rules: List[str] = MISSING
    nvd_token: Optional[str] = None
    database: DatabaseConfig = DatabaseConfig(
        user="postgres", password="example", host="db", port=5432, dbname="postgres"
    )
    llm_service: Optional[LLMServiceConfig] = None
    github_token: Optional[str] = None


# Prospector's own Configuration object (combining args and config.yaml)
@dataclass
class Config:
    def __init__(
        self,
        vuln_id: str,
        repository: str,
        preprocess_only: bool,
        pub_date: str,
        description: str,
        max_candidates: int,
        # tag_interval: str,
        version_interval: str,
        modified_files: str,
        filter_extensions: str,
        keywords: str,
        use_nvd: bool,
        fetch_references: bool,
        use_backend: str,
        backend: str,
        report: ReportConfig,
        report_filename: str,
        ping: bool,
        log_level: str,
        git_cache: str,
        enabled_rules: List[str],
        ignore_refs: bool,
        llm_service: LLMServiceConfig,
    ):
        self.vuln_id = vuln_id
        self.repository = repository
        self.llm_service = llm_service
        self.preprocess_only = preprocess_only
        self.pub_date = pub_date
        self.description = description
        self.max_candidates = max_candidates
        # self.tag_interval = tag_interval
        self.version_interval = version_interval if version_interval else "None:None"
        self.modified_files = modified_files.split(",") if modified_files else []
        self.filter_extensions = filter_extensions
        self.keywords = keywords.split(",") if keywords else []
        self.use_nvd = use_nvd
        self.fetch_references = fetch_references
        self.backend = backend
        self.use_backend = use_backend
        self.report = report
        self.report_filename = report_filename
        self.ping = ping
        self.log_level = log_level
        self.git_cache = git_cache
        self.enabled_rules = enabled_rules
        self.ignore_refs = ignore_refs


def get_configuration(argv):
    args = parse_cli_args(argv)
    conf = parse_config_file(args.config)
    if conf is None:
        sys.exit(
            "No configuration file found, or error in configuration file. Check logs."
        )
    # --repository in CL overrides config.yaml settings for LLM usage
    if args.repository:
        conf.llm_service.use_llm_repository_url = False
    try:
        config = Config(
            vuln_id=args.vuln_id,
            repository=args.repository,
            llm_service=conf.llm_service,
            preprocess_only=args.preprocess_only or conf.preprocess_only,
            pub_date=args.pub_date,
            description=args.description,
            modified_files=args.modified_files,
            keywords=args.keywords,
            max_candidates=args.max_candidates or conf.max_candidates,
            # tag_interval=args.tag_interval,
            version_interval=args.version_interval,
            filter_extensions=args.filter_extensions,
            use_nvd=args.use_nvd or conf.use_nvd,
            fetch_references=args.fetch_references or conf.fetch_references,
            backend=args.backend or conf.backend,
            use_backend=args.use_backend or conf.use_backend,
            report=args.report or conf.report.format,
            report_filename=args.report_filename or conf.report.name,
            ping=args.ping,
            git_cache=conf.git_cache,
            enabled_rules=conf.enabled_rules,
            log_level=args.log_level or conf.log_level,
            ignore_refs=args.ignore_refs,
        )
        return config
    except MissingMandatoryValue as e:
        logger.error(e)
        sys.exit(f"'{e.full_key}' is missing in {args.config}.")
    except Exception as e:
        logger.error(f"Error in {args.config}: {e}.")
        sys.exit(f"Error in {args.config}. Check logs.")
