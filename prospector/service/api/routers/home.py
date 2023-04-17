from api.rq_utils import queue, get_all_jobs
from fastapi import FastAPI, Request
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse
from util.config_parser import parse_config_file
from rq import Connection, Queue
from rq.job import Job
import redis
import time

# from core.report import generate_report

router = APIRouter(
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="service/static")

config = parse_config_file()
redis_url = config.redis_url


# endpoint for monitoring all job status
@router.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    joblist = get_all_jobs()
    return templates.TemplateResponse(
        "index.html", {"request": request, "joblist": joblist}
    )
