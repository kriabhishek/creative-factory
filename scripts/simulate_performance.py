#!/usr/bin/env python3
"""
Performance data simulator for Creative Factory.

Generates realistic mock performance data that demonstrates:
- Creative fatigue (CTR decay over time)
- CAC shifts (CPA spikes from competitive pressure)
- Payback drift (conversion quality degradation)
- Geo variance (different performance by market)
- Winner/loser separation in A/B tests

Usage:
    python3 simulate_performance.py              # Generate full dataset
    python3 simulate_performance.py --alerts     # Generate data + trigger alerts
    python3 simulate_performance.py --seed 42    # Reproducible output
"""

import json
import math
import random
import sys
import os
from datetime import datetime, timedelta

DATA_DIR = os.path.expanduser("~/.claude/data/creative-factory")
METRICS_FILE = os.path.join(DATA_DIR, "performance", "metrics.json")
ALERTS_FILE = os.path.join(DATA_DIR, "performance", "alerts.json")
ALLOCATION_FILE = os.path.join(DATA_DIR, "performance", "allocation.json")


def fatigue_curve(day, peak_ctr, onset_day, decline_type="gradual"):
    """Model creative fatigue as CTR decay over time."""
    if day < onset_day:
        # Pre-fatigue: slight random walk around peak
        noise = random.gauss(0, peak_ctr * 0.03)
        return max(0.001, peak_ctr + noise)

    days_past_onset = day - onset_day

    if decline_type == "gradual":
        # Exponential decay: -2% per day past onset
        decay = math.exp(-0.02 * days_past_onset)
        noise = random.gauss(0, peak_ctr * 0.02)
        return max(0.001, peak_ctr * decay + noise)
    elif decline_type == "cliff":
        # Sharp cliff: -7% per day past onset
        decay = math.exp(-0.07 * days_past_onset)
        noise = random.gauss(0, peak_ctr * 0.02)
        return max(0.001, peak_ctr * decay + noise)
    else:
        # Slow: -0.8% per day
        decay = math.exp(-0.008 * days_past_onset)
        noise = random.gauss(0, peak_ctr * 0.015)
        return max(0.001, peak_ctr * decay + noise)


def cpa_shift(day, base_cpa, spike_day, spike_magnitude=1.6):
    """Model CPA spike from competitive pressure."""
    if day < spike_day:
        noise = random.gauss(0, base_cpa * 0.05)
        return max(1.0, base_cpa + noise)

    days_past_spike = day - spike_day
    # Gradual ramp up to spike magnitude over 7 days
    progress = min(1.0, days_past_spike / 7.0)
    current_multiplier = 1.0 + (spike_magnitude - 1.0) * progress
    noise = random.gauss(0, base_cpa * 0.08)
    return max(1.0, base_cpa * current_multiplier + noise)


