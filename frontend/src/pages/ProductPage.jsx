import React, { useState } from 'react'
import { useLocation, useParams, useNavigate } from 'react-router-dom'
import { useAlsoBought } from '../hooks/useRecommendations'
import { useCart } from '../context/CartContext'
import Header from '../components/Header'
import ProductRow from '../components/ProductRow'

const CATEGORY_COLORS = {
  Electronics: '#3b82f6',
  Home:        '#10b981',
  Clothing:    '#8b5cf6',
  Beauty:      '#ec4899',
  Grocery:     '#f59e0b',
  Toys:        '#ef4444',
}

function categoryEmoji(cat) {
  const map = { Electronics: '💻', Home: '🏠', Clothing: '👕', Beauty: '✨', Grocery: '🛒', Toys: '🎮' }
  return map[cat] || '📦'
}

function Stars({ rating }) {
  const full  = Math.floor(rating)
  const half  = rating - full >= 0.5
  const empty = 5 - full - (half ? 1 : 0)
  return (
    <span style={{ color: '#f59e0b', fontSize: '1rem' }}>
      {'★'.repeat(full)}{half ? '½' : ''}{'☆'.repeat(empty)}
    </span>
  )
}

export default function ProductPage() {
  const { id } = useParams()
  const { state } = useLocation()
  const navigate = useNavigate()
  const { addItem } = useCart()
  const [added, setAdded] = useState(false)
  const product = state?.product
  const { data: alsoBought, loading } = useAlsoBought(id)

  function handleAddToCart() {
    addItem(product)
    setAdded(true)
    setTimeout(() => setAdded(false), 2000)
  }

  if (!product) {
    return (
      <div style={s.notFound}>
        <p>Product not found. Please go back and click a product card.</p>
        <button style={s.backBtn} onClick={() => navigate('/')}>← Back to Store</button>
      </div>
    )
  }

  const {
    name, category, subcategory, brand, price, original_price,
    rating, review_count, description, tags,
    flash_discount_pct, ends_in_hours, discount_pct, savings, badge,
  } = product

  const accentColor = CATEGORY_COLORS[category] || '#64748b'
  const discounted  = original_price > price

  return (
    <div style={s.page}>
      <Header />

      {/* Top bar */}
      <div style={{ ...s.topBar, borderBottomColor: accentColor }}>
        <button style={s.backBtn} onClick={() => navigate(-1)}>← Back</button>
        <span style={{ ...s.categoryLabel, color: accentColor }}>
          {categoryEmoji(category)} {category}
        </span>
      </div>

      <main style={s.main}>
        {/* Product detail card */}
        <div style={s.card}>
          {/* Image area */}
          <div style={{ ...s.imgBox, background: accentColor + '18' }}>
            <span style={{ fontSize: '5rem' }}>{categoryEmoji(category)}</span>
          </div>

          {/* Info */}
          <div style={s.info}>
            {badge && <div style={{ ...s.badge, background: accentColor }}>{badge}</div>}

            <div style={s.meta}>{brand} · {subcategory}</div>
            <h1 style={s.name}>{name}</h1>

            <div style={s.ratingRow}>
              <Stars rating={rating} />
              <span style={s.ratingText}>{rating.toFixed(1)} · {review_count.toLocaleString()} reviews</span>
            </div>

            <div style={s.priceRow}>
              <span style={s.price}>${price.toFixed(2)}</span>
              {discounted && <span style={s.originalPrice}>${original_price.toFixed(2)}</span>}
              {savings && <span style={s.savings}>Save ${savings.toFixed(2)}</span>}
              {discount_pct && <span style={s.discountChip}>-{discount_pct}%</span>}
            </div>

            {flash_discount_pct && ends_in_hours && (
              <div style={s.flashBanner}>
                🔥 Flash Deal — {flash_discount_pct}% off · ends in {ends_in_hours}h
              </div>
            )}

            {description && <p style={s.description}>{description}</p>}

            {tags && tags.length > 0 && (
              <div style={s.tags}>
                {tags.map(t => (
                  <span key={t} style={{ ...s.tag, borderColor: accentColor, color: accentColor }}>{t}</span>
                ))}
              </div>
            )}

            <button
              style={{ ...s.addToCart, background: added ? '#10b981' : accentColor }}
              onClick={handleAddToCart}
            >
              {added ? '✓ Added to Cart' : 'Add to Cart'}
            </button>
          </div>
        </div>

        {/* Customers also bought */}
        <div style={s.recoSection}>
          <ProductRow
            title="Customers Also Bought"
            subtitle="Based on shoppers who viewed this item"
            products={alsoBought}
            loading={loading}
          />
        </div>
      </main>
    </div>
  )
}

