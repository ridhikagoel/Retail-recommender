import React, { useState, useMemo } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import ProductRow from './components/ProductRow'
import { useLandingPage } from './hooks/useRecommendations'
import ProductPage from './pages/ProductPage'

function LandingPage() {
  const [category, setCategory] = useState(null)
  const { data, loading, error } = useLandingPage('current_user')

  const sections = useMemo(() => {
    if (!data?.sections) return []
    if (!category) return data.sections
    return data.sections
      .map(s => ({
        ...s,
        products: s.products.filter(p => p.category === category),
      }))
      .filter(s => s.products.length > 0)
  }, [data, category])

  return (
    <div style={s.page}>
      <Header activeCategory={category} onCategory={setCategory} />

      <main style={s.main}>
        {/* Hero banner */}
        <div style={s.hero}>
          <div>
            <h1 style={s.heroTitle}>Your Personal Store</h1>
            <p style={s.heroSub}>
              Recommendations tailored to you — powered by collaborative filtering,
              trending signals, and editorial curation.
            </p>
          </div>
          <div style={s.heroBadges}>
            {['52 Products', '12 Strategies', '25 Users', 'Live ML'].map(t => (
              <span key={t} style={s.heroBadge}>{t}</span>
            ))}
          </div>
        </div>

        {/* Error state */}
        {error && (
          <div style={s.errorBox}>
            ⚠️ Could not load recommendations — is the backend running on port 8000?
            <br />
            <code style={{ fontSize: '0.75rem' }}>{error.message}</code>
          </div>
        )}

        {/* Sections */}
        {loading
          ? SKELETON_SECTIONS.map(({ title, subtitle }) => (
              <ProductRow key={title} title={title} subtitle={subtitle} loading />
            ))
          : sections.map(({ id, title, subtitle, products }) => (
              <ProductRow
                key={id}
                title={title}
                subtitle={subtitle}
                products={products}
              />
            ))}

        {!loading && !error && sections.length === 0 && (
          <div style={s.emptyState}>
            No products found for <strong>{category}</strong> in the current recommendations.
            Try a different category.
          </div>
        )}
      </main>

      <footer style={s.footer}>
        ShopSmart Retail Recommender · FastAPI + Redis + PostgreSQL + scikit-learn
      </footer>

      {/* Shimmer keyframes injected as a style tag */}
      <style>{`
        @keyframes shimmer {
          0%   { background-position: 100% 0; }
          100% { background-position: -100% 0; }
        }
        * { box-sizing: border-box; }
        body { margin: 0; background: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
        ::-webkit-scrollbar { height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
      `}</style>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/product/:id" element={<ProductPage />} />
      </Routes>
    </BrowserRouter>
  )
}

const SKELETON_SECTIONS = [
  { title: 'Picked For You',     subtitle: 'Based on your shopping history' },
  { title: 'Flash Deals',        subtitle: 'Today only — limited time offers' },
  { title: 'Trending Right Now', subtitle: 'What everyone is buying this week' },
  { title: 'Best Sellers',       subtitle: 'Most loved by our customers' },
]

const s = {
  page: { minHeight: '100vh', display: 'flex', flexDirection: 'column' },
  main: { flex: 1, padding: '28px 0 0' },
  hero: {
    background: 'linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%)',
    color: '#fff',
    padding: '32px 28px',
    marginBottom: '36px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: '16px',
  },
  heroTitle: {
    margin: '0 0 8px',
    fontSize: '1.8rem',
    fontWeight: 800,
    letterSpacing: '-0.5px',
  },
  heroSub: {
    margin: 0,
    fontSize: '0.9rem',
    color: '#94a3b8',
    maxWidth: '480px',
    lineHeight: 1.5,
  },
  heroBadges: {
    display: 'flex',
    gap: '8px',
    flexWrap: 'wrap',
  },
  heroBadge: {
    background: 'rgba(255,255,255,0.1)',
    border: '1px solid rgba(255,255,255,0.2)',
    color: '#e2e8f0',
    padding: '6px 14px',
    borderRadius: '20px',
    fontSize: '0.78rem',
    fontWeight: 600,
  },
  errorBox: {
    margin: '0 28px 24px',
    background: '#fef2f2',
    border: '1px solid #fecaca',
    color: '#b91c1c',
    padding: '16px 20px',
    borderRadius: '10px',
    fontSize: '0.9rem',
    lineHeight: 1.6,
  },
  emptyState: {
    textAlign: 'center',
    padding: '60px 28px',
    color: '#64748b',
    fontSize: '0.95rem',
  },
  footer: {
    textAlign: 'center',
    padding: '20px',
    fontSize: '0.75rem',
    color: '#94a3b8',
    borderTop: '1px solid #e2e8f0',
    marginTop: '40px',
  },
}