def generate_daily_metrics(start_date, n_days=21):
    """Generate daily performance metrics across channels/geos."""
    metrics = {"generated": datetime.now().isoformat(), "days": []}

    for day_offset in range(n_days):
        date = start_date + timedelta(days=day_offset)
        day_data = {
            "date": date.strftime("%Y-%m-%d"),
            "channels": {}
        }

        # Paid Search - US - Developer
        day_data["channels"]["paid_search_us_developer"] = {
            "channel": "paid_search", "geo": "us", "segment": "developer",
            "impressions": random.randint(2800, 3200),
            "clicks": 0, "signups": 0, "first_app": 0, "paid": 0,
            "spend": round(random.uniform(380, 420), 2),
            "ctr": 0, "cpa": 0, "cvr": 0
        }
        d = day_data["channels"]["paid_search_us_developer"]
        ctr = fatigue_curve(day_offset, 0.042, 18, "cliff")
        d["ctr"] = round(ctr, 5)
        d["clicks"] = max(1, int(d["impressions"] * ctr))
        d["cvr"] = round(random.uniform(0.12, 0.16), 4)
        d["signups"] = max(0, int(d["clicks"] * d["cvr"]))
        d["first_app"] = max(0, int(d["signups"] * random.uniform(0.55, 0.65)))
        d["paid"] = max(0, int(d["first_app"] * random.uniform(0.18, 0.25)))
        d["cpa"] = round(d["spend"] / max(1, d["signups"]), 2)

        # Paid Search - India - All
        day_data["channels"]["paid_search_in_all"] = {
            "channel": "paid_search", "geo": "in", "segment": "all",
            "impressions": random.randint(5000, 6000),
            "clicks": 0, "signups": 0, "first_app": 0, "paid": 0,
            "spend": round(random.uniform(80, 120), 2),
            "ctr": 0, "cpa": 0, "cvr": 0
        }
        d = day_data["channels"]["paid_search_in_all"]
        d["ctr"] = round(random.uniform(0.028, 0.035), 5)
        d["clicks"] = max(1, int(d["impressions"] * d["ctr"]))
        # CPA spike in India starting day 14
        d["cpa"] = round(cpa_shift(day_offset, 7.20, 14, 1.58), 2)
        d["signups"] = max(1, int(d["spend"] / d["cpa"]))
        d["cvr"] = round(d["signups"] / max(1, d["clicks"]), 4)
        d["first_app"] = max(0, int(d["signups"] * random.uniform(0.25, 0.35)))
        d["paid"] = max(0, int(d["first_app"] * random.uniform(0.08, 0.12)))

        # Paid Social - US - Non-Technical
        day_data["channels"]["paid_social_us_non_technical"] = {
            "channel": "paid_social", "geo": "us", "segment": "non_technical_builder",
            "impressions": random.randint(8000, 10000),
            "clicks": 0, "signups": 0, "first_app": 0, "paid": 0,
            "spend": round(random.uniform(450, 550), 2),
            "ctr": 0, "cpa": 0, "cvr": 0
        }
        d = day_data["channels"]["paid_social_us_non_technical"]
        ctr = fatigue_curve(day_offset, 0.048, 12, "gradual")
        d["ctr"] = round(ctr, 5)
        d["clicks"] = max(1, int(d["impressions"] * ctr))
        d["cvr"] = round(random.uniform(0.14, 0.18), 4)
        d["signups"] = max(0, int(d["clicks"] * d["cvr"]))
        d["first_app"] = max(0, int(d["signups"] * random.uniform(0.40, 0.50)))
        d["paid"] = max(0, int(d["first_app"] * random.uniform(0.15, 0.22)))
        d["cpa"] = round(d["spend"] / max(1, d["signups"]), 2)

        # Paid Social - India - Student
        day_data["channels"]["paid_social_in_student"] = {
            "channel": "paid_social", "geo": "in", "segment": "student",
            "impressions": random.randint(12000, 15000),
            "clicks": 0, "signups": 0, "first_app": 0, "paid": 0,
            "spend": round(random.uniform(60, 80), 2),
            "ctr": 0, "cpa": 0, "cvr": 0
        }
        d = day_data["channels"]["paid_social_in_student"]
        d["ctr"] = round(random.uniform(0.030, 0.045), 5)
        d["clicks"] = max(1, int(d["impressions"] * d["ctr"]))
        d["cvr"] = round(random.uniform(0.035, 0.045), 4)
        d["signups"] = max(0, int(d["clicks"] * d["cvr"]))
        # Low activation rate (INS-017)
        d["first_app"] = max(0, int(d["signups"] * random.uniform(0.06, 0.10)))
        d["paid"] = 0
        d["cpa"] = round(d["spend"] / max(1, d["signups"]), 2)

        # Paid Search - EU - Enterprise
        day_data["channels"]["paid_search_eu_enterprise"] = {
            "channel": "paid_search", "geo": "eu", "segment": "enterprise_team",
            "impressions": random.randint(1500, 2000),
            "clicks": 0, "signups": 0, "first_app": 0, "paid": 0,
            "spend": round(random.uniform(280, 340), 2),
            "ctr": 0, "cpa": 0, "cvr": 0
        }
        d = day_data["channels"]["paid_search_eu_enterprise"]
        d["ctr"] = round(fatigue_curve(day_offset, 0.025, 25, "slow"), 5)
        d["clicks"] = max(1, int(d["impressions"] * d["ctr"]))
        d["cvr"] = round(random.uniform(0.06, 0.10), 4)
        d["signups"] = max(0, int(d["clicks"] * d["cvr"]))
        d["first_app"] = max(0, int(d["signups"] * random.uniform(0.45, 0.55)))
        d["paid"] = max(0, int(d["first_app"] * random.uniform(0.25, 0.35)))
        d["cpa"] = round(d["spend"] / max(1, d["signups"]), 2)

        # Lifecycle - All
        day_data["channels"]["lifecycle_all"] = {
            "channel": "lifecycle", "geo": "all", "segment": "all",
            "emails_sent": random.randint(4000, 5000),
            "opens": 0, "clicks": 0, "activations": 0,
            "open_rate": 0, "click_rate": 0, "activation_rate": 0
        }
        d = day_data["channels"]["lifecycle_all"]
        d["open_rate"] = round(random.uniform(0.32, 0.38), 4)
        d["opens"] = int(d["emails_sent"] * d["open_rate"])
        d["click_rate"] = round(random.uniform(0.08, 0.12), 4)
        d["clicks"] = int(d["opens"] * d["click_rate"])
        d["activation_rate"] = round(random.uniform(0.25, 0.35), 4)
        d["activations"] = int(d["clicks"] * d["activation_rate"])

        metrics["days"].append(day_data)

    return metrics


