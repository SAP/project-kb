#
# This file is part of Eclipse Steady.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import io
import json
import os
import time
import zipfile
from contextlib import closing

import plac
import requests
from tqdm import tqdm

from log.logger import logger

NVD_API_KEY = os.getenv("NVD_API_KEY", "")

# note: The NVD has not data older than 2002
START_FROM_YEAR = os.getenv("CVE_DATA_AS_OF_YEAR", "2002")
DATA_PATH = os.getenv("CVE_DATA_PATH", "data/")
FEED_SCHEMA_VERSION = os.getenv("FEED_SCHEMA_VERSION", "1,1")


def do_update(quiet=False):
    # read metadata of last fetch
    last_fetch_metadata = dict()
    try:
        with open(os.path.join(DATA_PATH, "metadata.json"), "r") as f:
            last_fetch_metadata = json.load(f)
            if not quiet:
                logger.info("last fetch: " + last_fetch_metadata["sha256"])
    except Exception:
        last_fetch_metadata["sha256"] = ""
        logger.info(
            "Could not read metadata about previous fetches"
            " (this might be the first time we fetch data).",
            exc_info=True,
        )

    # read metadata of new data from the NVD site
    url = "https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-modified.meta"
    r = requests.get(url, params={"apiKey": NVD_API_KEY})
    if r.status_code != 200:
        logger.error(
            "Received status code {} when contacting {}.".format(r.status_code, url)
        )
        return False

    metadata_txt = r.text.strip().split("\n")
    metadata_dict = dict()
    for d in metadata_txt:
        d_split = d.split(":", 1)
        metadata_dict[d_split[0]] = d_split[1].strip()
    if not quiet:
        logger.info("current:    " + metadata_dict["sha256"])

    # check if the new data is actually new
    if last_fetch_metadata["sha256"] == metadata_dict["sha256"]:
        if not quiet:
            logger.info("We already have this update, no new data to fetch.")
        return False

    do_fetch("modified")
    with open(os.path.join(DATA_PATH, "metadata.json"), "w") as f:
        f.write(json.dumps(metadata_dict))
    return True


def do_fetch_full(start_from_year=START_FROM_YEAR, quiet=False):
    years_to_fetch = [
        y for y in range(int(start_from_year), int(time.strftime("%Y")) + 1)
    ]
    if not quiet:
        logger.info("Fetching feeds: " + str(years_to_fetch))

    for y in years_to_fetch:
        if not do_fetch(y):
            logger.error("Could not fetch data for year " + str(y))


def do_fetch(what, quiet=True):
    """
    the 'what' parameter can be a year or 'recent' or 'modified'
    """
    url = f"https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-{what}.json.zip"
    r = requests.get(url, params={"apiKey": NVD_API_KEY})
    if r.status_code != 200:
        logger.error(
            "Received status code {} when contacting {}.".format(r.status_code, url)
        )
        return False

    with closing(r), zipfile.ZipFile(io.BytesIO(r.content)) as archive:
        for f in archive.infolist():
            logger.info(f.filename)
            data = json.loads(archive.read(f).decode())

    if not quiet:
        pbar = tqdm(data["CVE_Items"], desc="fetching CVE entries", unit="CVE entry")
    else:
        pbar = data["CVE_Items"]
    for v in pbar:
        CVE_id = v["cve"]["CVE_data_meta"]["ID"]
        CVE_year = CVE_id.split("-")[1]
        target_dir = os.path.join(DATA_PATH, CVE_year)
        if not os.path.isdir(target_dir):
            # pbar.set_description('Create dir ' + target_dir)
            os.makedirs(target_dir)

        with open(os.path.join(target_dir, CVE_id + ".json"), "w") as f:
            # pbar.set_description('Updating: ' + CVE_id)
            f.write(json.dumps(v))

    return True


def need_full(quiet=False):
    if os.path.exists(DATA_PATH) and os.path.isdir(DATA_PATH):
        if not os.listdir(DATA_PATH):
            if not quiet:
                logger.info("Data folder {} is empty".format(DATA_PATH))
            return True

        # Directory exists and is not empty
        if not quiet:
            logger.info("Data folder found at " + DATA_PATH)
        return False

    # Directory doesn't exist
    if not quiet:
        logger.info("Data folder {} does not exist".format(DATA_PATH))
    return True


@plac.annotations(
    force=("Force a full update of all feeds", "flag", "f", bool),
    quiet=("Quiet mode (outputs only exception messages)", "flag", "q", bool),
)
def main(force, quiet):

    if force or need_full(quiet=quiet):
        do_fetch_full(quiet=quiet)

    # always do this, so that metadata are fine and so is the /status API
    do_update(quiet=quiet)


# if __name__ == "__main__":
#     plac.call(main)
