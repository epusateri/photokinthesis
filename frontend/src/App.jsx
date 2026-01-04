import { useState } from 'react'
import CollectionSelector from './components/CollectionSelector'
import PhotoGrid from './components/PhotoGrid'
import PhotoDetail from './components/PhotoDetail'
import SearchFilter from './components/SearchFilter'
import { useCollections } from './hooks/useCollections'
import './styles/main.css'

function App() {
  const [selectedCollection, setSelectedCollection] = useState(null)
  const [selectedPhoto, setSelectedPhoto] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const { collections, loading } = useCollections()

  return (
    <div className="app">
      <header className="app-header">
        <h1>Photokinthesis</h1>
        <div className="app-controls">
          <CollectionSelector
            collections={collections}
            selected={selectedCollection}
            onChange={setSelectedCollection}
          />
          {selectedCollection && (
            <SearchFilter onSearch={setSearchQuery} />
          )}
        </div>
      </header>

      <main className="app-main">
        {loading ? (
          <div className="app-loading">Loading collections...</div>
        ) : (
          <PhotoGrid
            collection={selectedCollection}
            searchQuery={searchQuery}
            onPhotoClick={setSelectedPhoto}
          />
        )}
      </main>

      {selectedPhoto && (
        <PhotoDetail
          photo={selectedPhoto}
          collection={selectedCollection}
          onClose={() => setSelectedPhoto(null)}
        />
      )}
    </div>
  )
}

export default App
