import sys

from fastapi import status
from fastapi.testclient import TestClient

sys.path.append("templates/fastapi_basic")

from templates.fastapi_basic.main import app

client = TestClient(app)


def test_root():
    response = client.get("/info")
    assert response.status_code == status.HTTP_200_OK


def test_routers_item():
    # list items
    response = client.get("/items/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 3

    # create item
    item_params = {"name": "Item 4", "price": 20.0}
    response = client.post("/items/", params=item_params)
    assert response.status_code == status.HTTP_200_OK
    item_created = response.json()
    assert item_created["name"] == item_params["name"]
    assert item_created["price"] == item_params["price"]

    # read item
    response = client.get(f"/items/{item_created['id']}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == item_created

    # update item
    item_to_update = {"name": "Item 4 Updated", "price": 25.0}
    response = client.put(f"/items/{item_created['id']}", params=item_to_update)
    assert response.status_code == status.HTTP_200_OK
    item_read = client.get(f"/items/{item_created['id']}").json()
    assert item_read["name"] == item_to_update["name"]
    assert item_read["price"] == item_to_update["price"]

    # delete item
    response = client.delete(f"/items/{item_created['id']}")
    assert response.status_code == status.HTTP_200_OK
    response = client.get(f"/items/{item_created['id']}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
