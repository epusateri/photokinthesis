export default function MetadataPanel({ metadata }) {
  if (!metadata) {
    return <div className="metadata-panel">Loading metadata...</div>
  }

  return (
    <div className="metadata-panel">
      <h3>Metadata</h3>
      {Object.keys(metadata.metadata).length > 0 ? (
        <dl className="metadata-list">
          {Object.entries(metadata.metadata).map(([key, value]) => (
            <div key={key} className="metadata-item">
              <dt>{key}</dt>
              <dd>{value}</dd>
            </div>
          ))}
        </dl>
      ) : (
        <p>No metadata available</p>
      )}

      {metadata.faces && metadata.faces.length > 0 && (
        <>
          <h3>Detected Faces ({metadata.faces.length})</h3>
          <ul className="face-list">
            {metadata.faces.map((face, idx) => (
              <li key={idx}>
                {face.name}
                <span className="face-coords">
                  {' '}(x: {face.area.x.toFixed(3)}, y: {face.area.y.toFixed(3)})
                </span>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  )
}
