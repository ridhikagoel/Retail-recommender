"""
Statistical engine for A/B test analysis.

Implements all tests from scratch using only the Python standard library so
no extra dependencies are required (numpy / scipy are NOT used here).

Tests use two-sided hypothesis testing throughout.
"""

import math
import random
from dataclasses import dataclass, field
from typing import Optional


# ── Normal distribution helpers ─────────────────────────────────────────────

def _normal_cdf(z: float) -> float:
    """CDF of the standard normal distribution."""
    return 0.5 * math.erfc(-z / math.sqrt(2))


def _normal_ppf(p: float) -> float:
    """
    Percent-point function (inverse CDF) of the standard normal.
    Beasley–Springer–Moro rational approximation.
    """
    c = [-7.784894002430293e-03, -3.223964580411365e-01,
         -2.400758277161838e+00, -2.549732539343734e+00,
          4.374664141464968e+00,  2.938163982698783e+00]
    d = [ 7.784695709041462e-03,  3.224671290700398e-01,
          2.445134137142996e+00,  3.754408661907416e+00]

    p_low, p_high = 0.02425, 1 - 0.02425

    if p < p_low:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    elif p <= p_high:
        a = [ 0, -3.969683028665376e+01,  2.209460984245205e+02,
             -2.759285104469687e+02,  1.383577518672690e+02,
             -3.066479806614716e+01,  2.506628277459239e+00]
        b = [ 0, -5.447609879822406e+01,  1.615858368580409e+02,
             -1.556989798598866e+02,  6.680131188771972e+01,
             -1.328068155288572e+01]
        q = p - 0.5
        r = q * q
        return (((((a[1]*r+a[2])*r+a[3])*r+a[4])*r+a[5])*r+a[6])*q / \
               (((((b[1]*r+b[2])*r+b[3])*r+b[4])*r+b[5])*r+1)
    else:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)


# ── Data classes ────────────────────────────────────────────────────────────

@dataclass
class VariantStats:
    sessions:    int
    conversions: int

    @property
    def rate(self) -> float:
        return self.conversions / self.sessions if self.sessions > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "sessions":    self.sessions,
            "conversions": self.conversions,
            "rate":        round(self.rate, 6),
        }


@dataclass
class MetricResult:
    """Full statistical analysis for one metric."""
    metric: str

    # Raw data
    control:   VariantStats
    treatment: VariantStats

    # Frequentist
    z_statistic:      float
    p_value:          float
    confidence_level: float
    is_significant:   bool

    # Magnitude
    absolute_lift:     float   # treatment_rate − control_rate
    relative_lift_pct: float   # ((t − c) / c) × 100
    cohens_h:          float   # effect size for proportions

    # 95 % Wilson confidence intervals
    control_ci_lower:   float
    control_ci_upper:   float
    treatment_ci_lower: float
    treatment_ci_upper: float

    # Bayesian
    bayesian_prob_treatment_wins: float   # P(θ_T > θ_C)

    # Power analysis
    required_sample_size: Optional[int]
    is_underpowered:      bool

    # Practical significance
    meets_mde:                  bool
    effect_size_label:          str   # "negligible" / "small" / "medium" / "large"
    practical_significance_msg: str

    def to_dict(self) -> dict:
        return {
            "metric":            self.metric,
            "control":           self.control.to_dict(),
            "treatment":         self.treatment.to_dict(),
            "z_statistic":       self.z_statistic,
            "p_value":           self.p_value,
            "confidence_level":  self.confidence_level,
            "is_significant":    self.is_significant,
            "absolute_lift":     self.absolute_lift,
            "relative_lift_pct": self.relative_lift_pct,
            "cohens_h":          self.cohens_h,
            "control_ci": {
                "lower": self.control_ci_lower,
                "upper": self.control_ci_upper,
            },
            "treatment_ci": {
                "lower": self.treatment_ci_lower,
                "upper": self.treatment_ci_upper,
            },
            "bayesian_prob_treatment_wins": self.bayesian_prob_treatment_wins,
            "required_sample_size":         self.required_sample_size,
            "is_underpowered":              self.is_underpowered,
            "meets_mde":                    self.meets_mde,
            "effect_size_label":            self.effect_size_label,
            "practical_significance_msg":   self.practical_significance_msg,
        }


# ── Statistical helpers ─────────────────────────────────────────────────────

