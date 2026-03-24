import React, { useState } from 'react'

const CATEGORY_COLORS = {
  Electronics: '#3b82f6',
  Home:        '#10b981',
  Clothing:    '#8b5cf6',
  Beauty:      '#ec4899',
  Grocery:     '#f59e0b',
  Toys:        '#ef4444',
}

const BADGE_STYLES = {
  'NEW':        { bg: '#10b981', color: '#fff' },
  'FLASH DEAL': { bg: '#ef4444', color: '#fff' },
  '🔥 HOT':    { bg: '#f97316', color: '#fff' },
  'BEST VALUE': { bg: '#8b5cf6', color: '#fff' },
}

function Stars({ rating }) {
  const full  = Math.floor(rating)
  const half  = rating - full >= 0.5
  const empty = 5 - full - (half ? 1 : 0)
  return (
    <span style={{ color: '#f59e0b', fontSize: '0.75rem' }}>
      {'★'.repeat(full)}
      {half ? '½' : ''}
      {'☆'.repeat(empty)}
      <span style={{ color: '#94a3b8', marginLeft: 4 }}>
        {rating.toFixed(1)} ({shortNum(rating)})
      </span>
    </span>
  )
}

function shortNum(n) {
  if (n >= 1000) return (n / 1000).toFixed(1) + 'k'
  return n
}

export default function ProductCard({ product }) {
  const [hovered, setHovered] = useState(false)
  const {
    name, category, brand, price, original_price,
    rating, review_count, badge, reason,
    flash_discount_pct, ends_in_hours, discount_pct, savings,
  } = product

  const discounted = original_price > price
  const accentColor = CATEGORY_COLORS[category] || '#64748b'
  const badgeStyle  = BADGE_STYLES[badge] || null

  return (
    <div
      style={{ ...s.card, ...(hovered ? s.cardHover : {}) }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* Category accent bar */}
      <div style={{ ...s.accentBar, background: accentColor }} />

      {/* Badge */}
      {badge && badgeStyle && (
        <div style={{ ...s.badge, background: badgeStyle.bg, color: badgeStyle.color }}>
          {badge}
        </div>
      )}
      {/* Discount badge (for price drops) */}
      {!badge && discount_pct && (
        <div style={{ ...s.badge, background: '#ef4444', color: '#fff' }}>
          -{discount_pct}%
        </div>
      )}

      {/* Product image placeholder */}
      <div style={{ ...s.imgBox, background: accentColor + '18' }}>
        <span style={{ fontSize: '2.2rem' }}>{categoryEmoji(category)}</span>
      </div>

      <div style={s.body}>
        {/* Category + brand */}
        <div style={s.meta}>
          <span style={{ ...s.catChip, color: accentColor }}>{category}</span>
          <span style={s.brandText}>{brand}</span>
        </div>

        {/* Name */}
        <div style={s.name}>{name}</div>

        {/* Rating */}
        <div style={{ margin: '4px 0' }}>
          <Stars rating={rating} />
          <span style={{ fontSize: '0.7rem', color: '#94a3b8', marginLeft: 4 }}>
            ({review_count.toLocaleString()})
          </span>
        </div>

        {/* Price */}
        <div style={s.priceRow}>
          <span style={s.price}>${price.toFixed(2)}</span>
          {discounted && (
            <span style={s.originalPrice}>${original_price.toFixed(2)}</span>
          )}
          {savings && (
            <span style={s.savings}>Save ${savings.toFixed(2)}</span>
          )}
        </div>

        {/* Flash deal info */}
        {flash_discount_pct && ends_in_hours && (
          <div style={s.flashInfo}>
            🔥 {flash_discount_pct}% off · ends in {ends_in_hours}h
          </div>
        )}

        {/* Reason */}
        <div style={s.reason}>{reason}</div>
      </div>
    </div>
  )
}

function categoryEmoji(cat) {
  const map = {
    Electronics: '💻', Home: '🏠', Clothing: '👕',
    Beauty: '✨', Grocery: '🛒', Toys: '🎮',
  }
  return map[cat] || '📦'
}

const s = {
  card: {
    background: '#fff',
    borderRadius: '12px',
    width: '210px',
    minWidth: '210px',
    boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
    overflow: 'hidden',
    position: 'relative',
    transition: 'transform 0.18s, box-shadow 0.18s',
    cursor: 'pointer',
    display: 'flex',
    flexDirection: 'column',
  },
  cardHover: {
    transform: 'translateY(-4px)',
    boxShadow: '0 8px 24px rgba(0,0,0,0.14)',
  },
  accentBar: {
    height: '4px',
    width: '100%',
  },
  badge: {
    position: 'absolute',
    top: '12px',
    right: '10px',
    fontSize: '0.65rem',
    fontWeight: 700,
    padding: '3px 7px',
    borderRadius: '6px',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  imgBox: {
    height: '110px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  body: {
    padding: '10px 12px 14px',
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
    flex: 1,
  },
  meta: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    marginBottom: '2px',
  },
  catChip: {
    fontSize: '0.68rem',
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  brandText: {
    fontSize: '0.68rem',
    color: '#94a3b8',
  },
  name: {
    fontSize: '0.87rem',
    fontWeight: 600,
    color: '#1e293b',
    lineHeight: 1.3,
    display: '-webkit-box',
    WebkitLineClamp: 2,
    WebkitBoxOrient: 'vertical',
    overflow: 'hidden',
  },
  priceRow: {
    display: 'flex',
    alignItems: 'baseline',
    gap: '6px',
    margin: '4px 0 2px',
  },
  price: {
    fontSize: '1.05rem',
    fontWeight: 700,
    color: '#0f172a',
  },
  originalPrice: {
    fontSize: '0.8rem',
    color: '#94a3b8',
    textDecoration: 'line-through',
  },
  savings: {
    fontSize: '0.72rem',
    color: '#10b981',
    fontWeight: 600,
  },
  flashInfo: {
    fontSize: '0.72rem',
    color: '#ef4444',
    fontWeight: 600,
    background: '#fef2f2',
    padding: '3px 6px',
    borderRadius: '4px',
  },
  reason: {
    fontSize: '0.7rem',
    color: '#64748b',
    marginTop: 'auto',
    paddingTop: '6px',
    fontStyle: 'italic',
  },
}
