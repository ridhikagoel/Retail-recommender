"""
A/B Testing Agent — deterministic per-session variant assignment.

Assignment is hash-based: given an experiment_id + session_id, the variant is
always the same for that session with no DB lookup required.  This ensures a
consistent experience across page loads while enabling true simultaneous traffic
splitting (unlike the previous env-var approach that assigns ALL users to one
variant).

Env vars:
  AB_TESTING_ENABLED   "true" / "false"  (default false)
  AB_EXPERIMENT_ID     string            (default "exp_reco_v1")
  AB_TRAFFIC_SPLIT     0.0–1.0           fraction routed to TREATMENT (default 0.5)
"""

import hashlib
import os
from typing import Literal

# ── Config ─────────────────────────────────────────────────────────────────

AB_TESTING_ENABLED: bool = os.getenv("AB_TESTING_ENABLED", "false").lower() == "true"
EXPERIMENT_ID: str       = os.getenv("AB_EXPERIMENT_ID", "exp_reco_v1")
TRAFFIC_SPLIT: float     = float(os.getenv("AB_TRAFFIC_SPLIT", "0.5"))

# ── Experiment metadata ─────────────────────────────────────────────────────

EXPERIMENT_META: dict = {
    "id":   EXPERIMENT_ID,
    "name": "Recommendation Strategy A/B Test",
    "description": (
        "Control: personalised collaborative-filtering + velocity-based trending. "
        "Treatment: best-sellers (popularity) replaces both personalised and trending sections."
    ),
    "control_description":   "Collaborative filtering + velocity-based trending",
    "treatment_description": "Best sellers (popularity) for personalised + trending",
    "primary_metric":        "add_to_cart_rate",
    "secondary_metrics":     ["click_through_rate", "cart_per_click"],
    "traffic_split":         TRAFFIC_SPLIT,
    "minimum_detectable_effect": 0.02,   # 2 pp absolute lift to declare a winner
    "confidence_threshold":      0.95,
    "ab_testing_enabled":    AB_TESTING_ENABLED,
}

# ── Core function ───────────────────────────────────────────────────────────

def assign_variant(session_id: str) -> Literal["control", "treatment"]:
    """
    Deterministically assign a variant for a session.

    Hash(experiment_id + ":" + session_id) → integer → bucket [0, 1000).
    Buckets 0..(split*1000 - 1) → treatment; rest → control.

    When AB_TESTING_ENABLED is False every session is always "control".
    """
    if not AB_TESTING_ENABLED:
        return "control"

    key    = f"{EXPERIMENT_ID}:{session_id}"
    digest = int(hashlib.md5(key.encode()).hexdigest(), 16)
    bucket = (digest % 1000) / 1000.0          # uniform in [0.000, 0.999]
    return "treatment" if bucket < TRAFFIC_SPLIT else "control"
