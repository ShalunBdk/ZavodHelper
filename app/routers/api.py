"""API routes for CRUD operations."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import ItemType
from app.schemas import (
    ItemCreate, ItemUpdate, ItemResponse, ItemListResponse,
    ImportData
)
from app.crud import (
    get_items, get_item, create_item, update_item, delete_item,
    search_items, get_items_by_type, bulk_import_items, export_all_items
)

router = APIRouter(prefix="/api", tags=["API"])


@router.get("/items", response_model=list[ItemListResponse])
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    item_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all items with pagination."""
    type_filter = None
    if item_type:
        try:
            type_filter = ItemType(item_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid item type")

    items = get_items(db, skip=skip, limit=limit, item_type=type_filter)
    return [
        ItemListResponse(
            id=item.id,
            title=item.title,
            item_type=item.item_type,
            pages_count=len(item.pages),
            created_at=item.created_at,
            updated_at=item.updated_at
        )
        for item in items
    ]


@router.get("/items/search")
def search(
    q: str = Query(..., min_length=1),
    item_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Search items by title."""
    type_filter = None
    if item_type:
        try:
            type_filter = ItemType(item_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid item type")

    items = search_items(db, q, type_filter)
    return [
        {
            "id": item.id,
            "title": item.title,
            "item_type": item.item_type,
            "pages_count": len(item.pages)
        }
        for item in items
    ]


@router.get("/items/{item_id}", response_model=ItemResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    """Get a single item with all pages and actions."""
    item = get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/items", response_model=ItemResponse, status_code=201)
def create_new_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Create a new item."""
    return create_item(db, item)


@router.put("/items/{item_id}", response_model=ItemResponse)
def update_existing_item(
    item_id: int,
    item: ItemUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing item."""
    updated = update_item(db, item_id, item)
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated


@router.delete("/items/{item_id}")
def delete_existing_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item."""
    if not delete_item(db, item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "deleted", "id": item_id}


# Data type specific endpoints
@router.get("/incidents")
def get_incidents(db: Session = Depends(get_db)):
    """Get all incidents with full data."""
    items = get_items_by_type(db, ItemType.INCIDENT)
    return [
        {
            "id": item.id,
            "title": item.title,
            "pages": [
                {
                    "title": page.title,
                    "time": page.time,
                    "image": page.image or "",
                    "actions": [action.text for action in page.actions]
                }
                for page in item.pages
            ]
        }
        for item in items
    ]


@router.get("/instructions")
def get_instructions(db: Session = Depends(get_db)):
    """Get all instructions with full data."""
    items = get_items_by_type(db, ItemType.INSTRUCTION)
    return [
        {
            "id": item.id,
            "title": item.title,
            "pages": [
                {
                    "title": page.title,
                    "time": page.time,
                    "image": page.image or "",
                    "actions": [action.text for action in page.actions]
                }
                for page in item.pages
            ]
        }
        for item in items
    ]


# Export/Import endpoints
@router.get("/export")
def export_data(db: Session = Depends(get_db)):
    """Export all data in JSON format compatible with the original structure."""
    return export_all_items(db)


@router.post("/import")
def import_data(data: ImportData, db: Session = Depends(get_db)):
    """Import data from JSON."""
    result = bulk_import_items(db, data)
    return {
        "status": "success",
        "imported": result
    }


@router.delete("/clear")
def clear_all_data(
    confirm: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Clear all data from the database. Requires confirm=true."""
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Set confirm=true to clear all data"
        )

    from app.models.models import Item
    db.query(Item).delete()
    db.commit()
    return {"status": "cleared"}
