"""CRUD operations for the knowledge base."""
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func

from app.models.models import Item, Page, Action, ItemType, Category, Location
from app.schemas import ItemCreate, ItemUpdate, ImportData, CategoryCreate, CategoryUpdate, LocationCreate, LocationUpdate


# Location CRUD
def get_locations(db: Session) -> list[Location]:
    """Get all locations."""
    return db.query(Location).order_by(Location.order, Location.name).all()


def get_location(db: Session, location_id: int) -> Optional[Location]:
    """Get a single location by ID."""
    return db.query(Location).filter(Location.id == location_id).first()


def get_location_by_code(db: Session, code: str) -> Optional[Location]:
    """Get a location by code."""
    return db.query(Location).filter(Location.code == code).first()


def create_location(db: Session, location_data: LocationCreate) -> Location:
    """Create a new location."""
    db_location = Location(**location_data.model_dump())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def update_location(db: Session, location_id: int, location_data: LocationUpdate) -> Optional[Location]:
    """Update a location."""
    db_location = db.query(Location).filter(Location.id == location_id).first()
    if not db_location:
        return None

    update_data = location_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_location, field, value)

    db.commit()
    db.refresh(db_location)
    return db_location


def delete_location(db: Session, location_id: int) -> bool:
    """Delete a location."""
    db_location = db.query(Location).filter(Location.id == location_id).first()
    if not db_location:
        return False
    db.delete(db_location)
    db.commit()
    return True


# Category CRUD
def get_categories(
    db: Session,
    item_type: Optional[ItemType] = None
) -> list[Category]:
    """Get all categories with item counts."""
    query = db.query(Category)
    if item_type:
        query = query.filter(Category.item_type == item_type)
    return query.order_by(Category.order, Category.name).all()


def get_category(db: Session, category_id: int) -> Optional[Category]:
    """Get a single category by ID."""
    return db.query(Category).filter(Category.id == category_id).first()


def create_category(db: Session, category_data: CategoryCreate) -> Category:
    """Create a new category."""
    db_category = Category(**category_data.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(db: Session, category_id: int, category_data: CategoryUpdate) -> Optional[Category]:
    """Update a category."""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        return None

    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)

    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int) -> bool:
    """Delete a category."""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        return False
    db.delete(db_category)
    db.commit()
    return True


def get_category_items_count(db: Session, category_id: int) -> int:
    """Get count of items in a category."""
    return db.query(func.count(Item.id)).filter(Item.category_id == category_id).scalar()


# Item CRUD


def get_items(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    item_type: Optional[ItemType] = None,
    category_id: Optional[int] = None,
    location_id: Optional[int] = None
) -> list[Item]:
    """Get all items with optional filtering."""
    query = db.query(Item).options(
        joinedload(Item.category),
        joinedload(Item.locations)
    )
    if item_type:
        query = query.filter(Item.item_type == item_type)
    if category_id is not None:
        query = query.filter(Item.category_id == category_id)
    if location_id is not None:
        query = query.filter(Item.locations.any(Location.id == location_id))
    return query.order_by(Item.updated_at.desc()).offset(skip).limit(limit).all()


def get_items_by_type(
    db: Session,
    item_type: ItemType,
    category_id: Optional[int] = None,
    location_id: Optional[int] = None
) -> list[Item]:
    """Get all items of a specific type with full data."""
    query = (
        db.query(Item)
        .options(
            joinedload(Item.pages).joinedload(Page.actions),
            joinedload(Item.category),
            joinedload(Item.locations)
        )
        .filter(Item.item_type == item_type)
    )
    if category_id is not None:
        query = query.filter(Item.category_id == category_id)
    if location_id is not None:
        query = query.filter(Item.locations.any(Location.id == location_id))
    return query.order_by(Item.id).all()


def get_item(db: Session, item_id: int) -> Optional[Item]:
    """Get a single item by ID with all related data."""
    return (
        db.query(Item)
        .options(
            joinedload(Item.pages).joinedload(Page.actions),
            joinedload(Item.category),
            joinedload(Item.locations)
        )
        .filter(Item.id == item_id)
        .first()
    )


def search_items(
    db: Session,
    query: str,
    item_type: Optional[ItemType] = None,
    category_id: Optional[int] = None,
    location_id: Optional[int] = None
) -> list[Item]:
    """Search items by title."""
    search = f"%{query}%"
    q = db.query(Item).options(
        joinedload(Item.category),
        joinedload(Item.locations)
    ).filter(Item.title.ilike(search))
    if item_type:
        q = q.filter(Item.item_type == item_type)
    if category_id is not None:
        q = q.filter(Item.category_id == category_id)
    if location_id is not None:
        q = q.filter(Item.locations.any(Location.id == location_id))
    return q.order_by(Item.title).all()


