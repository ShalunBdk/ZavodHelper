"""API routes for CRUD operations."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import ItemType
from app.schemas import (
    ItemCreate, ItemUpdate, ItemResponse, ItemListResponse,
    ImportData, CategoryCreate, CategoryUpdate, CategoryResponse,
    LocationCreate, LocationUpdate, LocationResponse
)
from app.crud import (
    get_items, get_item, create_item, update_item, delete_item,
    search_items, get_items_by_type, bulk_import_items, export_all_items,
    get_categories, get_category, create_category, update_category, delete_category,
    get_category_items_count,
    get_locations, get_location, create_location, update_location, delete_location
)

router = APIRouter(prefix="/api", tags=["API"])


# Location endpoints
@router.get("/locations", response_model=list[LocationResponse])
def list_locations(db: Session = Depends(get_db)):
    """Get all locations."""
    return get_locations(db)


@router.post("/locations", response_model=LocationResponse, status_code=201)
def create_new_location(location: LocationCreate, db: Session = Depends(get_db)):
    """Create a new location."""
    return create_location(db, location)


@router.put("/locations/{location_id}", response_model=LocationResponse)
def update_existing_location(
    location_id: int,
    location: LocationUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing location."""
    loc = update_location(db, location_id, location)
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return loc


@router.delete("/locations/{location_id}")
def delete_existing_location(location_id: int, db: Session = Depends(get_db)):
    """Delete a location."""
    if not delete_location(db, location_id):
        raise HTTPException(status_code=404, detail="Location not found")
    return {"status": "deleted", "id": location_id}


# Category endpoints
@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(
    item_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all categories."""
    type_filter = None
    if item_type:
        try:
            type_filter = ItemType(item_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid item type")

    categories = get_categories(db, item_type=type_filter)
    return [
        CategoryResponse(
            id=cat.id,
            name=cat.name,
            item_type=cat.item_type,
            icon=cat.icon,
            color=cat.color,
            order=cat.order,
            items_count=get_category_items_count(db, cat.id),
            created_at=cat.created_at
        )
        for cat in categories
    ]


@router.post("/categories", response_model=CategoryResponse, status_code=201)
def create_new_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category."""
    cat = create_category(db, category)
    return CategoryResponse(
        id=cat.id,
        name=cat.name,
        item_type=cat.item_type,
        icon=cat.icon,
        color=cat.color,
        order=cat.order,
        items_count=0,
        created_at=cat.created_at
    )


@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_existing_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing category."""
    cat = update_category(db, category_id, category)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryResponse(
        id=cat.id,
        name=cat.name,
        item_type=cat.item_type,
        icon=cat.icon,
        color=cat.color,
        order=cat.order,
        items_count=get_category_items_count(db, cat.id),
        created_at=cat.created_at
    )


@router.delete("/categories/{category_id}")
def delete_existing_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a category."""
    if not delete_category(db, category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    return {"status": "deleted", "id": category_id}


@router.get("/items", response_model=list[ItemListResponse])
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    item_type: Optional[str] = None,
    category_id: Optional[int] = None,
    location_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all items with pagination."""
    type_filter = None
    if item_type:
        try:
            type_filter = ItemType(item_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid item type")

    items = get_items(db, skip=skip, limit=limit, item_type=type_filter, category_id=category_id, location_id=location_id)
    return [
        ItemListResponse(
            id=item.id,
            title=item.title,
            item_type=item.item_type,
            category_id=item.category_id,
            category=item.category,
            location_ids=[loc.id for loc in item.locations],
            locations=item.locations,
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
    category_id: Optional[int] = None,
    location_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Search items by title."""
    type_filter = None
    if item_type:
        try:
            type_filter = ItemType(item_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid item type")

    items = search_items(db, q, type_filter, category_id, location_id)
    return [
        {
            "id": item.id,
            "title": item.title,
            "item_type": item.item_type,
            "category_id": item.category_id,
            "category": {
                "id": item.category.id,
                "name": item.category.name,
                "icon": item.category.icon,
                "color": item.category.color
            } if item.category else None,
            "location_ids": [loc.id for loc in item.locations],
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
def get_incidents(
    category_id: Optional[int] = None,
    location_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all incidents with full data."""
    items = get_items_by_type(db, ItemType.INCIDENT, category_id, location_id)
    return [
        {
            "id": item.id,
            "title": item.title,
            "category_id": item.category_id,
            "category": {
                "id": item.category.id,
                "name": item.category.name,
                "icon": item.category.icon,
                "color": item.category.color
            } if item.category else None,
            "location_ids": [loc.id for loc in item.locations],
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
def get_instructions(
    category_id: Optional[int] = None,
    location_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all instructions with full data."""
    items = get_items_by_type(db, ItemType.INSTRUCTION, category_id, location_id)
    return [
        {
            "id": item.id,
            "title": item.title,
            "category_id": item.category_id,
            "category": {
                "id": item.category.id,
                "name": item.category.name,
                "icon": item.category.icon,
                "color": item.category.color
            } if item.category else None,
            "location_ids": [loc.id for loc in item.locations],
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
