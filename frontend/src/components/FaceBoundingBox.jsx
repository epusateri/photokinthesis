export default function FaceBoundingBox({ face, imageWidth, imageHeight }) {
  // Convert normalized coordinates to pixel coordinates
  // face.area.x, face.area.y are center points
  // face.area.w, face.area.h are width/height

  const left = (face.area.x - face.area.w / 2) * imageWidth
  const top = (face.area.y - face.area.h / 2) * imageHeight
  const width = face.area.w * imageWidth
  const height = face.area.h * imageHeight

  return (
    <div
      className="face-bounding-box"
      style={{
        position: 'absolute',
        left: `${left}px`,
        top: `${top}px`,
        width: `${width}px`,
        height: `${height}px`,
        border: '2px solid #00ff00',
        boxSizing: 'border-box',
        pointerEvents: 'none',
      }}
    >
      {face.name && face.name !== 'Unknown' && (
        <span
          className="face-label"
          style={{
            position: 'absolute',
            top: '-20px',
            left: '0',
            background: 'rgba(0, 255, 0, 0.8)',
            color: 'white',
            padding: '2px 6px',
            fontSize: '12px',
            borderRadius: '3px',
          }}
        >
          {face.name}
        </span>
      )}
    </div>
  )
}
