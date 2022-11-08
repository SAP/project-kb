import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse

# from .dependencies import oauth2_scheme
from api.routers import jobs, nvd, preprocessed, users

api_metadata = [
    {"name": "data", "description": "Operations with data used to train ML models."},
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
    allow_origins=["http://localhost:3000", "localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(jobs.router)
app.include_router(nvd.router)
app.include_router(preprocessed.router)


# -----------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def read_items():
    response = RedirectResponse(url="/docs")
    return response
    # return """
    # <html>
    #     <head>
    #         <title>Prospector</title>
    #     </head>
    #     <body>
    #         <h1>Prospector API</h1>
    #         Click <a href="/docs">here</a> for docs and here for
    #         <a href="/openapi.json">OpenAPI specs</a>.
    #     </body>
    # </html>
    # """


# -----------------------------------------------------------------------------
@app.get("/status")
async def get_status():
    return {"status": "ok"}


if __name__ == "__main__":

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=80,
    )