const s = {
  page: { minHeight: '100vh', background: '#f8fafc', fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" },
  topBar: {
    display: 'flex', alignItems: 'center', gap: '16px',
    padding: '14px 28px', background: '#fff',
    borderBottom: '2px solid #e2e8f0', position: 'sticky', top: 0, zIndex: 10,
  },
  backBtn: {
    background: 'none', border: '1px solid #e2e8f0', borderRadius: '8px',
    padding: '6px 14px', cursor: 'pointer', fontSize: '0.88rem',
    color: '#475569', fontWeight: 600,
  },
  categoryLabel: { fontSize: '0.88rem', fontWeight: 600 },
  main: { maxWidth: '1000px', margin: '0 auto', padding: '32px 24px' },
  card: {
    display: 'flex', gap: '40px', background: '#fff',
    borderRadius: '16px', boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
    overflow: 'hidden', marginBottom: '48px',
    flexWrap: 'wrap',
  },
  imgBox: {
    width: '340px', minWidth: '260px', minHeight: '300px',
    display: 'flex', alignItems: 'center', justifyContent: 'center', flex: '0 0 auto',
  },
  info: { flex: 1, padding: '32px 32px 32px 0', minWidth: '260px', display: 'flex', flexDirection: 'column', gap: '12px' },
  badge: {
    display: 'inline-block', color: '#fff', fontSize: '0.7rem', fontWeight: 700,
    padding: '4px 10px', borderRadius: '6px', textTransform: 'uppercase',
    letterSpacing: '0.5px', alignSelf: 'flex-start',
  },
  meta: { fontSize: '0.82rem', color: '#94a3b8', fontWeight: 500 },
  name: { margin: 0, fontSize: '1.6rem', fontWeight: 800, color: '#0f172a', lineHeight: 1.2 },
  ratingRow: { display: 'flex', alignItems: 'center', gap: '8px' },
  ratingText: { fontSize: '0.88rem', color: '#64748b' },
  priceRow: { display: 'flex', alignItems: 'baseline', gap: '10px', flexWrap: 'wrap' },
  price: { fontSize: '1.8rem', fontWeight: 800, color: '#0f172a' },
  originalPrice: { fontSize: '1.1rem', color: '#94a3b8', textDecoration: 'line-through' },
  savings: { fontSize: '0.88rem', color: '#10b981', fontWeight: 700 },
  discountChip: {
    fontSize: '0.78rem', fontWeight: 700, color: '#fff',
    background: '#ef4444', padding: '3px 8px', borderRadius: '6px',
  },
  flashBanner: {
    background: '#fef2f2', border: '1px solid #fecaca',
    color: '#dc2626', padding: '10px 14px', borderRadius: '8px',
    fontSize: '0.88rem', fontWeight: 600,
  },
  description: { margin: 0, fontSize: '0.92rem', color: '#475569', lineHeight: 1.6 },
  tags: { display: 'flex', flexWrap: 'wrap', gap: '8px' },
  tag: {
    fontSize: '0.75rem', fontWeight: 500, padding: '4px 10px',
    borderRadius: '20px', border: '1px solid', background: 'transparent',
  },
  addToCart: {
    color: '#fff', border: 'none', borderRadius: '10px',
    padding: '14px 28px', fontSize: '1rem', fontWeight: 700,
    cursor: 'pointer', marginTop: '8px', alignSelf: 'flex-start',
  },
  recoSection: { marginTop: '8px' },
  notFound: { textAlign: 'center', padding: '80px 24px', color: '#64748b' },
}
