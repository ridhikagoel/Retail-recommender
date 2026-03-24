import { useState, useEffect } from 'react'
import { getLandingPage, getAlsoBought } from '../api/recommendations'

export function useLandingPage(userId = 'current_user') {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)

  useEffect(() => {
    setLoading(true)
    getLandingPage(userId)
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [userId])

  return { data, loading, error }
}

export function useAlsoBought(productId, n = 6) {
  const [data,    setData]    = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!productId) return
    setLoading(true)
    getAlsoBought(productId, n)
      .then(setData)
      .catch(() => setData([]))
      .finally(() => setLoading(false))
  }, [productId, n])

  return { data, loading }
}
