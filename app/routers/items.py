"""Items CRUD router.

Uses a module-level in-memory store for demonstration. In production, swap
`_items` and `_next_id` for a real repository (database, cache, etc.).
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.metrics import ITEMS_CREATED_TOTAL, ITEMS_TOTAL

router = APIRouter(prefix="/items", tags=["items"])

_items: dict[int, dict] = {}
_next_id: int = 1


class ItemIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(1, ge=0)


class Item(ItemIn):
    id: int


@router.get("", response_model=list[Item])
def list_items() -> list[dict]:
    return list(_items.values())


@router.get("/{item_id}", response_model=Item)
def get_item(item_id: int) -> dict:
    if item_id not in _items:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")
    return _items[item_id]


@router.post("", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemIn) -> dict:
    global _next_id
    new_id = _next_id
    _next_id += 1
    stored = {"id": new_id, **item.model_dump()}
    _items[new_id] = stored
    ITEMS_TOTAL.set(len(_items))
    ITEMS_CREATED_TOTAL.inc()
    return stored


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int) -> None:
    if item_id not in _items:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")
    del _items[item_id]
    ITEMS_TOTAL.set(len(_items))


def reset_state() -> None:
    """Clear the store — used by tests to isolate state between cases."""
    global _next_id
    _items.clear()
    _next_id = 1
    ITEMS_TOTAL.set(0)
