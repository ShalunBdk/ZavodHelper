"""HTML page routes."""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import ItemType
from app.crud import get_items_by_type, export_all_items

templates = Jinja2Templates(directory="templates")

router = APIRouter(tags=["Pages"])


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    """Main page - view incidents and instructions."""
    data = export_all_items(db)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "incidents": data["incidents"],
            "instructions": data["instructions"]
        }
    )


@router.get("/editor", response_class=HTMLResponse)
async def editor(request: Request, db: Session = Depends(get_db)):
    """Editor page - create and edit items."""
    data = export_all_items(db)
    return templates.TemplateResponse(
        "editor.html",
        {
            "request": request,
            "incidents": data["incidents"],
            "instructions": data["instructions"]
        }
    )
