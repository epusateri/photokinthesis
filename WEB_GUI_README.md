# Photokinthesis Web GUI

A Flask + React web interface for browsing photo collections with metadata and face detection visualization.

## Features

- Browse multiple photo collections
- View photos in a responsive grid layout
- Display face detection bounding boxes overlaid on images
- View XMP metadata for each photo
- Search photos by metadata content
- Pagination support for large collections

## Quick Start

### 1. Build the Frontend (First Time Only)

You need Node.js and npm installed to build the React frontend.

```bash
cd frontend
npm install
npm run build
```

Or use the build script:

```bash
./scripts/build_frontend.sh
```

This will:
- Install npm dependencies
- Build the React app for production
- Copy the built files to `src/photokinthesis/web/static/`

### 2. Start the Server

```bash
photokinthesis serve \
  --collection-xmp-dir ./collections \
  --collection-image-dir ./images \
  --port 5000
```

Then open your browser to: http://localhost:5000

## Architecture

### Backend (Flask)

```
src/photokinthesis/web/
├── app.py              # Flask application factory
├── api/                # API endpoints
│   ├── collections.py  # GET /api/collections
│   ├── photos.py       # GET /api/collections/{name}/photos
│   │                   # GET /api/images/{collection}/{version}/{type}/{filename}
│   └── metadata.py     # GET /api/collections/{name}/photos/{basename}/metadata
└── services/           # Business logic
    ├── collection_service.py
    ├── photo_service.py
    └── xmp_service.py
```

### Frontend (React + Vite)

```
frontend/src/
├── App.jsx                        # Main application component
├── components/
│   ├── CollectionSelector.jsx    # Collection dropdown
│   ├── PhotoGrid.jsx              # Photo grid layout
│   ├── PhotoCard.jsx              # Individual photo card
│   ├── PhotoDetail.jsx            # Full-size photo modal
│   ├── MetadataPanel.jsx          # Metadata display
│   ├── FaceBoundingBox.jsx        # Face overlay rendering
│   └── SearchFilter.jsx           # Search input
├── hooks/
│   ├── useCollections.js          # Fetch collections
│   ├── usePhotos.js               # Fetch photos with pagination
│   └── useMetadata.js             # Fetch photo metadata
└── services/
    └── api.js                     # API client
```

## API Endpoints

### Collections

```
GET /api/collections
```

Response:
```json
{
  "collections": [
    {
      "name": "phase_0_tiny",
      "version": "0000",
      "photo_count": 788,
      "xmp_path": "/path/to/collections/phase_0_tiny",
      "image_path": "/path/to/images/phase_0_tiny/0000"
    }
  ]
}
```

### Photos

```
GET /api/collections/{collection_name}/photos?offset=0&limit=50&search=query
```

Response:
```json
{
  "photos": [
    {
      "filename": "More_Grandma_Ellen__0001.jpg",
      "basename": "More_Grandma_Ellen__0001",
      "thumbnail_url": "/api/images/.../...?size=thumb",
      "full_url": "/api/images/.../...",
      "has_xmp": true,
      "has_faces": true,
      "face_count": 1
    }
  ],
  "total": 788,
  "offset": 0,
  "limit": 50
}
```

### Metadata

```
GET /api/collections/{collection_name}/photos/{basename}/metadata
```

Response:
```json
{
  "basename": "More_Grandma_Ellen__0001",
  "xmp_path": "/path/to/collections/phase_0_tiny/More_Grandma_Ellen__0001.xmp",
  "metadata": {
    "dc:source": "Ellen (Deichler) Pusateri"
  },
  "faces": [
    {
      "name": "Unknown",
      "type": "Face",
      "area": {
        "x": 0.532909,
        "y": 0.364185,
        "w": 0.131635,
        "h": 0.124748,
        "unit": "normalized"
      }
    }
  ]
}
```

### Images

```
GET /api/images/{collection}/{version}/{type}/{filename}?size=thumb|medium|full
```

- `size=thumb`: 300x300px thumbnail
- `size=medium`: 800x800px thumbnail
- `size=full`: Original image (default)

## Development

### Run Backend and Frontend Separately

#### Terminal 1: Flask backend

```bash
photokinthesis serve \
  --collection-xmp-dir ./collections \
  --collection-image-dir ./images \
  --debug
```

#### Terminal 2: React dev server with hot reload

```bash
cd frontend
npm run dev
```

The Vite dev server runs on http://localhost:3000 and proxies API requests to Flask on port 5000.

## Face Bounding Box Rendering

Face regions are stored in XMP files using normalized coordinates (0-1 range):
- `x`, `y`: Center point of face
- `w`, `h`: Width and height

The frontend converts these to pixel coordinates:

```javascript
const left = (face.area.x - face.area.w / 2) * imageWidth
const top = (face.area.y - face.area.h / 2) * imageHeight
const width = face.area.w * imageWidth
const height = face.area.h * imageHeight
```

## Security

### Path Traversal Prevention

All image serving endpoints validate paths to prevent directory traversal attacks:

```python
def validate_path(base_dir: Path, *parts: str) -> Path:
    resolved = (base_dir / Path(*parts)).resolve()
    if not resolved.is_relative_to(base_dir.resolve()):
        raise ValueError("Invalid path")
    return resolved
```

### CORS

CORS is enabled for development. For production, configure allowed origins in `web/app.py`.

## Troubleshooting

### Frontend not displaying

If you see a placeholder message instead of the React app:

1. Make sure you've built the frontend: `./scripts/build_frontend.sh`
2. Check that files exist in `src/photokinthesis/web/static/`

### API returns empty collections

Make sure:
1. `--collection-xmp-dir` points to the correct directory
2. Each collection directory contains a `VERSION` file
3. XMP files (*.xmp) exist in the collection directory

### Images not loading

Make sure:
1. `--collection-image-dir` points to the correct directory
2. The directory structure is: `{collection_name}/{version}/enhanced_fronts/*.jpg`

### Face bounding boxes misaligned

This happens if the image displayed is a different size than the natural image. The component uses `naturalWidth` and `naturalHeight` to ensure correct scaling.
