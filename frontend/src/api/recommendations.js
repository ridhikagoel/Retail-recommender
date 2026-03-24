import axios from 'axios'

// In dev: Vite proxies /api → localhost:8000
// In production: VITE_API_URL is set to the Render backend URL
const baseURL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : '/api'

const api = axios.create({ baseURL })

export const getLandingPage  = (userId = 'current_user') =>
  api.get('/landing-page', { params: { user_id: userId } }).then(r => r.data)

export const getTrending     = (n = 8, category = null) =>
  api.get('/reco/trending',    { params: { n, ...(category && { category }) } }).then(r => r.data)

export const getBestSellers  = (n = 8, category = null) =>
  api.get('/reco/best-sellers',{ params: { n, ...(category && { category }) } }).then(r => r.data)

export const getFlashDeals   = (n = 6) =>
  api.get('/reco/flash-deals', { params: { n } }).then(r => r.data)

export const getNewArrivals  = (n = 8) =>
  api.get('/reco/new-arrivals',{ params: { n } }).then(r => r.data)

export const getPriceDrops   = (n = 8, minPct = 10) =>
  api.get('/reco/price-drops', { params: { n, min_pct: minPct } }).then(r => r.data)
