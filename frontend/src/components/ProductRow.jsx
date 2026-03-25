import React from 'react'
import ProductCard from './ProductCard'

export default function ProductRow({ title, subtitle, products, loading, strategy }) {
  return (
    <section style={s.section}>
      <div style={s.heading}>
        <h2 style={s.title}>{title}</h2>
        {subtitle && <p style={s.subtitle}>{subtitle}</p>}
      </div>

      {loading ? (
        <div style={s.shimmerRow}>
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} style={s.shimmerCard} />
          ))}
        </div>
      ) : products && products.length > 0 ? (
        <div style={s.row}>
          {products.map(p => <ProductCard key={p.id} product={p} strategy={strategy} />)}
        </div>
      ) : (
        <p style={s.empty}>No products to show.</p>
      )}
    </section>
  )
}

const s = {
  section: {
    marginBottom: '40px',
  },
  heading: {
    padding: '0 28px 10px',
  },
  title: {
    margin: 0,
    fontSize: '1.2rem',
    fontWeight: 700,
    color: '#0f172a',
  },
  subtitle: {
    margin: '2px 0 0',
    fontSize: '0.82rem',
    color: '#64748b',
  },
  row: {
    display: 'flex',
    gap: '16px',
    overflowX: 'auto',
    padding: '4px 28px 12px',
    scrollbarWidth: 'thin',
    scrollbarColor: '#cbd5e1 transparent',
  },
  shimmerRow: {
    display: 'flex',
    gap: '16px',
    padding: '4px 28px 12px',
  },
  shimmerCard: {
    width: '210px',
    minWidth: '210px',
    height: '280px',
    borderRadius: '12px',
    background: 'linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%)',
    backgroundSize: '400% 100%',
    animation: 'shimmer 1.4s infinite',
  },
  empty: {
    padding: '0 28px',
    color: '#94a3b8',
    fontSize: '0.85rem',
  },
}
