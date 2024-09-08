import azure.functions as func
from core import app as fastapi_app
from dotenv import load_dotenv

load_dotenv()

app = func.AsgiFunctionApp(
    app=fastapi_app,
    http_auth_level=func.AuthLevel.ANONYMOUS,
)
