import { useState, useEffect } from 'react'
import { fetchPhotos } from '../services/api'

export function usePhotos(collectionName, searchQuery = '', offset = 0, limit = 50) {
  const [photos, setPhotos] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!collectionName) {
      setPhotos([])
      setTotal(0)
      return
    }

    setLoading(true)
    fetchPhotos(collectionName, { offset, limit, search: searchQuery })
      .then(data => {
        setPhotos(data.photos)
        setTotal(data.total)
        setLoading(false)
      })
      .catch(err => {
        setError(err)
        setLoading(false)
      })
  }, [collectionName, searchQuery, offset, limit])

  return { photos, total, loading, error }
}
