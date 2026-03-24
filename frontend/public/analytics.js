/**
 * Retail Analytics Tracker
 * Drop this script into retail-recommender.vercel.app
 *
 * Usage:
 *   <script src="/analytics.js" data-api="https://your-api.onrender.com"></script>
 *
 * Then call:
 *   analytics.trackPageView()
 *   analytics.trackProductClick({ product_id: "123", product_name: "Blue Shirt" })
 *   analytics.trackAddToCart({ product_id: "123", product_name: "Blue Shirt" })
 */

;(function () {
  const script = document.currentScript
  const API_URL = (script && script.dataset.api) || 'http://localhost:8000'

  // Persist session id across page loads for the browser session
  function getSessionId() {
    let id = sessionStorage.getItem('_ra_sid')
    if (!id) {
      id = Math.random().toString(36).slice(2) + Date.now().toString(36)
      sessionStorage.setItem('_ra_sid', id)
    }
    return id
  }

  function send(payload) {
    const body = JSON.stringify({
      session_id: getSessionId(),
      page_url: window.location.href,
      referrer: document.referrer || null,
      timestamp: new Date().toISOString(),
      ...payload,
    })

    // Use sendBeacon when available so events survive page unload
    if (navigator.sendBeacon) {
      const blob = new Blob([body], { type: 'application/json' })
      navigator.sendBeacon(API_URL + '/events', blob)
    } else {
      fetch(API_URL + '/events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body,
        keepalive: true,
      }).catch(() => {})
    }
  }

  window.analytics = {
    trackPageView() {
      send({ event_type: 'page_view' })
    },

    trackProductClick({ product_id, product_name } = {}) {
      send({ event_type: 'product_click', product_id, product_name })
    },

    trackAddToCart({ product_id, product_name } = {}) {
      send({ event_type: 'add_to_cart', product_id, product_name })
    },
  }

  // Auto-track page views on script load
  window.analytics.trackPageView()
})()
