from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from util.config_parser import parse_config_file
from service.api.routers.jobs import connect_to_db

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
    db = connect_to_db()
    joblist = db.get_all_jobs()
    return templates.TemplateResponse(
        "index.html", {"request": request, "joblist": joblist}
    )
