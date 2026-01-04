"""API endpoints for collections."""

from flask import Blueprint, jsonify, current_app
from photokinthesis.web.services.collection_service import CollectionService


collections_bp = Blueprint('collections', __name__)


@collections_bp.route('/collections', methods=['GET'])
def list_collections():
    """
    List all available collections.

    Returns:
        JSON response with list of collections
    """
    service = CollectionService(
        current_app.config['COLLECTION_XMP_DIR'],
        current_app.config['COLLECTION_IMAGE_DIR']
    )

    try:
        collections = service.list_collections()
        return jsonify({
            "collections": [c.to_dict() for c in collections]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@collections_bp.route('/collections/<collection_name>', methods=['GET'])
def get_collection(collection_name):
    """
    Get details about a specific collection.

    Args:
        collection_name: Name of the collection

    Returns:
        JSON response with collection details
    """
    service = CollectionService(
        current_app.config['COLLECTION_XMP_DIR'],
        current_app.config['COLLECTION_IMAGE_DIR']
    )

    try:
        collection = service.get_collection_info(collection_name)
        if collection is None:
            return jsonify({"error": "Collection not found"}), 404

        return jsonify(collection.to_dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
