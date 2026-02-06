"""Image upload and processing routes."""
import uuid
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image

from app.config import UPLOAD_DIR, MAX_UPLOAD_SIZE, ALLOWED_EXTENSIONS

router = APIRouter(prefix="/api", tags=["Upload"])

# Image settings
MAX_WIDTH = 800
MAX_HEIGHT = 600
WEBP_QUALITY = 80


def process_image(image_data: bytes) -> bytes:
    """Convert image to WebP and resize if needed."""
    img = Image.open(BytesIO(image_data))

    # Convert to RGB if necessary (for PNG with transparency)
    if img.mode in ('RGBA', 'P'):
        # Create white background
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[3] if len(img.split()) == 4 else None)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # Resize if too large
    if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
        img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.Resampling.LANCZOS)

    # Save as WebP
    output = BytesIO()
    img.save(output, format='WEBP', quality=WEBP_QUALITY, optimize=True)
    return output.getvalue()


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload and process an image."""
    # Check file extension
    if file.filename:
        ext = file.filename.rsplit('.', 1)[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Use: {', '.join(ALLOWED_EXTENSIONS)}"
            )

    # Read file
    content = await file.read()

    # Check size
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {MAX_UPLOAD_SIZE // 1024 // 1024}MB"
        )

    try:
        # Process image
        processed = process_image(content)

        # Generate unique filename
        filename = f"{uuid.uuid4().hex}.webp"
        filepath = UPLOAD_DIR / filename

        # Ensure upload directory exists
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        # Save file
        with open(filepath, 'wb') as f:
            f.write(processed)

        return {
            "url": f"uploads/{filename}",
            "filename": filename,
            "size": len(processed)
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process image: {str(e)}")
