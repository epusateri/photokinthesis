"""API endpoints for photos and images."""

from flask import Blueprint, jsonify, current_app, request, send_file
from io import BytesIO
from photokinthesis.web.services.photo_service import PhotoService
from photokinthesis.web.services.xmp_service import XMPService


photos_bp = Blueprint('photos', __name__)


@photos_bp.route('/collections/<collection_name>/photos', methods=['GET'])
def list_photos(collection_name):
    """
    List photos in a collection with pagination.

    Args:
        collection_name: Name of the collection

    Query Parameters:
        offset: Pagination offset (default: 0)
        limit: Number of photos to return (default: 50)
        search: Search query string (optional)

    Returns:
        JSON response with photos list and pagination info
    """
    # Parse query parameters
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 50, type=int)
    search_query = request.args.get('search', '', type=str)

    # Validate pagination parameters
    if offset < 0:
        return jsonify({"error": "Offset must be >= 0"}), 400
    if limit < 1 or limit > 100:
        return jsonify({"error": "Limit must be between 1 and 100"}), 400

    photo_service = PhotoService(
        current_app.config['COLLECTION_XMP_DIR'],
        current_app.config['COLLECTION_IMAGE_DIR']
    )

    try:
        # If search query provided, get matching basenames
        search_basenames = None
        if search_query:
            xmp_service = XMPService(current_app.config['COLLECTION_XMP_DIR'])
            search_basenames = xmp_service.search_metadata(collection_name, search_query)

        # Get photos list
        result = photo_service.list_photos(
            collection_name,
            offset=offset,
            limit=limit,
            search_basenames=search_basenames
        )

        # Enhance with face counts
        xmp_service = XMPService(current_app.config['COLLECTION_XMP_DIR'])
        basenames = [p['basename'] for p in result['photos']]
        face_counts = xmp_service.get_face_counts(collection_name, basenames)

        # Add face information to photos
        for photo in result['photos']:
            face_count = face_counts.get(photo['basename'], 0)
            photo['face_count'] = face_count
            photo['has_faces'] = face_count > 0

        return jsonify(result)

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@photos_bp.route('/images/<collection_name>/<version>/<photo_type>/<filename>', methods=['GET'])
def serve_image(collection_name, version, photo_type, filename):
    """
    Serve an image file with optional resizing.

    Args:
        collection_name: Name of the collection
        version: Collection version
        photo_type: Type of photo ("enhanced_fronts", "fronts", "backs")
        filename: Image filename

    Query Parameters:
        size: Image size ("thumb", "medium", "full"; default: "full")

    Returns:
        Image binary data with appropriate Content-Type
    """
    size = request.args.get('size', 'full', type=str)

    # Validate size parameter
    if size not in ['thumb', 'medium', 'full']:
        return jsonify({"error": "Invalid size parameter"}), 400

    photo_service = PhotoService(
        current_app.config['COLLECTION_XMP_DIR'],
        current_app.config['COLLECTION_IMAGE_DIR']
    )

    try:
        # Get validated image path
        image_path = photo_service.get_image_path(
            collection_name,
            version,
            photo_type,
            filename
        )

        # Serve image with optional resizing
        image_data = photo_service.serve_image(image_path, size)

        return send_file(
            BytesIO(image_data),
            mimetype='image/jpeg',
            as_attachment=False
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
