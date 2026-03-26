/**
 * Retail Recommender — Analytics & A/B Test Tracker
 *
 * Loaded as a plain <script> tag in index.html.  Exposes window.analytics
 * with methods called by React components at key interaction points.
 *
 * A/B variant assignment:
 *   1. A stable session_id is generated once per browser session and stored
 *      in sessionStorage.
 *   2. On initialisation the tracker calls GET /api/ab/variant?session_id=…
 *      to receive the server-assigned variant ("control" or "treatment").
 *      The variant is cached in sessionStorage so subsequent page loads in
 *      the same session don't need an extra round-trip.
 *   3. Every event sent to POST /events includes the session_id and variant,
 *      enabling the backend to split conversion metrics by variant.
 */

(function () {
  'use strict';

  /* ── Config ─────────────────────────────────────────────────────────────── */

  // Populated by Vite at build time; falls back to relative path for dev.
  var API_URL = (typeof import_meta_env !== 'undefined' && import_meta_env.VITE_API_URL)
    ? import_meta_env.VITE_API_URL
    : (window.__API_URL__ || '');   // set window.__API_URL__ in index.html if needed

  /* ── Session & variant ──────────────────────────────────────────────────── */

  var SESSION_KEY = 'ab_session_id';
  var VARIANT_KEY  = 'ab_variant';

  function _genId() {
    return 'sess_' +
      Math.random().toString(36).slice(2, 10) +
      Date.now().toString(36);
  }

  var sessionId = sessionStorage.getItem(SESSION_KEY);
  if (!sessionId) {
    sessionId = _genId();
    sessionStorage.setItem(SESSION_KEY, sessionId);
  }

  // Variant may already be known from a previous page in the same session.
  var variant = sessionStorage.getItem(VARIANT_KEY) || null;

  // Fetch the server-assigned variant asynchronously.
  // Events fired before the response arrives use 'control' as a safe default;
  // the server will re-assign the correct variant when it stores the event.
  if (!variant) {
    fetch(API_URL + '/api/ab/variant?session_id=' + encodeURIComponent(sessionId), {
      method: 'GET',
      mode:   'cors',
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        variant = data.variant || 'control';
        sessionStorage.setItem(VARIANT_KEY, variant);
      })
      .catch(function () {
        variant = 'control';
      });
  }

  /* ── Core send function ─────────────────────────────────────────────────── */

  function _send(eventType, props) {
    var payload = Object.assign(
      {
        session_id: sessionId,
        variant:    variant || sessionStorage.getItem(VARIANT_KEY) || 'control',
        event_type: eventType,
        page_url:   window.location.href,
        referrer:   document.referrer,
        timestamp:  new Date().toISOString(),
      },
      props || {}
    );

    try {
      fetch(API_URL + '/events', {
        method:    'POST',
        mode:      'cors',
        keepalive: true,
        headers:   { 'Content-Type': 'application/json' },
        body:      JSON.stringify(payload),
      }).catch(function () { /* fail silently */ });
    } catch (_) { /* fetch not available */ }
  }

  /* ── Public API ─────────────────────────────────────────────────────────── */

  window.analytics = {
    /** Called when the landing page mounts. */
    trackLandingPageView: function () {
      _send('landing_page_view');
    },

    /** Called when a product detail page mounts.
     *  @param {{ product_id: string, product_name: string }} props
     */
    trackProductDisplayPageView: function (props) {
      _send('product_display_page_view', props);
    },

    /** Called when a product card is clicked from a recommendation row.
     *  @param {{ product_id, product_name, category, strategy }} props
     */
    trackProductClick: function (props) {
      _send('product_click', props);
    },

    /** Called when a product is added to the cart.
     *  @param {{ product_id, product_name }} props
     */
    trackAddToCart: function (props) {
      _send('add_to_cart', props);
    },

    /** Expose session metadata for debugging. */
    getSessionId: function () { return sessionId; },
    getVariant:   function () { return variant || sessionStorage.getItem(VARIANT_KEY) || 'control'; },

    /**
     * Allow external code (e.g. landing-page fetch) to override the variant
     * without waiting for the async /api/ab/variant call.
     */
    setVariant: function (v) {
      variant = v;
      sessionStorage.setItem(VARIANT_KEY, v);
    },
  };
})();
