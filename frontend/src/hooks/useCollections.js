import { useState, useEffect } from 'react'
import { fetchCollections } from '../services/api'

export function useCollections() {
  const [collections, setCollections] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchCollections()
      .then(data => {
        setCollections(data)
        setLoading(false)
      })
      .catch(err => {
        setError(err)
        setLoading(false)
      })
  }, [])

  return { collections, loading, error }
}
