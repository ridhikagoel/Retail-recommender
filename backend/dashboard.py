"""
HTML for the A/B test dashboard, served at GET /dashboard.

The page is entirely self-contained: it fetches /api/ab/results on load and
auto-refreshes every 30 s.  Chart.js and Tailwind are loaded from CDN.
"""

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>A/B Test Dashboard — Retail Recommender</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
  <style>
    body { font-family: 'Inter', system-ui, sans-serif; background: #f8fafc; }
    .card { background: white; border-radius: 12px; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
    .badge-sig   { background:#dcfce7; color:#15803d; }
    .badge-insig { background:#fef9c3; color:#92400e; }
    .badge-low   { background:#fee2e2; color:#991b1b; }
    .pill { padding: 3px 10px; border-radius: 999px; font-size: .75rem; font-weight: 600; display:inline-block; }
    canvas { max-height: 280px; }
    .metric-card { border-left: 4px solid #6366f1; }
    .metric-card.treatment { border-color: #f59e0b; }
    #status-dot { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:6px; }
  </style>
</head>
<body class="min-h-screen p-6">

<!-- ── Header ─────────────────────────────────────────────────────────────── -->
<div class="max-w-7xl mx-auto">
  <div class="flex items-center justify-between mb-6">
    <div>
      <h1 class="text-2xl font-bold text-gray-900" id="exp-name">A/B Test Dashboard</h1>
      <p class="text-sm text-gray-500 mt-1" id="exp-desc">Loading experiment…</p>
    </div>
    <div class="flex items-center gap-3">
      <span id="status-dot" class="bg-yellow-400"></span>
      <span class="text-sm text-gray-500" id="last-updated">Fetching…</span>
      <button onclick="load()" class="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition">↺ Refresh</button>
    </div>
  </div>

  <!-- ── Significance verdict ──────────────────────────────────────────────── -->
  <div id="verdict-banner" class="card p-5 mb-6 flex items-start gap-4 hidden">
    <div class="text-3xl" id="verdict-icon">⏳</div>
    <div>
      <div class="font-semibold text-gray-900 text-lg" id="verdict-title">Computing…</div>
      <div class="text-sm text-gray-600 mt-1" id="verdict-msg"></div>
    </div>
    <div class="ml-auto text-right">
      <div class="text-xs text-gray-400 uppercase tracking-wide">Bayesian P(T&gt;C)</div>
      <div class="text-2xl font-bold text-indigo-600" id="bayes-prob">—</div>
    </div>
  </div>

  <!-- ── Summary cards ─────────────────────────────────────────────────────── -->
  <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
    <div class="card p-5 metric-card">
      <div class="text-xs text-gray-400 uppercase tracking-wide mb-1">Control Sessions</div>
      <div class="text-3xl font-bold text-gray-900" id="c-sessions">—</div>
      <div class="text-xs text-indigo-600 mt-1">Collaborative filtering</div>
    </div>
    <div class="card p-5 metric-card treatment">
      <div class="text-xs text-gray-400 uppercase tracking-wide mb-1">Treatment Sessions</div>
      <div class="text-3xl font-bold text-gray-900" id="t-sessions">—</div>
      <div class="text-xs text-amber-600 mt-1">Best sellers</div>
    </div>
    <div class="card p-5">
      <div class="text-xs text-gray-400 uppercase tracking-wide mb-1">Add-to-Cart Rate</div>
      <div class="flex gap-3 items-end mt-1">
        <div>
          <div class="text-xs text-gray-400">Control</div>
          <div class="text-xl font-bold text-indigo-600" id="c-cart-rate">—</div>
        </div>
        <div class="text-gray-300 text-xl mb-0.5">vs</div>
        <div>
          <div class="text-xs text-gray-400">Treatment</div>
          <div class="text-xl font-bold text-amber-500" id="t-cart-rate">—</div>
        </div>
      </div>
    </div>
    <div class="card p-5">
      <div class="text-xs text-gray-400 uppercase tracking-wide mb-1">Relative Lift</div>
      <div class="text-3xl font-bold" id="rel-lift">—</div>
      <div class="text-xs text-gray-400 mt-1">Treatment vs Control</div>
    </div>
  </div>

  <!-- ── Charts row ─────────────────────────────────────────────────────────── -->
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">

    <!-- Conversion rate comparison -->
    <div class="card p-5">
      <h2 class="font-semibold text-gray-700 mb-4">Conversion Rates with 95% CI</h2>
      <canvas id="convChart"></canvas>
    </div>

    <!-- Time series -->
    <div class="card p-5">
      <h2 class="font-semibold text-gray-700 mb-4">Daily Cart Conversion Rate (14 days)</h2>
      <canvas id="tsChart"></canvas>
    </div>
  </div>

  <!-- ── Statistical detail ─────────────────────────────────────────────────── -->
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">

    <!-- Primary metric detail -->
    <div class="card p-5 lg:col-span-2">
      <h2 class="font-semibold text-gray-700 mb-4">Primary Metric — Add-to-Cart Rate</h2>
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 text-sm">
        <div><div class="text-gray-400">Z-statistic</div><div class="font-bold text-gray-900 text-lg" id="z-stat">—</div></div>
        <div><div class="text-gray-400">p-value</div><div class="font-bold text-gray-900 text-lg" id="p-val">—</div></div>
        <div><div class="text-gray-400">Confidence</div><div class="font-bold text-gray-900 text-lg" id="conf">95%</div></div>
        <div><div class="text-gray-400">Absolute Lift</div><div class="font-bold text-gray-900 text-lg" id="abs-lift">—</div></div>
        <div><div class="text-gray-400">Cohen's h</div><div class="font-bold text-gray-900 text-lg" id="cohens-h">—</div></div>
        <div><div class="text-gray-400">Effect Size</div><div class="font-bold text-gray-900 text-lg" id="effect-label">—</div></div>
        <div class="sm:col-span-2"><div class="text-gray-400">Control 95% CI</div><div class="font-bold text-gray-900" id="c-ci">—</div></div>
        <div class="sm:col-span-1"><div class="text-gray-400">Treatment 95% CI</div><div class="font-bold text-gray-900" id="t-ci">—</div></div>
      </div>

      <!-- Power / sample size -->
      <div class="mt-5 pt-4 border-t border-gray-100">
        <div class="flex items-center gap-2 mb-2">
          <span class="text-sm font-medium text-gray-700">Power Analysis</span>
          <span id="power-badge" class="pill">—</span>
        </div>
        <p class="text-sm text-gray-500" id="power-msg">—</p>
      </div>
    </div>

    <!-- Secondary metrics -->
    <div class="card p-5">
      <h2 class="font-semibold text-gray-700 mb-4">Secondary Metrics</h2>
      <div id="secondary-metrics" class="space-y-4 text-sm text-gray-600">
        <p class="text-gray-400 italic">Loading…</p>
      </div>
    </div>
  </div>

  <!-- ── Strategy breakdown table ──────────────────────────────────────────── -->
  <div class="card p-5 mb-6">
    <h2 class="font-semibold text-gray-700 mb-4">Click-Through Rate by Strategy</h2>
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-left text-gray-400 text-xs uppercase tracking-wide border-b">
            <th class="pb-2 pr-4">Strategy</th>
            <th class="pb-2 pr-4">Variant</th>
            <th class="pb-2 pr-4 text-right">Clicks</th>
            <th class="pb-2 text-right">CTR</th>
          </tr>
        </thead>
        <tbody id="strategy-table" class="divide-y divide-gray-50">
          <tr><td colspan="4" class="py-4 text-center text-gray-400 italic">No click data yet</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- ── Experiment config ───────────────────────────────────────────────────── -->
  <div class="card p-5 mb-6">
    <h2 class="font-semibold text-gray-700 mb-3">Experiment Config</h2>
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
      <div><div class="text-gray-400">Experiment ID</div><div class="font-mono text-gray-900" id="exp-id">—</div></div>
      <div><div class="text-gray-400">Traffic Split</div><div class="text-gray-900" id="traffic-split">—</div></div>
      <div><div class="text-gray-400">MDE</div><div class="text-gray-900" id="mde">—</div></div>
      <div><div class="text-gray-400">Required n/variant</div><div class="text-gray-900" id="req-n">—</div></div>
    </div>
    <div class="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
      <div><div class="text-gray-400">Control</div><div class="text-gray-700" id="ctrl-desc">—</div></div>
      <div><div class="text-gray-400">Treatment</div><div class="text-gray-700" id="trt-desc">—</div></div>
    </div>
  </div>

  <p class="text-center text-xs text-gray-400 pb-6">Auto-refreshes every 30 s · <a href="/docs" class="underline hover:text-indigo-600">API docs</a></p>
</div>

<!-- ── JavaScript ─────────────────────────────────────────────────────────── -->
<script>
let convChart, tsChart;

function pct(v) { return (v * 100).toFixed(2) + '%'; }
function fmt(v, decimals=4) { return v == null ? '—' : Number(v).toFixed(decimals); }

function renderConvChart(data) {
  const pm   = data.primary_metric;
  const ctrl = pm.control;
  const trt  = pm.treatment;

  const labels = ['Control', 'Treatment'];
  const rates  = [ctrl.rate * 100, trt.rate * 100];
  const ciLow  = [pm.control_ci.lower * 100,   pm.treatment_ci.lower * 100];
  const ciHigh = [pm.control_ci.upper * 100,   pm.treatment_ci.upper * 100];

  const errLow  = rates.map((r, i) => r - ciLow[i]);
  const errHigh = rates.map((r, i) => ciHigh[i] - r);

  const ctx = document.getElementById('convChart').getContext('2d');
  if (convChart) convChart.destroy();
  convChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Cart Conversion Rate (%)',
        data: rates,
        backgroundColor: ['#6366f1cc', '#f59e0bcc'],
        borderColor:     ['#4f46e5',   '#d97706'],
        borderWidth: 2,
        borderRadius: 6,
        errorBars: { '0': { plus: errHigh[0], minus: errLow[0] },
                     '1': { plus: errHigh[1], minus: errLow[1] } },
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            afterLabel: (ctx) => {
              const i = ctx.dataIndex;
              return `95% CI: [${ciLow[i].toFixed(2)}%, ${ciHigh[i].toFixed(2)}%]`;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { callback: v => v.toFixed(1) + '%' },
          title: { display: true, text: 'Add-to-Cart Rate (%)' },
        }
      }
    }
  });

  // manually draw error bars (Chart.js 4 doesn't have built-in error bars)
  // Use the after-draw plugin
  convChart.options.animation = { onComplete: () => drawErrBars(convChart, errLow, errHigh) };
  convChart.update();
}

function drawErrBars(chart, errLow, errHigh) {
  const ctx  = chart.ctx;
  const meta = chart.getDatasetMeta(0);
  ctx.save();
  ctx.strokeStyle = '#374151';
  ctx.lineWidth   = 2;
  meta.data.forEach((bar, i) => {
    const x    = bar.x;
    const yMid = bar.y;
    const pxPerUnit = chart.scales.y.height / (chart.scales.y.max - chart.scales.y.min);
    const hiPx = errHigh[i] * pxPerUnit;
    const loPx = errLow[i]  * pxPerUnit;
    ctx.beginPath();
    ctx.moveTo(x, yMid - hiPx);
    ctx.lineTo(x, yMid + loPx);
    [yMid - hiPx, yMid + loPx].forEach(y => {
      ctx.moveTo(x - 6, y);
      ctx.lineTo(x + 6, y);
    });
    ctx.stroke();
  });
  ctx.restore();
}

function renderTsChart(ts) {
  if (!ts || ts.length === 0) return;

  // Group by date
  const dates   = [...new Set(ts.map(r => r.date))].sort();
  const ctrl    = {}, trt = {};
  ts.forEach(r => {
    const rate = r.sessions > 0 ? (r.cart_sessions / r.sessions * 100) : 0;
    if (r.variant === 'control')   ctrl[r.date]  = rate;
    if (r.variant === 'treatment') trt[r.date]   = rate;
  });

  const ctx = document.getElementById('tsChart').getContext('2d');
  if (tsChart) tsChart.destroy();
  tsChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: dates,
      datasets: [
        {
          label: 'Control',
          data: dates.map(d => ctrl[d] ?? null),
          borderColor: '#6366f1', backgroundColor: '#6366f120',
          tension: 0.3, pointRadius: 4, fill: false,
        },
        {
          label: 'Treatment',
          data: dates.map(d => trt[d] ?? null),
          borderColor: '#f59e0b', backgroundColor: '#f59e0b20',
          tension: 0.3, pointRadius: 4, fill: false,
        },
      ]
    },
    options: {
      responsive: true,
      plugins: { legend: { position: 'bottom' } },
      scales: {
        y: { ticks: { callback: v => v.toFixed(1) + '%' },
             title: { display: true, text: 'Cart Rate (%)' } },
        x: { ticks: { maxRotation: 45 } }
      }
    }
  });
}

