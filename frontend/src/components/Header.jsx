import React from 'react'

const CATEGORIES = ['All', 'Electronics', 'Home', 'Clothing', 'Beauty', 'Grocery', 'Toys']

export default function Header({ activeCategory, onCategory }) {
  return (
    <header style={s.header}>
      <div style={s.top}>
        <div style={s.logo}>🛍️ ShopSmart</div>
        <div style={s.tagline}>Recommendations powered by ML</div>
      </div>
      <nav style={s.nav}>
        {CATEGORIES.map(cat => (
          <button
            key={cat}
            onClick={() => onCategory(cat === 'All' ? null : cat)}
            style={{
              ...s.pill,
              ...(activeCategory === (cat === 'All' ? null : cat) ? s.pillActive : {}),
            }}
          >
            {cat}
          </button>
        ))}
      </nav>
    </header>
  )
}

const s = {
  header: {
    background: '#0f172a',
    color: '#fff',
    padding: '0',
    position: 'sticky',
    top: 0,
    zIndex: 100,
    boxShadow: '0 2px 12px rgba(0,0,0,0.4)',
  },
  top: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '14px 28px',
  },
  logo: {
    fontSize: '1.4rem',
    fontWeight: 700,
    letterSpacing: '-0.5px',
  },
  tagline: {
    fontSize: '0.75rem',
    color: '#94a3b8',
  },
  nav: {
    display: 'flex',
    gap: '8px',
    padding: '0 28px 12px',
    overflowX: 'auto',
  },
  pill: {
    background: 'transparent',
    border: '1px solid #334155',
    color: '#cbd5e1',
    borderRadius: '20px',
    padding: '5px 14px',
    fontSize: '0.8rem',
    cursor: 'pointer',
    whiteSpace: 'nowrap',
    transition: 'all 0.15s',
  },
  pillActive: {
    background: '#3b82f6',
    borderColor: '#3b82f6',
    color: '#fff',
  },
}
