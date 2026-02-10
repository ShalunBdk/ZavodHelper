"""SQLAlchemy models for the knowledge base."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, Table
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class ItemType(str, enum.Enum):
    """Type of knowledge base item."""
    INCIDENT = "incident"
    INSTRUCTION = "instruction"


# Association table for many-to-many relationship between items and locations
item_locations = Table(
    'item_locations',
    Base.metadata,
    Column('item_id', Integer, ForeignKey('items.id', ondelete='CASCADE'), primary_key=True),
    Column('location_id', Integer, ForeignKey('locations.id', ondelete='CASCADE'), primary_key=True)
)


class Location(Base):
    """Location where items are applicable (e.g., ПУ-1, ПУ-2)."""
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(20), nullable=False, unique=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    items = relationship("Item", secondary=item_locations, back_populates="locations")

    def __repr__(self):
        return f"<Location(id={self.id}, code='{self.code}', name='{self.name}')>"


class Category(Base):
    """Category for grouping items."""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    item_type = Column(Enum(ItemType), nullable=False, index=True)
    icon = Column(String(50), default="📁")
    color = Column(String(20), default="#3498db")
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    items = relationship("Item", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', type={self.item_type})>"


class Item(Base):
    """Main entity: Incident or Instruction."""
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    item_type = Column(Enum(ItemType), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("Category", back_populates="items")
    locations = relationship("Location", secondary=item_locations, back_populates="items")
    pages = relationship(
        "Page",
        back_populates="item",
        cascade="all, delete-orphan",
        order_by="Page.order"
    )

    def __repr__(self):
        return f"<Item(id={self.id}, title='{self.title}', type={self.item_type})>"


class Page(Base):
    """Page within an Item (step in the process)."""
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    time = Column(String(50), default="5 минут")
    image = Column(Text, nullable=True)  # URL or base64
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    item = relationship("Item", back_populates="pages")
    actions = relationship(
        "Action",
        back_populates="page",
        cascade="all, delete-orphan",
        order_by="Action.order"
    )

    def __repr__(self):
        return f"<Page(id={self.id}, title='{self.title}')>"


class Action(Base):
    """Action step within a Page."""
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    page = relationship("Page", back_populates="actions")

    def __repr__(self):
        return f"<Action(id={self.id}, text='{self.text[:30]}...')>"
