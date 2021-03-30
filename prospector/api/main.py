import os
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


from fastapi.responses import HTMLResponse
from typing import Optional

from commitdb.postgres import PostgresCommitDB
db_pass = (os.environ['POSTGRES_PASSWORD'])
connect_string = "HOST=localhost;DB=postgres;UID=postgres;PWD={};PORT=5432;".format(db_pass)

db = PostgresCommitDB()
db.connect(connect_string)

# legacy prospector
import main as prospector

api_metadata = [
    {
        "name": "data",
        "description": "Operations with data used to train ML models.",
    },
    {
        "name": "jobs",
        "description": "Manage jobs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]


app = FastAPI(openapi_tags=api_metadata)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ======================================
# AUTH STUFF
# The following is taken from https://fastapi.tiangolo.com/tutorial/security/first-steps/
# with slight modifications to support roles.
# This will be moved to a separate file eventually,
# as explained here: https://fastapi.tiangolo.com/tutorial/bigger-applications/

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "roles": ['user'],
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "roles": ['user','admin'],
        "hashed_password": "fakehashedsecret2",
        "disabled": False,
    },
}

class User(BaseModel):
    username: str
    email: Optional[str] = None
    roles: Optional[list] = []
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user

def fake_hash_password(password: str):
    return "fakehashed" + password

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# ===================================
# Application APIs


# -----------------------------------------------------------------------------
#
@app.post("/jobs/", tags=['jobs'])
async def create_job(vulnerability_id='', description='', url=''):
    return {
        "id": 12,
        "status": "WAITING",
        "query": "CVE-1234-5678",
        "results": []
    }


@app.get("/jobs/{job_id}", tags=['jobs'])
async def get_job(job_id, current_user: User = Depends(get_current_active_user)):
    if current_user.username != 'alice':
        raise HTTPException(status_code=400, detail="Unauthorized")

    return {
        "id": job_id,
        "owner": 'alice',
        "status": "RUNNING",
        "query": "CVE-1234-5678",
        "results": []
    }

# -----------------------------------------------------------------------------
# Data here refers to training data, used to train ML models
# TODO find a less generic term
@app.get("/data", tags=['data'])
async def get_data():
    return [
        {
        'repository_url': "https://github.com/apache/struts",
        'commit_id': 'a4612fe8232678cab3297',
        'label': 1,
        'vulnerability_id': 'CVE-XXXX-YYYY'
        },
        {
        'repository_url': "https://github.com/apache/struts",
        'commit_id': 'a4612fe8232678cab3297',
        'label': 1,
        'vulnerability_id': 'CVE-XXXX-YYYY'
        },
        {
        'repository_url': "https://github.com/apache/struts",
        'commit_id': 'a4612fe8232678cab3297',
        'label': 1,
        'vulnerability_id': 'CVE-XXXX-YYYY'
        },
    ]


@app.post("/data", tags=['data'])
async def create_data(repository_url, commit_id, label, vulnerability_id):
    return {
        'repository_url': repository_url,
        'commit_id': commit_id,
        'label': label,
        'vulnerability_id': vulnerability_id
    }
# -----------------------------------------------------------------------------
@app.get("/commits/{repository_url}")
async def get_commits(repository_url, commit_id=None, token = Depends(oauth2_scheme)):
    commit = (commit_id, repository_url)
    data = db.lookup( commit )
    
    return data


# -----------------------------------------------------------------------------
@app.post("/legacy", response_class=HTMLResponse)
async def make_legacy_query(vulnerability_id,repository_url=""):
    prospector.main(vulnerability_id=vulnerability_id, repo_url = repository_url)
    return """
    <html>
        <head>
            <title>Prospector</title>
        </head>
        <body>
            <h1>Results</h1>
            .........
        </body>
    </html>
    """


# -----------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def read_items():
    return """
    <html>
        <head>
            <title>Prospector</title>
        </head>
        <body>
            <h1>Prospector API</h1>
            Click <a href="/docs">here</a> for docs and here for <a href="/openapi.json">OpenAPI specs</a>.
        </body>
    </html>
    """
@app.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}
