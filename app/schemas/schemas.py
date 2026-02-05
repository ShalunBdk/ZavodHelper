"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.models import ItemType


# Action schemas
class ActionBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    order: int = 0


class ActionCreate(ActionBase):
    pass


class ActionResponse(ActionBase):
    id: int
    page_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Page schemas
class PageBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    time: str = Field(default="5 минут", max_length=50)
    image: Optional[str] = None
    order: int = 0


class PageCreate(PageBase):
    actions: list[str] = Field(default_factory=list)


class PageResponse(PageBase):
    id: int
    item_id: int
    actions: list[ActionResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Item schemas
class ItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    item_type: ItemType


class ItemCreate(ItemBase):
    pages: list[PageCreate] = Field(default_factory=list)


class ItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    item_type: Optional[ItemType] = None
    pages: Optional[list[PageCreate]] = None


class ItemResponse(ItemBase):
    id: int
    pages: list[PageResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ItemListResponse(BaseModel):
    id: int
    title: str
    item_type: ItemType
    pages_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Export/Import schemas
class ExportItem(BaseModel):
    id: int
    title: str
    pages: list[dict]


class ExportData(BaseModel):
    incidents: list[ExportItem] = []
    instructions: list[ExportItem] = []


class ImportItem(BaseModel):
    id: Optional[int] = None
    title: str
    pages: list[dict]


class ImportData(BaseModel):
    incidents: list[ImportItem] = []
    instructions: list[ImportItem] = []
