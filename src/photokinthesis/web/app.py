"""
FastAPI application for photokinthesis.

This module sets up a web server with:
- API endpoints for loading and viewing collections
- Static file serving for JavaScript/CSS
- HTML template serving
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from photokinthesis.collection import Collection

# Create the FastAPI application
app = FastAPI(title="Photokinthesis")

# Get the directory where this file lives
WEB_DIR = Path(__file__).parent

# Store the currently loaded collection in memory
current_collection: Collection | None = None
current_collection_path: str | None = None

# Mount the static files directory
# This means any request to /static/... will serve files from the static/ folder
app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")


class LoadCollectionRequest(BaseModel):
    """Request body for loading a collection."""
    path: str


class OrientationUpdateRequest(BaseModel):
    """Request body for updating image orientation."""
    image_type: str  # 'front', 'back', or 'enhanced_front'
    orientation: int  # 0, 90, 180, or 270


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main HTML page."""
    html_path = WEB_DIR / "templates" / "index.html"
    return html_path.read_text()


@app.get("/thumbnails", response_class=HTMLResponse)
async def thumbnails():
    """Serve the thumbnails page."""
    html_path = WEB_DIR / "templates" / "thumbnails.html"
    return html_path.read_text()


@app.post("/api/collection/load")
async def load_collection(request: LoadCollectionRequest):
    """
    Load a collection from a directory path.

    The directory should contain a collection.json file and images subdirectory.
    """
    global current_collection, current_collection_path

    collection_path = Path(request.path)
    if not collection_path.exists():
        raise HTTPException(status_code=404, detail=f"Directory not found: {request.path}")

    if not (collection_path / "collection.json").exists():
        raise HTTPException(status_code=400, detail="No collection.json found in directory")

    current_collection = Collection.read(collection_path)
    current_collection_path = request.path

    return {
        "name": current_collection.name,
        "path": current_collection_path,
        "photo_count": len(current_collection.photos),
    }


@app.get("/api/collection")
async def get_collection():
    """
    Get metadata about the currently loaded collection.

    Returns the collection name, path, and list of photo IDs.
    """
    if current_collection is None:
        raise HTTPException(status_code=400, detail="No collection loaded")

    return {
        "name": current_collection.name,
        "path": current_collection_path,
        "photos": [{"id": photo.id} for photo in current_collection.photos],
    }


def get_photo_or_404(photo_id: str):
    """Helper to find a photo by ID or raise 404."""
    if current_collection is None:
        raise HTTPException(status_code=400, detail="No collection loaded")

    for photo in current_collection.photos:
        if photo.id == photo_id:
            return photo

    raise HTTPException(status_code=404, detail=f"Photo not found: {photo_id}")


@app.get("/photo/{photo_id}", response_class=HTMLResponse)
async def photo_detail_page(photo_id: str):
    """Serve the photo detail HTML page."""
    get_photo_or_404(photo_id)  # Verify photo exists
    html_path = WEB_DIR / "templates" / "photo.html"
    return html_path.read_text()


@app.get("/api/photos/{photo_id}")
async def get_photo(photo_id: str):
    """
    Get metadata for a specific photo.

    Returns the photo ID, source filenames, which images are available,
    and IDs of previous/next photos for navigation.
    """
    photo = get_photo_or_404(photo_id)

    # Find previous and next photo IDs
    prev_id = None
    next_id = None
    photos = current_collection.photos
    for i, p in enumerate(photos):
        if p.id == photo_id:
            if i > 0:
                prev_id = photos[i - 1].id
            if i < len(photos) - 1:
                next_id = photos[i + 1].id
            break

    return {
        "id": photo.id,
        "source_filenames": photo.source_filenames,
        "has_front": photo.images.front is not None,
        "has_back": photo.images.back is not None,
        "has_enhanced_front": photo.images.enhanced_front is not None,
        "has_thumbnail": photo.images.thumbnail is not None,
        "front_orientation": photo.images.front_orientation,
        "back_orientation": photo.images.back_orientation,
        "enhanced_front_orientation": photo.images.enhanced_front_orientation,
        "prev_id": prev_id,
        "next_id": next_id,
    }


@app.get("/api/photos/{photo_id}/thumbnail")
async def get_thumbnail(photo_id: str):
    """Get the thumbnail image for a specific photo."""
    photo = get_photo_or_404(photo_id)

    if photo.images.thumbnail is None:
        raise HTTPException(status_code=404, detail="Photo has no thumbnail")
    return Response(content=photo.images.thumbnail, media_type="image/jpeg")


@app.get("/api/photos/{photo_id}/front")
async def get_front(photo_id: str):
    """Get the front image for a specific photo."""
    photo = get_photo_or_404(photo_id)

    if photo.images.front is None:
        raise HTTPException(status_code=404, detail="Photo has no front image")
    return Response(content=photo.images.front, media_type="image/jpeg")


@app.get("/api/photos/{photo_id}/back")
async def get_back(photo_id: str):
    """Get the back image for a specific photo."""
    photo = get_photo_or_404(photo_id)

    if photo.images.back is None:
        raise HTTPException(status_code=404, detail="Photo has no back image")
    return Response(content=photo.images.back, media_type="image/jpeg")


@app.get("/api/photos/{photo_id}/enhanced_front")
async def get_enhanced_front(photo_id: str):
    """Get the enhanced front image for a specific photo."""
    photo = get_photo_or_404(photo_id)

    if photo.images.enhanced_front is None:
        raise HTTPException(status_code=404, detail="Photo has no enhanced front image")
    return Response(content=photo.images.enhanced_front, media_type="image/jpeg")


@app.patch("/api/photos/{photo_id}/orientation")
async def update_orientation(photo_id: str, request: OrientationUpdateRequest):
    """Update the orientation of a specific image in memory."""
    photo = get_photo_or_404(photo_id)

    try:
        photo.set_orientation(request.image_type, request.orientation)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "ok"}


@app.post("/api/collection/save")
async def save_collection():
    """Save the current collection to disk."""
    if current_collection is None or current_collection_path is None:
        raise HTTPException(status_code=400, detail="No collection loaded")

    current_collection.write(Path(current_collection_path))
    return {"status": "ok"}
