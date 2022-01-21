"""
Fastapi server main program
"""
import os

import uvicorn
from config import DEBUG
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

version = os.environ.get("TAG", "0.0.1")
app = FastAPI(title="AVL-Exam", version=version)
app.debug = DEBUG
origins = [
    "*",
]

secret_key = "C~u#C$P0T7sdfsdNgnn!vdddS!D2NW{sdfsfG!3"
app.add_middleware(SessionMiddleware, secret_key=secret_key)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/version/")
def get_version():
    return {
        "version": version,
    }


@app.on_event("startup")
async def startup():
    pass


if __name__ == "__main__":
    if DEBUG:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=5000,
            log_level="info",
            reload=True,
            workers=1,
            debug=True,
        )
