"""CRUD operations for the knowledge base."""
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.models.models import Item, Page, Action, ItemType
from app.schemas import ItemCreate, ItemUpdate, ImportData


def get_items(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    item_type: Optional[ItemType] = None
) -> list[Item]:
    """Get all items with optional filtering."""
    query = db.query(Item)
    if item_type:
        query = query.filter(Item.item_type == item_type)
    return query.order_by(Item.updated_at.desc()).offset(skip).limit(limit).all()


def get_items_by_type(db: Session, item_type: ItemType) -> list[Item]:
    """Get all items of a specific type with full data."""
    return (
        db.query(Item)
        .options(joinedload(Item.pages).joinedload(Page.actions))
        .filter(Item.item_type == item_type)
        .order_by(Item.id)
        .all()
    )


def get_item(db: Session, item_id: int) -> Optional[Item]:
    """Get a single item by ID with all related data."""
    return (
        db.query(Item)
        .options(joinedload(Item.pages).joinedload(Page.actions))
        .filter(Item.id == item_id)
        .first()
    )


def search_items(
    db: Session,
    query: str,
    item_type: Optional[ItemType] = None
) -> list[Item]:
    """Search items by title."""
    search = f"%{query}%"
    q = db.query(Item).filter(Item.title.ilike(search))
    if item_type:
        q = q.filter(Item.item_type == item_type)
    return q.order_by(Item.title).all()


def create_item(db: Session, item_data: ItemCreate) -> Item:
    """Create a new item with pages and actions."""
    # Create main item
    db_item = Item(
        title=item_data.title,
        item_type=item_data.item_type
    )
    db.add(db_item)
    db.flush()  # Get the ID

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
        .options(joinedload(Item.pages).joinedload(Page.actions))
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
