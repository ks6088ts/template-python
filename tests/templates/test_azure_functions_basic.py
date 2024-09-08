from fastapi import status
from fastapi.testclient import TestClient

from templates.azure_functions_basic.core import app

client = TestClient(app)


def test_root():
    response = client.get("/info")
    assert response.status_code == status.HTTP_200_OK
