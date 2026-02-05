"""SQLAlchemy models for the knowledge base."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class ItemType(str, enum.Enum):
    """Type of knowledge base item."""
    INCIDENT = "incident"
    INSTRUCTION = "instruction"


class Item(Base):
    """Main entity: Incident or Instruction."""
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    item_type = Column(Enum(ItemType), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
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