function renderStrategyTable(breakdown) {
  const tbody = document.getElementById('strategy-table');
  if (!breakdown || breakdown.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" class="py-4 text-center text-gray-400 italic">No click data yet — make sure analytics tracking is active.</td></tr>';
    return;
  }

  // Get total sessions per variant for CTR calculation
  tbody.innerHTML = breakdown.map(r => {
    const ctr = r.sessions > 0 ? (r.clicks / r.sessions * 100).toFixed(1) + '%' : '—';
    const variantBadge = r.variant === 'control'
      ? '<span class="pill bg-indigo-50 text-indigo-700">control</span>'
      : '<span class="pill bg-amber-50 text-amber-700">treatment</span>';
    return `
      <tr class="hover:bg-gray-50">
        <td class="py-2 pr-4 font-mono text-xs text-gray-700">${r.strategy}</td>
        <td class="py-2 pr-4">${variantBadge}</td>
        <td class="py-2 pr-4 text-right text-gray-700">${r.clicks.toLocaleString()}</td>
        <td class="py-2 text-right font-semibold text-gray-900">${ctr}</td>
      </tr>`;
  }).join('');
}

function renderSecondaryMetrics(metrics) {
  const div = document.getElementById('secondary-metrics');
  if (!metrics || metrics.length === 0) {
    div.innerHTML = '<p class="text-gray-400 italic">No data</p>';
    return;
  }
  div.innerHTML = metrics.map(m => `
    <div class="border-l-2 border-gray-200 pl-3">
      <div class="font-medium text-gray-700">${m.metric.replace(/_/g,' ')}</div>
      <div class="flex gap-4 mt-1">
        <span class="text-indigo-600">C: ${pct(m.control.rate)}</span>
        <span class="text-amber-500">T: ${pct(m.treatment.rate)}</span>
        <span class="${m.relative_lift_pct >= 0 ? 'text-green-600' : 'text-red-500'} font-semibold">
          ${m.relative_lift_pct >= 0 ? '+' : ''}${m.relative_lift_pct}%
        </span>
      </div>
      <div class="text-gray-400 text-xs mt-0.5">p=${fmt(m.p_value,4)} · ${m.is_significant ? '✓ sig' : '✗ not sig'}</div>
    </div>
  `).join('');
}

