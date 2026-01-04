import { useState } from 'react'

export default function SearchFilter({ onSearch }) {
  const [query, setQuery] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    onSearch(query)
  }

  return (
    <div className="search-filter">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Search metadata..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit">Search</button>
        {query && (
          <button
            type="button"
            onClick={() => {
              setQuery('')
              onSearch('')
            }}
          >
            Clear
          </button>
        )}
      </form>
    </div>
  )
}
