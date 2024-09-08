from os import getenv

from fastapi import FastAPI

app = FastAPI(
    docs_url="/",
)


@app.get("/info")
def read_root():
    return {
        "VERSION": getenv("VERSION", "0.0.0"),
    }
