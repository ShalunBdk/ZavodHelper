"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.models import ItemType


# Category schemas
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    item_type: ItemType
    icon: str = Field(default="📁", max_length=50)
    color: str = Field(default="#3498db", max_length=20)
    order: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=20)
    order: Optional[int] = None


class CategoryResponse(CategoryBase):
    id: int
    items_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


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
    category_id: Optional[int] = None


class ItemCreate(ItemBase):
    pages: list[PageCreate] = Field(default_factory=list)


class ItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    item_type: Optional[ItemType] = None
    category_id: Optional[int] = None
    pages: Optional[list[PageCreate]] = None


class CategoryInfo(BaseModel):
    id: int
    name: str
    icon: str
    color: str

    class Config:
        from_attributes = True


class ItemResponse(ItemBase):
    id: int
    pages: list[PageResponse] = []
    category: Optional[CategoryInfo] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ItemListResponse(BaseModel):
    id: int
    title: str
    item_type: ItemType
    category_id: Optional[int] = None
    category: Optional[CategoryInfo] = None
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
