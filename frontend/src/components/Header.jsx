import React, { useState } from 'react'
import { useCart } from '../context/CartContext'

const CATEGORIES = ['All', 'Electronics', 'Home', 'Clothing', 'Beauty', 'Grocery', 'Toys']

export default function Header({ activeCategory, onCategory }) {
  const { items, removeItem, totalCount, totalPrice } = useCart()
  const [cartOpen, setCartOpen] = useState(false)

  return (
    <header style={s.header}>
      <div style={s.top}>
        <div style={s.logo}>🛍️ ShopSmart</div>
        <div style={s.tagline}>Recommendations powered by ML</div>

        {/* Cart icon */}
        <button style={s.cartBtn} onClick={() => setCartOpen(o => !o)}>
          🛒
          {totalCount > 0 && (
            <span style={s.badge}>{totalCount}</span>
          )}
        </button>
      </div>

      {/* Cart dropdown */}
      {cartOpen && (
        <div style={s.cartDropdown}>
          <div style={s.cartHeader}>
            <span style={s.cartTitle}>Your Cart</span>
            <button style={s.closeBtn} onClick={() => setCartOpen(false)}>✕</button>
          </div>

          {items.length === 0 ? (
            <div style={s.emptyCart}>Your cart is empty</div>
          ) : (
            <>
              <div style={s.cartItems}>
                {items.map(({ product, quantity }) => (
                  <div key={product.id} style={s.cartItem}>
                    <div style={s.cartItemInfo}>
                      <div style={s.cartItemName}>{product.name}</div>
                      <div style={s.cartItemMeta}>
                        ${product.price.toFixed(2)} × {quantity}
                      </div>
                    </div>
                    <div style={s.cartItemRight}>
                      <span style={s.cartItemTotal}>
                        ${(product.price * quantity).toFixed(2)}
                      </span>
                      <button style={s.removeBtn} onClick={() => removeItem(product.id)}>✕</button>
                    </div>
                  </div>
                ))}
              </div>
              <div style={s.cartFooter}>
                <span style={s.totalLabel}>Total</span>
                <span style={s.totalPrice}>${totalPrice.toFixed(2)}</span>
              </div>
              <button style={s.checkoutBtn}>Checkout</button>
            </>
          )}
        </div>
      )}

      {onCategory && (
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
      )}
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
    gap: '12px',
  },
  logo: { fontSize: '1.4rem', fontWeight: 700, letterSpacing: '-0.5px' },
  tagline: { fontSize: '0.75rem', color: '#94a3b8', flex: 1 },
  cartBtn: {
    background: 'none',
    border: '1px solid #334155',
    borderRadius: '10px',
    color: '#fff',
    fontSize: '1.2rem',
    padding: '6px 12px',
    cursor: 'pointer',
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
  },
  badge: {
    position: 'absolute',
    top: '-6px',
    right: '-6px',
    background: '#ef4444',
    color: '#fff',
    fontSize: '0.65rem',
    fontWeight: 700,
    borderRadius: '999px',
    minWidth: '18px',
    height: '18px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '0 4px',
  },
  cartDropdown: {
    position: 'absolute',
    top: '64px',
    right: '28px',
    width: '340px',
    background: '#fff',
    borderRadius: '14px',
    boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
    zIndex: 200,
    overflow: 'hidden',
  },
  cartHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '16px 20px',
    borderBottom: '1px solid #f1f5f9',
  },
  cartTitle: { fontSize: '1rem', fontWeight: 700, color: '#0f172a' },
  closeBtn: {
    background: 'none', border: 'none', cursor: 'pointer',
    color: '#94a3b8', fontSize: '1rem',
  },
  emptyCart: { padding: '32px 20px', textAlign: 'center', color: '#94a3b8', fontSize: '0.9rem' },
  cartItems: { maxHeight: '320px', overflowY: 'auto' },
  cartItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px 20px',
    borderBottom: '1px solid #f8fafc',
    gap: '12px',
  },
  cartItemInfo: { flex: 1, minWidth: 0 },
  cartItemName: {
    fontSize: '0.85rem', fontWeight: 600, color: '#0f172a',
    whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
  },
  cartItemMeta: { fontSize: '0.75rem', color: '#94a3b8', marginTop: '2px' },
  cartItemRight: { display: 'flex', alignItems: 'center', gap: '10px' },
  cartItemTotal: { fontSize: '0.9rem', fontWeight: 700, color: '#0f172a' },
  removeBtn: {
    background: 'none', border: 'none', cursor: 'pointer',
    color: '#94a3b8', fontSize: '0.8rem', padding: '2px 4px',
  },
  cartFooter: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '14px 20px',
    borderTop: '1px solid #f1f5f9',
  },
  totalLabel: { fontSize: '0.9rem', fontWeight: 600, color: '#475569' },
  totalPrice: { fontSize: '1rem', fontWeight: 800, color: '#0f172a' },
  checkoutBtn: {
    width: 'calc(100% - 40px)',
    margin: '0 20px 16px',
    background: '#3b82f6',
    color: '#fff',
    border: 'none',
    borderRadius: '10px',
    padding: '12px',
    fontSize: '0.95rem',
    fontWeight: 700,
    cursor: 'pointer',
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
