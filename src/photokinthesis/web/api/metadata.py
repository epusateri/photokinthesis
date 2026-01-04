"""API endpoints for photo metadata."""

from flask import Blueprint, jsonify, current_app
from photokinthesis.web.services.xmp_service import XMPService


metadata_bp = Blueprint('metadata', __name__)


@metadata_bp.route('/collections/<collection_name>/photos/<basename>/metadata', methods=['GET'])
def get_photo_metadata(collection_name, basename):
    """
    Get XMP metadata and face regions for a photo.

    Args:
        collection_name: Name of the collection
        basename: Photo basename (without extension)

    Returns:
        JSON response with metadata and faces
    """
    service = XMPService(current_app.config['COLLECTION_XMP_DIR'])

    try:
        metadata = service.get_photo_metadata(collection_name, basename)
        return jsonify(metadata)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