def _wilson_ci(n: int, k: int, confidence: float = 0.95) -> tuple[float, float]:
    """Wilson score confidence interval for a proportion k/n."""
    if n == 0:
        return 0.0, 0.0
    z     = _normal_ppf(1 - (1 - confidence) / 2)
    p_hat = k / n
    denom = 1 + z ** 2 / n
    centre = p_hat + z ** 2 / (2 * n)
    spread = math.sqrt((p_hat * (1 - p_hat) + z ** 2 / (4 * n)) / n)
    return (
        max(0.0, (centre - z * spread) / denom),
        min(1.0, (centre + z * spread) / denom),
    )


def _cohens_h(p1: float, p2: float) -> float:
    """Cohen's h effect size between two proportions."""
    return abs(2 * math.asin(math.sqrt(max(p1, 1e-10)))
               - 2 * math.asin(math.sqrt(max(p2, 1e-10))))


def _effect_size_label(h: float) -> str:
    """Interpret Cohen's h."""
    if h < 0.20:
        return "negligible"
    if h < 0.50:
        return "small"
    if h < 0.80:
        return "medium"
    return "large"


def _bayesian_prob(
    n_control: int,   conv_control: int,
    n_treatment: int, conv_treatment: int,
    n_samples: int = 10_000,
) -> float:
    """
    P(θ_treatment > θ_control) via Beta-posterior Monte Carlo.

    Posteriors:  θ_C ~ Beta(1 + conv_C,  1 + failures_C)
                 θ_T ~ Beta(1 + conv_T,  1 + failures_T)
    """
    alpha_c = 1 + conv_control
    beta_c  = 1 + max(n_control - conv_control, 0)
    alpha_t = 1 + conv_treatment
    beta_t  = 1 + max(n_treatment - conv_treatment, 0)

    def _beta(a: float, b: float) -> float:
        x = random.gammavariate(a, 1)
        y = random.gammavariate(b, 1)
        return x / (x + y)

    wins = sum(
        _beta(alpha_t, beta_t) > _beta(alpha_c, beta_c)
        for _ in range(n_samples)
    )
    return wins / n_samples


def _required_n(baseline: float, mde: float,
                alpha: float = 0.05, power: float = 0.80) -> int:
    """
    Minimum sample size per variant for a two-proportion z-test.

    baseline : control conversion rate
    mde      : minimum detectable effect (absolute, e.g. 0.02 = 2 pp)
    """
    if baseline <= 0 or mde <= 0:
        return 0
    p1 = baseline
    p2 = min(baseline + mde, 0.9999)
    z_alpha = _normal_ppf(1 - alpha / 2)
    z_beta  = _normal_ppf(power)
    pool    = (p1 + p2) / 2
    n = (
        z_alpha * math.sqrt(2 * pool * (1 - pool)) +
        z_beta  * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
    ) ** 2 / mde ** 2
    return math.ceil(n)


# ── Main analysis function ───────────────────────────────────────────────────

