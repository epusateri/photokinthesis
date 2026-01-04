import { useState, useRef, useEffect } from 'react'
import { useMetadata } from '../hooks/useMetadata'
import FaceBoundingBox from './FaceBoundingBox'
import MetadataPanel from './MetadataPanel'

export default function PhotoDetail({ photo, collection, onClose }) {
  const { metadata, loading, error } = useMetadata(collection?.name, photo?.basename)
  const imgRef = useRef(null)
  const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 })

  useEffect(() => {
    if (imgRef.current && imgRef.current.complete) {
      setImageDimensions({
        width: imgRef.current.naturalWidth,
        height: imgRef.current.naturalHeight,
      })
    }
  }, [metadata])

  const handleImageLoad = () => {
    if (imgRef.current) {
      setImageDimensions({
        width: imgRef.current.naturalWidth,
        height: imgRef.current.naturalHeight,
      })
    }
  }

  if (!photo) return null

  return (
    <div className="photo-detail-overlay" onClick={onClose}>
      <div className="photo-detail" onClick={(e) => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>
          ×
        </button>

        <div className="photo-detail-content">
          <div className="photo-detail-image-container">
            <div style={{ position: 'relative', display: 'inline-block' }}>
              <img
                ref={imgRef}
                src={photo.full_url}
                alt={photo.basename}
                onLoad={handleImageLoad}
                style={{ maxWidth: '100%', height: 'auto', display: 'block' }}
              />
              {metadata?.faces && imageDimensions.width > 0 && (
                <div
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                  }}
                >
                  {metadata.faces.map((face, idx) => (
                    <FaceBoundingBox
                      key={idx}
                      face={face}
                      imageWidth={imageDimensions.width}
                      imageHeight={imageDimensions.height}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="photo-detail-sidebar">
            <h2>{photo.filename}</h2>
            {loading && <p>Loading metadata...</p>}
            {error && <p>Error loading metadata: {error.message}</p>}
            {metadata && <MetadataPanel metadata={metadata} />}
          </div>
        </div>
      </div>
    </div>
  )
}
