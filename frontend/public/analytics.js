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

  var _me = document.currentScript;
  var API_URL = (_me && _me.getAttribute('data-api'))
    || (typeof import_meta_env !== 'undefined' && import_meta_env.VITE_API_URL)
    || '';

  /* ── Device type ─────────────────────────────────────────────────────────── */

  function _getDeviceType() {
    var ua = navigator.userAgent;
    if (/Mobi|Android|iPhone|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua)) {
      return 'mobile';
    }
    if (/iPad|Tablet|(Android(?!.*Mobile))/i.test(ua) ||
        (window.innerWidth >= 768 && window.innerWidth < 1024)) {
      return 'tablet';
    }
    return 'desktop';
  }

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

  var variant = sessionStorage.getItem(VARIANT_KEY) || null;

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
        session_id:  sessionId,
        device_type: _getDeviceType(),
        variant:     variant || sessionStorage.getItem(VARIANT_KEY) || 'control',
        event_type:  eventType,
        page_url:    window.location.href,
        referrer:    document.referrer,
        timestamp:   new Date().toISOString(),
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
    trackLandingPageView: function () {
      _send('landing_page_view');
    },

    trackProductDisplayPageView: function (props) {
      _send('product_display_page_view', props);
    },

    trackProductClick: function (props) {
      _send('product_click', props);
    },

    trackAddToCart: function (props) {
      _send('add_to_cart', props);
    },

    getSessionId: function () { return sessionId; },
    getVariant:   function () { return variant || sessionStorage.getItem(VARIANT_KEY) || 'control'; },

    setVariant: function (v) {
      variant = v;
      sessionStorage.setItem(VARIANT_KEY, v);
    },
  };
})();
