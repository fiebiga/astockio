import os

from fastapi import FastAPI

_ROOT_PATH = os.environ.get("WEB_ROOT", "/")


tags_metadata = [
    {
        "name": "stock_ledger",
        "description": "All operations around interacting with a users stock portfolio/ledger",
    }
]

app = FastAPI(
    root_path=_ROOT_PATH,
    openapi_tags=tags_metadata
)

