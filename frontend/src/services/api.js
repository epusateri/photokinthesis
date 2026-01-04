const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export async function fetchCollections() {
  const response = await fetch(`${API_BASE_URL}/collections`)
  if (!response.ok) throw new Error('Failed to fetch collections')
  const data = await response.json()
  return data.collections
}

export async function fetchPhotos(collectionName, { offset = 0, limit = 50, search = '' }) {
  const params = new URLSearchParams({ offset: offset.toString(), limit: limit.toString() })
  if (search) params.append('search', search)

  const response = await fetch(
    `${API_BASE_URL}/collections/${collectionName}/photos?${params}`
  )
  if (!response.ok) throw new Error('Failed to fetch photos')
  return response.json()
}

export async function fetchMetadata(collectionName, basename) {
  const response = await fetch(
    `${API_BASE_URL}/collections/${collectionName}/photos/${basename}/metadata`
  )
  if (!response.ok) throw new Error('Failed to fetch metadata')
  return response.json()
}

export function getImageUrl(collectionName, version, type, filename, size = 'full') {
  const params = size !== 'full' ? `?size=${size}` : ''
  return `${API_BASE_URL}/images/${collectionName}/${version}/${type}/${filename}${params}`
}
