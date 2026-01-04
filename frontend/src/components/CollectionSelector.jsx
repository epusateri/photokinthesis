export default function CollectionSelector({ collections, selected, onChange }) {
  return (
    <div className="collection-selector">
      <label htmlFor="collection-select">Collection: </label>
      <select
        id="collection-select"
        value={selected?.name || ''}
        onChange={(e) => {
          const collection = collections.find(c => c.name === e.target.value)
          onChange(collection)
        }}
      >
        <option value="">Select a collection...</option>
        {collections.map(collection => (
          <option key={collection.name} value={collection.name}>
            {collection.name} ({collection.photo_count} photos)
          </option>
        ))}
      </select>
    </div>
  )
}
