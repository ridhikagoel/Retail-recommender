import { useState, useEffect } from 'react'
import { getLandingPage } from '../api/recommendations'

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
