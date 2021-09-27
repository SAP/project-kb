# This file is based on the rest-nvd module that is part of Eclipse Steady.

import json
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

import log.util

_logger = log.util.init_local_logger()


router = APIRouter(
    prefix="/nvd",
    tags=["nvd"],
    # dependencies=[Depends(oauth2_scheme)],
    responses={404: {"description": "Not found"}},
)

DATA_PATH = os.environ.get("CVE_DATA_PATH") or os.path.join(
    os.path.realpath(os.path.dirname(__file__)), "..", "data"
)


@router.get("/vulnerabilities/{vuln_id}")
async def get_vuln_data(vuln_id):
    _logger.debug("Requested data for vulnerability " + vuln_id)

    year = vuln_id.split("-")[1]
    json_file = os.path.join(DATA_PATH, year, vuln_id.upper() + ".json")
    if not os.path.isfile(json_file):
        _logger.info("No file found: " + json_file)
        raise HTTPException(status_code=404, detail="Vulnerability data not found")

    _logger.debug("Serving file: " + json_file)
    with open(json_file) as f:
        data = json.loads(f.read())

    return data


@router.get("/status")
async def status():
    _logger.debug("Serving status page")
    out = dict()
    metadata_file = os.path.join(DATA_PATH, "metadata.json")
    if os.path.isfile(metadata_file):
        with open(metadata_file) as f:
            metadata = json.loads(f.read())
        out["metadata"] = metadata
        return JSONResponse(out)
    raise HTTPException(status_code=404, detail="Missing feed file")