def generate_alerts(metrics):
    """Analyze metrics and generate performance alerts."""
    alerts = {"active_alerts": [], "alert_rules": {
        "creative_fatigue": {"metric": "ctr", "decline_pct": 20, "window_days": 14},
        "cac_shift": {"metric": "cpa", "increase_pct": 30, "window_days": 7},
        "payback_drift": {"metric": "payback_days", "increase_pct": 25, "window_days": 14},
        "conversion_quality": {"metric": "signup_to_paid_rate", "decline_pct": 15, "window_days": 7}
    }}

    days = metrics["days"]
    if len(days) < 7:
        return alerts

    # Check paid social US non-tech for fatigue
    recent_ctrs = [d["channels"]["paid_social_us_non_technical"]["ctr"] for d in days[-5:]]
    peak_ctrs = [d["channels"]["paid_social_us_non_technical"]["ctr"] for d in days[:5]]
    avg_recent = sum(recent_ctrs) / len(recent_ctrs)
    avg_peak = sum(peak_ctrs) / len(peak_ctrs)

    if avg_peak > 0 and (avg_peak - avg_recent) / avg_peak > 0.20:
        decline_pct = round((avg_peak - avg_recent) / avg_peak * 100, 1)
        alerts["active_alerts"].append({
            "id": f"ALT-{random.randint(100, 999)}",
            "type": "creative_fatigue",
            "severity": "warning",
            "detected": datetime.now().isoformat(),
            "creative_id": "V-049",
            "channel": "paid_social",
            "geo": "us",
            "segment": "non_technical_builder",
            "signal": f"CTR declined {decline_pct}% over {len(days)} days ({avg_peak:.3%} -> {avg_recent:.3%}). Fatigue threshold: 20% decline over 14 days.",
            "recommendation": "Rotate creative. Generate fresh variants from creative-dna.json using before/after transformation format (INS-007). Current static image format is fatiguing.",
            "auto_action": "pause_and_regenerate",
            "status": "pending_approval"
        })

    # Check India paid search for CPA spike
    recent_cpas = [d["channels"]["paid_search_in_all"]["cpa"] for d in days[-3:]]
    baseline_cpas = [d["channels"]["paid_search_in_all"]["cpa"] for d in days[:7]]
    avg_recent_cpa = sum(recent_cpas) / len(recent_cpas)
    avg_baseline_cpa = sum(baseline_cpas) / len(baseline_cpas)

    if avg_baseline_cpa > 0 and (avg_recent_cpa - avg_baseline_cpa) / avg_baseline_cpa > 0.30:
        increase_pct = round((avg_recent_cpa - avg_baseline_cpa) / avg_baseline_cpa * 100, 1)
        alerts["active_alerts"].append({
            "id": f"ALT-{random.randint(100, 999)}",
            "type": "cac_shift",
            "severity": "critical",
            "detected": datetime.now().isoformat(),
            "channel": "paid_search",
            "geo": "in",
            "segment": "all",
            "signal": f"CPA increased from ${avg_baseline_cpa:.2f} to ${avg_recent_cpa:.2f} (+{increase_pct}%) in India over {len(days)} days. Target: $8.00.",
            "recommendation": "Investigate: (1) competitor bid increase (Bolt/Lovable entering India), (2) audience saturation, (3) keyword competition. Recommend shifting 30% of India search budget to social where CPA is stable (INS-021). Also test new geo-specific creatives with 'free' hook (INS-010).",
            "status": "active"
        })

    # Check LATAM payback drift
    alerts["active_alerts"].append({
        "id": f"ALT-{random.randint(100, 999)}",
        "type": "payback_drift",
        "severity": "warning",
        "detected": datetime.now().isoformat(),
        "channel": "paid_social",
        "geo": "latam",
        "segment": "all",
        "signal": "LATAM payback period drifted from 72 to 91 days over 14 days. Approaching 90-day target. Conversion-to-paid rate declining.",
        "recommendation": "Tighten audience targeting. Consider lifecycle messaging adjustments for LATAM cohort. Review if mobile-first creative is driving low-intent signups.",
        "status": "active"
    })

    return alerts


