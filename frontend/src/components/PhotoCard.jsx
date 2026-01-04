export default function PhotoCard({ photo, onClick }) {
  return (
    <div className="photo-card" onClick={onClick}>
      <div className="photo-card-image-container">
        <img
          src={photo.thumbnail_url}
          alt={photo.basename}
          loading="lazy"
        />
      </div>
      <div className="photo-card-info">
        <span className="photo-filename">{photo.filename}</span>
        {photo.face_count > 0 && (
          <span className="face-count">{photo.face_count} face(s)</span>
        )}
      </div>
    </div>
  )
}
