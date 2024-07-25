import asyncio
import csv
import datetime
import json
from typing import Any, List

Any,
import aiofiles
import aiohttp
import psycopg2
import requests
from psycopg2.extensions import parse_dsn
from psycopg2.extras import DictCursor, DictRow, Json

from backenddb.postgres import PostgresBackendDB
from data_sources.nvd.versions_extraction import (
    extract_version_range,
    extract_version_ranges_cpe,
    process_versions,
)
from datamodel.nlp import extract_products
from log.logger import logger
from util.config_parser import parse_config_file

config = parse_config_file()

# with open("./data/project_metadata.json", "r") as f:
#    global match_list
#    match_list = json.load(f)


def connect_to_db():
    db = PostgresBackendDB(
        config.database.user,
        config.database.password,
        config.database.host,
        config.database.port,
        config.database.dbname,
    )
    db.connect()
    return db


def disconnect_from_database(db):
    db.disconnect()


async def retrieve_vulns(past_days_range: int):
    """Retrieve advisory data from the NVD.

    Params:
        past_days_range (int): How many days in the past the time range of
        retrieved CVEs starts.

    Returns:
        The raw data from the NVD database.
    """
    start_date, end_date = get_time_range(past_days_range)

    data = ""
    # Set up the URL to retrieve the latest CVE entries from NVD
    nvd_url = "https://services.nvd.nist.gov/rest/json/cves/2.0?"

    nvd_url += f"lastModStartDate={start_date}&lastModEndDate={end_date}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(nvd_url) as response:
                if response.status == 200:
                    data = await response.json()
                else:
                    print("Error while trying to retrieve entries")
        except aiohttp.ClientError as e:
            print(str(e))
            logger.error(
                "Error while retrieving vulnerabilities from NVD", exc_info=True
            )

    return data


def save_vuln_to_db(vulns: List[Any]):
    """Saves raw advisory data to the database for a list of advisories as
    obtained from the NVD database."""
    db = connect_to_db()
    for vuln in vulns["vulnerabilities"]:
        vuln_id = vuln["cve"]["id"]
        pub_date = vuln["cve"]["published"]
        mod_date = vuln["cve"]["lastModified"]
        raw_record = json.dumps(vuln)
        source = "NVD"
        url = (
            f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveID={vuln_id}"
        )

        res = db.lookup_vuln_id(vuln_id, mod_date)
        if res[0] == 0:
            print(f"Saving vuln: {vuln_id} in database")
            db.save_vuln(vuln_id, pub_date, mod_date, raw_record, source, url)
    db.disconnect()


async def get_cve_by_id(id):
    nvd_url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveID={id}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(nvd_url) as response:
                if response.status == 200:
                    data = await response.json()
                else:
                    print("Error while trying to retrieve entry")
        except aiohttp.ClientError as e:
            print(str(e))
            logger.error(
                "Error while retrieving vulnerability from NVD", exc_info=True
            )
    return data


async def add_single_cve(vuln_id: str):
    raw_json_cve = get_cve_by_id(vuln_id)
    save_vuln_to_db(raw_json_cve)


def write_list_to_file(lst, filename):
    with open(filename, "w") as file:
        for item in lst:
            file.write(str(item) + "\n")


def csv_to_json(csv_file_path):
    with open(csv_file_path, "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        data = []
        # Skip the header row
        next(csv_reader)
        # Loop through the rows of the file
        for row in csv_reader:
            # Create a dictionary for the row data
            row_data = {
                "project": row[0],
                "service_name": row[1],
                "repository": row[2],
            }
            data.append(row_data)
    # Convert to JSON object
    json_data = json.dumps(data)
    return json_data


def get_time_range(d_time):
    # calculate the date to retrieve new entries (%Y-%m-%dT%H:%M:%S.%f%2B01:00)
    date_now = datetime.datetime.now()
    start_date = (date_now - datetime.timedelta(days=d_time)).strftime(
        "%Y-%m-%dT%H:%M:%S"
    )
    end_date = date_now.strftime("%Y-%m-%dT%H:%M:%S")
    return start_date, end_date


async def process_entries():
    # start_date,end_date=get_time_range(d_time)
    db = connect_to_db()

    # Retrieve unprocessed entries from the vulnerability table
    unprocessed_vulns = db.get_unprocessed_vulns()

    # Process each entry
    processed_vulns = []
    for unprocessed_vuln in unprocessed_vulns:
        entry_id = unprocessed_vuln[0]
        raw_record = unprocessed_vuln[1]

        processed_vuln = await map_entry(raw_record)
        if processed_vuln is not None:
            processed_vulns.append(processed_vuln)
            db.save_processed_vuln(
                entry_id,
                processed_vuln["repo_url"],
                processed_vuln["version_interval"],
            )
    db.disconnect()
    return processed_vulns


async def map_entry(vuln):
    # TODO: improve mapping technique
    async with aiofiles.open("./data/project_metadata.json", "r") as f:
        match_list = json.loads(await f.read())

    project_names = extract_products(vuln["cve"]["descriptions"][0]["value"])
    # print(project_names)
    for project_name in project_names:
        for data in match_list.values():
            keywords = [kw.lower() for kw in data["search keywords"]]
            if project_name.lower() in keywords:
                version = extract_version_range(
                    vuln["cve"], vuln["cve"]["descriptions"][0]["value"]
                )
                filtered_vuln = {
                    "nvd_info": vuln,
                    "repo_url": data["git"],
                    "version_interval": version,
                }
                print(vuln["cve"]["id"])
                return filtered_vuln

    return None


# if no map is possible search project name using GitHub API
def retrieve_repository(project_name):
    """
    Retrieve the GitHub repository URL for a given project name
    """
    # GitHub API endpoint for searching repositories
    url = "https://api.github.com/search/repositories"

    query_params = {"q": project_name, "sort": "stars", "order": "desc"}

    response = requests.get(url, params=query_params)

    if response.status_code == 200:
        data = response.json()
        if data["total_count"] > 0:
            repository_url = data["items"][0]["html_url"]
            return repository_url

    return None
