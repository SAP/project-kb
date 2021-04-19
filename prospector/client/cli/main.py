#!/usr/bin/python3

# from advisory_processor.advisory_processor import AdvisoryProcessor
import argparse
import configparser
import logging
import os
import sys
from pathlib import Path
from pprint import pprint

import requests

from client.cli.prospector_client import MAX_CANDIDATES, prospector
from git.git import GIT_CACHE

logger = logging.getLogger("prospector")

# VERSION = '0.1.0'
# SCRIPT_PATH=os.path.dirname(os.path.realpath(__file__))
# print(SCRIPT_PATH)


def parseArguments():
    parser = argparse.ArgumentParser(description="Prospector CLI")
    parser.add_argument(
        "vulnerability_id", nargs="?", help="ID of the vulnerability to analyze"
    )

    parser.add_argument("--repository", default="", help="Git repository")

    parser.add_argument(
        "--pub-date", default="", help="Publication date of the advisory"
    )

    parser.add_argument("--descr", default="", help="Text of the advisory")

    parser.add_argument(
        "--max-candidates",
        default=MAX_CANDIDATES,
        type=int,
        help="Maximum number of candidates to consider",
    )

    parser.add_argument("--use-nvd", action="store_true", help="Get data from NVD")

    parser.add_argument("-c", "--conf", help="specify configuration file")

    parser.add_argument(
        "-p", "--ping", help="Contact server to check it's alive", action="store_true"
    )

    parser.add_argument(
        "-v", "--verbose", help="increase output verbosity", action="store_true"
    )

    parser.add_argument(
        "-d",
        "--debug",
        help="increase output verbosity even more and output stack-traces on exceptions",
        action="store_true",
    )

    return parser.parse_args()


def getConfiguration(customConfigFile=None):
    # simple is better: only one configuration file is
    # taken into account, no overriding of options from
    # one file to the other!

    # the order is (as soon as one is found, the rest is ignored):
    # 1) the file passed as argument to this function
    # 2) ./prospector.conf
    # 3) ~/.prospector/conf

    localConfigFile = os.path.join(os.getcwd(), "prospector.conf")
    userConfigFile = os.path.join(Path.home(), ".prospector/conf")

    config = configparser.ConfigParser()

    if customConfigFile and os.path.isfile(customConfigFile):
        configFile = customConfigFile
    elif os.path.isfile(localConfigFile):
        configFile = localConfigFile
    elif os.path.isfile(userConfigFile):
        configFile = userConfigFile
    else:
        return None

    print("Loading configuration from " + configFile)
    config.read(configFile)
    return config


def ping_server(server_url: str, verbose: bool = False):
    """Tries to contact backend server

    Args:
        server_url (str): the URL of the server endpoint
        verbose (bool, optional): enable verbose output. Defaults to False.
    """

    if verbose:
        print("Contacting server " + server_url)

    try:
        response = requests.get(server_url)
        if response.status_code != 200:
            print("Server replied with an unexpected status: " + response.status_code)
        else:
            print("Server ok!")
    except Exception:
        print("Server did not reply")


def main():
    args = parseArguments()
    configuration = getConfiguration(args.conf)

    if configuration is None:
        print("Invalid configuration, exiting.")
        sys.exit(-1)

    verbose = configuration["global"].getboolean("verbose")
    if args.verbose:
        verbose = args.verbose

    debug = configuration["global"].getboolean("debug")
    if args.debug:
        debug = args.debug

    if debug:
        verbose = True

    if configuration["global"].get("nvd_rest_endpoint"):
        nvd_rest_endpoint = configuration["global"].get("nvd_rest_endpoint")

    if args.ping:
        srv = configuration["global"]["server"]
        ping_server(srv, verbose)

    if args.vulnerability_id is None:
        print("No vulnerability id was specified. Cannot proceed.")
        sys.exit(-1)

    vulnerability_id = args.vulnerability_id
    repository = args.repository
    publication_date = args.pub_date
    vuln_descr = args.descr
    use_nvd = args.use_nvd
    max_candidates = args.max_candidates

    git_cache = GIT_CACHE
    if os.environ["GIT_CACHE"]:
        git_cache = os.environ["GIT_CACHE"]
    if configuration["global"].get("git_cache"):
        git_cache = configuration["global"].get("git_cache")

    if verbose:
        print("Using the following configuration:")
        pprint(
            {
                section: dict(configuration[section])
                for section in configuration.sections()
            }
        )

    if verbose:
        print("Vulnerability ID: " + vulnerability_id)

    prospector(
        vulnerability_id,
        repository,
        publication_date,
        vuln_descr,
        use_nvd,
        nvd_rest_endpoint,
        git_cache,
        verbose,
        debug,
        limit_candidates=max_candidates,
    )


if __name__ == "__main__":  # pragma: no cover
    main()
