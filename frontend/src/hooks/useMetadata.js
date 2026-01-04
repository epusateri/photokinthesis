import { useState, useEffect } from 'react'
import { fetchMetadata } from '../services/api'

export function useMetadata(collectionName, basename) {
  const [metadata, setMetadata] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!collectionName || !basename) {
      setMetadata(null)
      return
    }

    setLoading(true)
    fetchMetadata(collectionName, basename)
      .then(data => {
        setMetadata(data)
        setLoading(false)
      })
      .catch(err => {
        setError(err)
        setLoading(false)
      })
  }, [collectionName, basename])

  return { metadata, loading, error }
}
