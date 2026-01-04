import PhotoCard from './PhotoCard'
import { usePhotos } from '../hooks/usePhotos'

export default function PhotoGrid({ collection, searchQuery, onPhotoClick }) {
  const { photos, total, loading, error } = usePhotos(collection?.name, searchQuery)

  if (!collection) {
    return (
      <div className="photo-grid-placeholder">
        <p>Select a collection to view photos</p>
      </div>
    )
  }

  if (loading) {
    return <div className="photo-grid-loading">Loading photos...</div>
  }

  if (error) {
    return <div className="photo-grid-error">Error loading photos: {error.message}</div>
  }

  if (photos.length === 0) {
    return <div className="photo-grid-empty">No photos found</div>
  }

  return (
    <div className="photo-grid-container">
      <div className="photo-grid-header">
        <p>Showing {photos.length} of {total} photos</p>
      </div>
      <div className="photo-grid">
        {photos.map(photo => (
          <PhotoCard
            key={photo.basename}
            photo={photo}
            onClick={() => onPhotoClick(photo)}
          />
        ))}
      </div>
    </div>
  )
}