def generate_allocation():
    """Generate Thompson Sampling allocation state."""
    return {
        "last_updated": datetime.now().isoformat(),
        "arms": [
            {
                "id": "V-045",
                "experiment_id": "EXP-008",
                "alpha": 157,
                "beta": 6045,
                "impressions": 6200,
                "conversions": 156,
                "allocated_pct": 0.35,
                "estimated_value": 0.0253
            },
            {
                "id": "V-046",
                "experiment_id": "EXP-008",
                "alpha": 199,
                "beta": 6003,
                "impressions": 6200,
                "conversions": 198,
                "allocated_pct": 0.65,
                "estimated_value": 0.0321
            }
        ],
        "exploration_rate": 0.15,
        "total_budget_allocated": 25000,
        "rebalance_frequency_hours": 6
    }


def main():
    seed = 42
    for i, arg in enumerate(sys.argv):
        if arg == "--seed" and i + 1 < len(sys.argv):
            seed = int(sys.argv[i + 1])
    random.seed(seed)

    start_date = datetime(2026, 3, 3)
    n_days = 21

    print("Generating performance data...")
    metrics = generate_daily_metrics(start_date, n_days)

    # Save metrics
    os.makedirs(os.path.dirname(METRICS_FILE), exist_ok=True)
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {METRICS_FILE}")
    print(f"  {n_days} days of data across 6 channel/geo/segment combos")

    # Generate and save alerts
    if "--alerts" in sys.argv or True:  # Always generate for demo
        alerts = generate_alerts(metrics)
        with open(ALERTS_FILE, "w") as f:
            json.dump(alerts, f, indent=2)
        print(f"Alerts saved to {ALERTS_FILE}")
        print(f"  {len(alerts['active_alerts'])} active alerts")
        for alert in alerts["active_alerts"]:
            severity = alert["severity"].upper()
            print(f"    [{severity}] {alert['type']}: {alert['channel']}/{alert['geo']} — {alert['signal'][:80]}...")

    # Generate and save allocation state
    allocation = generate_allocation()
    with open(ALLOCATION_FILE, "w") as f:
        json.dump(allocation, f, indent=2)
    print(f"Allocation saved to {ALLOCATION_FILE}")

    # Summary stats
    total_spend = 0
    total_signups = 0
    for day in metrics["days"]:
        for key, ch in day["channels"].items():
            total_spend += ch.get("spend", 0)
            total_signups += ch.get("signups", 0)

    print(f"\nSummary:")
    print(f"  Period: {start_date.strftime('%Y-%m-%d')} to {(start_date + timedelta(days=n_days-1)).strftime('%Y-%m-%d')}")
    print(f"  Total spend: ${total_spend:,.2f}")
    print(f"  Total signups: {total_signups:,}")
    print(f"  Blended CPA: ${total_spend / max(1, total_signups):.2f}")


if __name__ == "__main__":
    main()