def run_test(
    metric:          str,
    n_control:       int,
    conv_control:    int,
    n_treatment:     int,
    conv_treatment:  int,
    confidence:      float = 0.95,
    mde:             float = 0.02,
) -> MetricResult:
    """
    Run a two-proportion z-test and return a complete MetricResult.

    Parameters
    ----------
    metric        : human-readable name, e.g. "add_to_cart_rate"
    n_*           : total sessions per variant
    conv_*        : converting sessions per variant
    confidence    : desired confidence level (default 0.95)
    mde           : minimum detectable effect in absolute terms (default 0.02)
    """
    ctrl = VariantStats(n_control,   conv_control)
    trt  = VariantStats(n_treatment, conv_treatment)

    p_c, p_t = ctrl.rate, trt.rate

    # ── Two-proportion z-test ────────────────────────────────────────────────
    total = n_control + n_treatment
    if total == 0 or (p_c == 0 and p_t == 0):
        z, p_value = 0.0, 1.0
    else:
        p_pool = (conv_control + conv_treatment) / total
        se     = math.sqrt(
            p_pool * (1 - p_pool) * (1 / max(n_control, 1) + 1 / max(n_treatment, 1))
        )
        z      = (p_t - p_c) / se if se > 0 else 0.0
        p_value = 2 * (1 - _normal_cdf(abs(z)))   # two-sided

    is_significant = p_value < (1 - confidence)

    # ── Effect size ──────────────────────────────────────────────────────────
    absolute_lift     = p_t - p_c
    relative_lift_pct = ((p_t - p_c) / p_c * 100) if p_c > 0 else 0.0
    h                 = _cohens_h(p_t, p_c)
    h_label           = _effect_size_label(h)

    # ── Confidence intervals ─────────────────────────────────────────────────
    c_lo, c_hi = _wilson_ci(n_control,   conv_control,   confidence)
    t_lo, t_hi = _wilson_ci(n_treatment, conv_treatment, confidence)

    # ── Bayesian ─────────────────────────────────────────────────────────────
    bayes = _bayesian_prob(n_control, conv_control, n_treatment, conv_treatment)

    # ── Power analysis ───────────────────────────────────────────────────────
    baseline = p_c if p_c > 0 else 0.05
    req_n    = _required_n(baseline, mde)
    underpowered = (n_control < req_n) or (n_treatment < req_n)

    # ── Practical significance ───────────────────────────────────────────────
    meets_mde = abs(absolute_lift) >= mde
    if not is_significant and underpowered:
        ps_msg = (
            f"Insufficient data — need ≥{req_n:,} sessions per variant "
            f"(have {min(n_control, n_treatment):,}). Collect more data before concluding."
        )
    elif is_significant and meets_mde:
        direction = "better" if absolute_lift > 0 else "worse"
        ps_msg = (
            f"Treatment is statistically AND practically significant "
            f"({relative_lift_pct:+.1f}% lift, p={p_value:.4f}). "
            f"Treatment performs {direction}."
        )
    elif is_significant and not meets_mde:
        ps_msg = (
            f"Statistically significant (p={p_value:.4f}) but lift "
            f"({absolute_lift:+.3f}) is below the {mde:.0%} MDE threshold. "
            "Effect may not be meaningful in production."
        )
    else:
        days_needed = max(1, math.ceil(req_n / max(n_control, 1) * 7))
        ps_msg = (
            f"Not yet significant (p={p_value:.4f}). "
            f"Estimated ~{days_needed} more days at current traffic to reach power."
        )

    return MetricResult(
        metric=metric,
        control=ctrl,
        treatment=trt,
        z_statistic=round(z, 4),
        p_value=round(p_value, 6),
        confidence_level=confidence,
        is_significant=is_significant,
        absolute_lift=round(absolute_lift, 6),
        relative_lift_pct=round(relative_lift_pct, 2),
        cohens_h=round(h, 4),
        control_ci_lower=round(c_lo, 4),
        control_ci_upper=round(c_hi, 4),
        treatment_ci_lower=round(t_lo, 4),
        treatment_ci_upper=round(t_hi, 4),
        bayesian_prob_treatment_wins=round(bayes, 4),
        required_sample_size=req_n if req_n > 0 else None,
        is_underpowered=underpowered,
        meets_mde=meets_mde,
        effect_size_label=h_label,
        practical_significance_msg=ps_msg,
    )


# ── Convenience: analyse a full experiment ───────────────────────────────────

def analyse_experiment(
    variant_metrics: dict,          # output of analytics.get_variant_metrics()
    mde:        float = 0.02,
    confidence: float = 0.95,
) -> dict:
    """
    Run all standard A/B test metrics and return a dict ready for serialisation.

    variant_metrics expected shape:
        {
          "control":   {"sessions": int, "click_sessions": int, "cart_sessions": int, ...},
          "treatment": {"sessions": int, "click_sessions": int, "cart_sessions": int, ...},
        }
    """
    def _get(variant: str, key: str, default: int = 0) -> int:
        return int((variant_metrics.get(variant) or {}).get(key, default))

    n_c  = _get("control",   "sessions")
    n_t  = _get("treatment", "sessions")

    cart_c  = _get("control",   "cart_sessions")
    cart_t  = _get("treatment", "cart_sessions")
    click_c = _get("control",   "click_sessions")
    click_t = _get("treatment", "click_sessions")

    primary   = run_test("add_to_cart_rate",   n_c, cart_c,  n_t, cart_t,  confidence, mde)
    secondary = run_test("click_through_rate",  n_c, click_c, n_t, click_t, confidence, mde)

    # Cart-per-click (only among sessions that clicked)
    cpc_ctrl = run_test(
        "cart_per_click",
        click_c, cart_c,
        click_t, cart_t,
        confidence, mde,
    )

    return {
        "primary_metric":    primary.to_dict(),
        "secondary_metrics": [secondary.to_dict(), cpc_ctrl.to_dict()],
    }
