"""Flask application factory for photokinthesis web GUI."""

from flask import Flask, send_from_directory
from flask_cors import CORS
from pathlib import Path
import os


def create_app(collection_xmp_dir: Path, collection_image_dir: Path):
    """
    Create and configure the Flask application.

    Args:
        collection_xmp_dir: Root directory for collection XMP files
        collection_image_dir: Root directory for collection image files

    Returns:
        Configured Flask application instance
    """
    # Determine static folder path
    static_folder = Path(__file__).parent / 'static'

    app = Flask(
        __name__,
        static_folder=str(static_folder),
        static_url_path=''
    )

    # Enable CORS for development
    CORS(app)

    # Store configuration
    app.config['COLLECTION_XMP_DIR'] = Path(collection_xmp_dir)
    app.config['COLLECTION_IMAGE_DIR'] = Path(collection_image_dir)

    # Register API blueprints
    from photokinthesis.web.api.collections import collections_bp
    from photokinthesis.web.api.photos import photos_bp
    from photokinthesis.web.api.metadata import metadata_bp

    app.register_blueprint(collections_bp, url_prefix='/api')
    app.register_blueprint(photos_bp, url_prefix='/api')
    app.register_blueprint(metadata_bp, url_prefix='/api')

    # Serve React app for non-API routes
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_react(path):
        """Serve React static files or index.html."""
        static_path = Path(static_folder)

        # If static folder doesn't exist or is empty, show placeholder
        if not static_path.exists() or not any(static_path.iterdir()):
            return """
            <html>
                <head><title>Photokinthesis</title></head>
                <body style="font-family: sans-serif; padding: 40px;">
                    <h1>Photokinthesis Web GUI</h1>
                    <p>The React frontend hasn't been built yet.</p>
                    <p>To build the frontend:</p>
                    <pre style="background: #f0f0f0; padding: 15px; border-radius: 5px;">
cd frontend
npm install
npm run build
cp -r dist/* ../src/photokinthesis/web/static/
                    </pre>
                    <p>The API is running at <a href="/api/collections">/api/collections</a></p>
                </body>
            </html>
            """, 200

        # Check if requested file exists
        file_path = static_path / path
        if file_path.exists() and file_path.is_file():
            return send_from_directory(str(static_path), path)

        # Otherwise serve index.html (for client-side routing)
        index_path = static_path / 'index.html'
        if index_path.exists():
            return send_from_directory(str(static_path), 'index.html')

        return "Not found", 404

    return app