async function load() {
  document.getElementById('status-dot').style.background = '#fbbf24';
  try {
    const res = await fetch('/api/ab/results');
    if (!res.ok) throw new Error(res.statusText);
    const data = await res.json();

    const pm   = data.primary_metric;
    const cfg  = data.experiment;

    // ── Header ───────────────────────────────────────────────────────────────
    document.getElementById('exp-name').textContent = cfg.name;
    document.getElementById('exp-desc').textContent = cfg.description;

    // ── Config panel ──────────────────────────────────────────────────────────
    document.getElementById('exp-id').textContent       = cfg.id;
    document.getElementById('traffic-split').textContent = `${(cfg.traffic_split * 100).toFixed(0)}% treatment`;
    document.getElementById('mde').textContent           = `${(cfg.minimum_detectable_effect * 100).toFixed(0)} pp`;
    document.getElementById('req-n').textContent         = pm.required_sample_size
      ? pm.required_sample_size.toLocaleString()
      : '—';
    document.getElementById('ctrl-desc').textContent = cfg.control_description;
    document.getElementById('trt-desc').textContent  = cfg.treatment_description;

    // ── Summary cards ─────────────────────────────────────────────────────────
    document.getElementById('c-sessions').textContent  = pm.control.sessions.toLocaleString();
    document.getElementById('t-sessions').textContent  = pm.treatment.sessions.toLocaleString();
    document.getElementById('c-cart-rate').textContent = pct(pm.control.rate);
    document.getElementById('t-cart-rate').textContent = pct(pm.treatment.rate);

    const lift = pm.relative_lift_pct;
    const liftEl = document.getElementById('rel-lift');
    liftEl.textContent  = (lift >= 0 ? '+' : '') + lift.toFixed(1) + '%';
    liftEl.className    = `text-3xl font-bold ${lift > 0 ? 'text-green-600' : lift < 0 ? 'text-red-500' : 'text-gray-700'}`;

    // ── Verdict banner ─────────────────────────────────────────────────────────
    const banner = document.getElementById('verdict-banner');
    banner.classList.remove('hidden');
    const bayes   = pm.bayesian_prob_treatment_wins;
    document.getElementById('bayes-prob').textContent = (bayes * 100).toFixed(1) + '%';

    if (pm.is_significant && pm.meets_mde) {
      banner.className = 'card p-5 mb-6 flex items-start gap-4 bg-green-50 border border-green-200';
      document.getElementById('verdict-icon').textContent  = lift > 0 ? '🎉' : '⚠️';
      document.getElementById('verdict-title').textContent = lift > 0
        ? 'Treatment wins — statistically & practically significant!'
        : 'Control wins — treatment is significantly worse.';
    } else if (pm.is_significant) {
      banner.className = 'card p-5 mb-6 flex items-start gap-4 bg-yellow-50 border border-yellow-200';
      document.getElementById('verdict-icon').textContent  = '⚡';
      document.getElementById('verdict-title').textContent = 'Statistically significant, but effect is below MDE.';
    } else if (pm.is_underpowered) {
      banner.className = 'card p-5 mb-6 flex items-start gap-4 bg-blue-50 border border-blue-200';
      document.getElementById('verdict-icon').textContent  = '⏳';
      document.getElementById('verdict-title').textContent = 'Collecting data — test is underpowered.';
    } else {
      banner.className = 'card p-5 mb-6 flex items-start gap-4 bg-gray-50 border border-gray-200';
      document.getElementById('verdict-icon').textContent  = '🔍';
      document.getElementById('verdict-title').textContent = 'No significant difference yet.';
    }
    document.getElementById('verdict-msg').textContent = pm.practical_significance_msg;

    // ── Statistical detail ─────────────────────────────────────────────────────
    document.getElementById('z-stat').textContent    = fmt(pm.z_statistic, 3);
    document.getElementById('p-val').textContent     = fmt(pm.p_value, 4);
    document.getElementById('conf').textContent      = (pm.confidence_level * 100).toFixed(0) + '%';
    document.getElementById('abs-lift').textContent  = (pm.absolute_lift * 100).toFixed(2) + ' pp';
    document.getElementById('cohens-h').textContent  = fmt(pm.cohens_h, 3);
    document.getElementById('effect-label').textContent = pm.effect_size_label;
    document.getElementById('c-ci').textContent = `[${pct(pm.control_ci.lower)}, ${pct(pm.control_ci.upper)}]`;
    document.getElementById('t-ci').textContent = `[${pct(pm.treatment_ci.lower)}, ${pct(pm.treatment_ci.upper)}]`;

    const powerBadge = document.getElementById('power-badge');
    document.getElementById('power-msg').textContent = pm.practical_significance_msg;
    if (pm.is_underpowered) {
      powerBadge.className   = 'pill badge-low';
      powerBadge.textContent = 'Underpowered';
    } else {
      powerBadge.className   = 'pill badge-sig';
      powerBadge.textContent = 'Adequately powered';
    }

    // ── Charts ────────────────────────────────────────────────────────────────
    renderConvChart(data);
    renderTsChart(data.time_series);
    renderStrategyTable(data.strategy_breakdown);
    renderSecondaryMetrics(data.secondary_metrics);

    // ── Status ────────────────────────────────────────────────────────────────
    document.getElementById('status-dot').style.background = '#22c55e';
    document.getElementById('last-updated').textContent =
      'Updated ' + new Date().toLocaleTimeString();

  } catch (err) {
    document.getElementById('status-dot').style.background = '#ef4444';
    document.getElementById('last-updated').textContent = 'Error: ' + err.message;
    console.error(err);
  }
}

// Initial load + auto-refresh every 30 s
load();
setInterval(load, 30_000);
</script>
</body>
</html>
"""