def create_item(db: Session, item_data: ItemCreate) -> Item:
    """Create a new item with pages and actions."""
    # Create main item
    db_item = Item(
        title=item_data.title,
        item_type=item_data.item_type,
        category_id=item_data.category_id
    )
    db.add(db_item)
    db.flush()  # Get the ID

    # Add locations if provided
    if item_data.location_ids:
        locations = db.query(Location).filter(Location.id.in_(item_data.location_ids)).all()
        db_item.locations = locations

    # Create pages
    for page_order, page_data in enumerate(item_data.pages):
        db_page = Page(
            item_id=db_item.id,
            title=page_data.title,
            time=page_data.time,
            image=page_data.image,
            order=page_order
        )
        db.add(db_page)
        db.flush()

        # Create actions
        for action_order, action_text in enumerate(page_data.actions):
            db_action = Action(
                page_id=db_page.id,
                text=action_text,
                order=action_order
            )
            db.add(db_action)

    db.commit()
    db.refresh(db_item)
    return get_item(db, db_item.id)


def update_item(db: Session, item_id: int, item_data: ItemUpdate) -> Optional[Item]:
    """Update an existing item."""
    # Load item with pages for proper cascade
    db_item = (
        db.query(Item)
        .options(
            joinedload(Item.pages).joinedload(Page.actions),
            joinedload(Item.locations)
        )
        .filter(Item.id == item_id)
        .first()
    )
    if not db_item:
        return None

    # Update basic fields
    if item_data.title is not None:
        db_item.title = item_data.title
    if item_data.item_type is not None:
        db_item.item_type = item_data.item_type
    if 'category_id' in item_data.model_fields_set:
        db_item.category_id = item_data.category_id

    # Update locations if provided
    if item_data.location_ids is not None:
        locations = db.query(Location).filter(Location.id.in_(item_data.location_ids)).all()
        db_item.locations = locations

    # Update pages if provided
    if item_data.pages is not None:
        # Clear existing pages (cascade deletes actions)
        db_item.pages.clear()
        db.flush()

        # Create new pages
        for page_order, page_data in enumerate(item_data.pages):
            db_page = Page(
                item_id=item_id,
                title=page_data.title,
                time=page_data.time,
                image=page_data.image,
                order=page_order
            )
            db.add(db_page)
            db.flush()

            # Create actions
            for action_order, action_text in enumerate(page_data.actions):
                db_action = Action(
                    page_id=db_page.id,
                    text=action_text,
                    order=action_order
                )
                db.add(db_action)

    db.commit()
    return get_item(db, item_id)


def delete_item(db: Session, item_id: int) -> bool:
    """Delete an item and all related data."""
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        return False
    db.delete(db_item)
    db.commit()
    return True


def export_all_items(db: Session) -> dict:
    """Export all items in the original JSON format."""
    incidents = get_items_by_type(db, ItemType.INCIDENT)
    instructions = get_items_by_type(db, ItemType.INSTRUCTION)

    def item_to_dict(item: Item) -> dict:
        return {
            "id": item.id,
            "title": item.title,
            "category_id": item.category_id,
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

    return {
        "incidents": [item_to_dict(i) for i in incidents],
        "instructions": [item_to_dict(i) for i in instructions]
    }


def bulk_import_items(db: Session, data: ImportData) -> dict:
    """Import items from JSON data."""
    imported = {"incidents": 0, "instructions": 0}

    # Import incidents
    for item_data in data.incidents:
        item = ItemCreate(
            title=item_data.title,
            item_type=ItemType.INCIDENT,
            pages=[
                {
                    "title": p.get("title", "Страница"),
                    "time": p.get("time", "5 минут"),
                    "image": p.get("image"),
                    "actions": p.get("actions", [])
                }
                for p in item_data.pages
            ]
        )
        create_item(db, item)
        imported["incidents"] += 1

    # Import instructions
    for item_data in data.instructions:
        item = ItemCreate(
            title=item_data.title,
            item_type=ItemType.INSTRUCTION,
            pages=[
                {
                    "title": p.get("title", "Страница"),
                    "time": p.get("time", "5 минут"),
                    "image": p.get("image"),
                    "actions": p.get("actions", [])
                }
                for p in item_data.pages
            ]
        )
        create_item(db, item)
        imported["instructions"] += 1

    return imported
