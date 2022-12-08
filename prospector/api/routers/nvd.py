# This file is based on the rest-nvd module that is part of Eclipse Steady.

import json
import os

import requests
from fastapi import APIRouter, HTTPException

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

        headers = {"apiKey": NVD_API_KEY} if NVD_API_KEY else {}
        params = {"cveId": cve_id}

        response = requests.get(NVD_REST_ENDPOINT, headers=headers, params=params)

        if response.status_code != 200:
            return False

        data = response.json()["vulnerabilities"]
        if len(data) == 0:
            return False

        with open(f"{DATA_PATH}/{cve_id}.json", "w") as out:
            json.dump(data[0]["cve"], out)

        return data[0]["cve"]

    except Exception:
        return None


@router.get("/vulnerabilities/{vuln_id}")
async def get_vuln_data(vuln_id):

    json_file = os.path.join(DATA_PATH, f"{vuln_id.upper()}.json")
    if not os.path.isfile(json_file):
        logger.debug("Fallback to NVD")
        data = get_from_nvd(vuln_id.upper())
    else:
        logger.debug("Vulnerability data found locally " + vuln_id)
        with open(json_file) as f:
            data = json.load(f)

    if data is None:
        raise HTTPException(status_code=404, detail="Vulnerability not found.")
    # TODO: check what happens if there's some error here
    return data


# @router.get("/status")
# async def status():
#     logger.debug("Serving status page")
#     out = dict()
#     metadata_file = os.path.join(DATA_PATH, "metadata.json")
#     if os.path.isfile(metadata_file):
#         with open(metadata_file) as f:
#             metadata = json.loads(f.read())
#         out["metadata"] = metadata
#         return JSONResponse(out)
#     raise HTTPException(status_code=404, detail="Missing feed file")

# @router.get("/vulnerabilities/by-year/{year}")
# async def get_vuln_list_by_year(year: str):
#     logger.debug("Requested list of vulnerabilities for " + year)

#     if len(year) != 4 or not year.isdigit():
#         return JSONResponse([])

#     data_dir = os.path.join(DATA_PATH, year)
#     if not os.path.isdir(data_dir):
#         logger.info("No data found for year " + year)
#         raise HTTPException(
#             status_code=404, detail="No vulnerabilities found for " + year
#         )

#     logger.debug("Serving data for year " + year)
#     vuln_ids = [vid.rstrip(".json") for vid in os.listdir(data_dir)]
#     results = {"count": len(vuln_ids), "data": vuln_ids}
#     return JSONResponse(results)
