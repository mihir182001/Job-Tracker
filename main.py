from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from logger_config import logger
from fastapi import FastAPI
import os

from database import bindBase
from routers.routes import router

from dotenv import load_dotenv

load_dotenv()

try:
    SECRET_KEY = os.environ["SECRET_KEY"]
    ALGORITHM = os.environ["ALGORITHM"]
    ACCESS_TOKEN_EXPIRE_MINUTES = os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"]
except KeyError as e:
    raise ValueError("Please check your environment variables")

# Create all database tables
bindBase()

app = FastAPI(
    title="Job Tracker API",
    description="Professional Job Tracking Backend",
    version="1.0.0"
)

@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException
):
    logger.warning(
        f"HTTP error: {exc.status_code} | Path: {request.url.path} | Detail: {exc.detail}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    logger.error(
        f"Unexpected error at {request.url.path}: {str(exc)}",
        exc_info=True
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error. Please try again later."
        }
    )

@app.get("/")
def home():
    return {
        "message": "Job Tracker API running successfully"
    }

_PREFIX = "/api/v1"
# Include all routes
app.include_router(router, prefix=_PREFIX)
