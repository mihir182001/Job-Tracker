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

@app.get("/")
def home():
    return {
        "message": "Job Tracker API running successfully"
    }

_PREFIX = "/api/v1"
# Include all routes
app.include_router(router, prefix=_PREFIX)
