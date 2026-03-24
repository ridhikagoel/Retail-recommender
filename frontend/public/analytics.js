/**
 * Retail Analytics Tracker
 */
;(function () {
  const script = document.currentScript
  const API_URL = (script && script.dataset.api) || 'http://localhost:8000'

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

    // Always use fetch with keepalive — more reliable than sendBeacon for CORS + JSON
    fetch(API_URL + '/events', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body,
      keepalive: true,
    }).catch(() => {})
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

  window.analytics.trackPageView()
})()
