# This file is based on the rest-nvd module that is part of Eclipse Steady.

import json
import os

import requests
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from log.logger import logger

from log.logger import logger

router = APIRouter(
    prefix="/nvd",
    tags=["nvd"],
    # dependencies=[Depends(oauth2_scheme)],
    responses={404: {"description": "Not found"}},
)


NVD_REST_ENDPOINT = "https://services.nvd.nist.gov/rest/json/cves/2.0"
NVD_API_KEY = os.getenv("NVD_API_KEY")
DATA_PATH = os.getenv("CVE_DATA_PATH")


def get_from_nvd(cve_id: str):
    """
    Get an advisory from the NVD dtabase
    """
    try:
        if NVD_API_KEY is None:
            logger.warning("No NVD API key provided, rate liting may apply")

@router.get("/vulnerabilities/by-year/{year}")
async def get_vuln_list_by_year(year: str):
    logger.debug("Requested list of vulnerabilities for " + year)

        response = requests.get(NVD_REST_ENDPOINT, headers=headers, params=params)

    data_dir = os.path.join(DATA_PATH, year)
    if not os.path.isdir(data_dir):
        logger.info("No data found for year " + year)
        raise HTTPException(
            status_code=404, detail="No vulnerabilities found for " + year
        )

    logger.debug("Serving data for year " + year)
    vuln_ids = [vid.rstrip(".json") for vid in os.listdir(data_dir)]
    results = {"count": len(vuln_ids), "data": vuln_ids}
    return JSONResponse(results)


@router.get("/vulnerabilities/{vuln_id}")
async def get_vuln_data(vuln_id):
    logger.debug("Requested data for vulnerability " + vuln_id)

    json_file = os.path.join(DATA_PATH, f"{vuln_id.upper()}.json")
    if not os.path.isfile(json_file):
        logger.info("No file found: " + json_file)
        raise HTTPException(
            status_code=404, detail=json_file
        )  # detail="Vulnerability data not found")

    logger.debug("Serving file: " + json_file)
    with open(json_file) as f:
        data = json.loads(f.read())

    return data


@router.get("/status")
async def status():
    logger.debug("Serving status page")
    out = dict()
    metadata_file = os.path.join(DATA_PATH, "metadata.json")
    if os.path.isfile(metadata_file):
        with open(metadata_file) as f:
            metadata = json.loads(f.read())
        out["metadata"] = metadata
        return JSONResponse(out)
    raise HTTPException(status_code=404, detail="Missing feed file")
