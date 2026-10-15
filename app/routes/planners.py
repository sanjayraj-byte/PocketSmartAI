from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import json
from app.services.recommender import generate_recommendations

router = APIRouter(tags=["planners"])
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024

@router.post("/generate-{planner}")
async def generate_planner(
    planner: str,
    budget: float = Form(...),
    currency: str = Form("INR"),
    preferences: str = Form(""),
    location: str = Form("India"),
    details: str = Form("{}"),
    image: Optional[UploadFile] = File(None),
):
    if planner not in {"home", "party", "jewelry"}:
        raise HTTPException(status_code=404, detail="Unknown planner.")
    if budget <= 0 or budget > 100000000:
        raise HTTPException(status_code=422, detail="Budget must be greater than zero.")
    try:
        details_data = json.loads(details or "{}")
        if not isinstance(details_data, dict):
            raise ValueError()
    except (ValueError, json.JSONDecodeError):
        raise HTTPException(status_code=422, detail="Details must be a JSON object.")
    image_bytes, image_mime = None, None
    if image and image.filename:
        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=415, detail="Upload a JPG, PNG, or WEBP image.")
        image_bytes = await image.read()
        if len(image_bytes) > MAX_IMAGE_BYTES:
            raise HTTPException(status_code=413, detail="Image must be 5 MB or smaller.")
        image_mime = image.content_type
    result = await generate_recommendations(
        planner=planner, budget=budget, currency=currency,
        preferences=preferences, location=location, details=details_data,
        image_bytes=image_bytes, image_mime=image_mime
    )
    return result
