import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel


class Item(BaseModel):
    id: uuid.UUID
    name: str
    price: float
    is_offer: bool | None = None


# generate random uuid for testing
mock_items = [
    Item(id=uuid.uuid4(), name="item1", price=9.99, is_offer=True),
    Item(id=uuid.uuid4(), name="item2", price=19.99, is_offer=False),
    Item(id=uuid.uuid4(), name="item3", price=29.99, is_offer=True),
]


router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[Item])
def list_items():
    return mock_items


@router.post("/")
def create_item(name: str, price: float):
    id = uuid.uuid4()
    item = Item(id=id, name=name, price=price)
    mock_items.append(item)
    return item


@router.get("/{item_id}")
def read_item(item_id: uuid.UUID):
    for item in mock_items:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")


@router.put("/{item_id}")
def update_item(item_id: uuid.UUID, name: str, price: float):
    for i, _item in enumerate(mock_items):
        if _item.id == item_id:
            mock_items[i].name = name
            mock_items[i].price = price
            return mock_items[i]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")


@router.delete("/{item_id}")
def delete_item(item_id: uuid.UUID):
    for i, item in enumerate(mock_items):
        if item.id == item_id:
            del mock_items[i]
            return {"message": "Item deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
