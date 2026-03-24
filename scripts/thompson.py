#!/usr/bin/env python3
"""
Thompson Sampling allocation engine for Creative Factory.

Takes current arm performance (alpha/beta from Beta distributions),
samples from each arm's posterior, and outputs new allocation percentages.

This is the "mathematical decision-making for spend allocation" that the JD asks for.

Usage:
    python3 thompson.py                          # Use default allocation.json
    python3 thompson.py --file path/to/alloc.json
    python3 thompson.py --simulate               # Demo mode with sample data
"""

import json
import random
import math
import sys
import os
from datetime import datetime

DATA_DIR = os.path.expanduser("~/.claude/data/creative-factory")
ALLOCATION_FILE = os.path.join(DATA_DIR, "performance", "allocation.json")


def beta_sample(alpha, beta_param):
    """Sample from Beta(alpha, beta) distribution using standard library."""
    return random.betavariate(alpha, beta_param)


def beta_mean(alpha, beta_param):
    """Expected value of Beta(alpha, beta)."""
    return alpha / (alpha + beta_param)


def beta_variance(alpha, beta_param):
    """Variance of Beta(alpha, beta)."""
    total = alpha + beta_param
    return (alpha * beta_param) / (total * total * (total + 1))


def probability_best(arms, n_samples=10000):
    """Estimate probability that each arm is the best via Monte Carlo sampling."""
    win_counts = {arm["id"]: 0 for arm in arms}

    for _ in range(n_samples):
        samples = {}
        for arm in arms:
            samples[arm["id"]] = beta_sample(arm["alpha"], arm["beta"])

        best_id = max(samples, key=samples.get)
        win_counts[best_id] += 1

    return {arm_id: count / n_samples for arm_id, count in win_counts.items()}


def thompson_allocate(arms, exploration_rate=0.15, n_samples=10000):
    """
    Run Thompson Sampling to determine budget allocation.

    Args:
        arms: list of arm dicts with alpha, beta, id fields
        exploration_rate: minimum allocation per arm (prevents zero exploration)
        n_samples: Monte Carlo samples for probability estimation

    Returns:
        dict with new allocations, probabilities, and recommendations
    """
    n_arms = len(arms)
    min_per_arm = exploration_rate / n_arms

    # Estimate probability each arm is best
    prob_best = probability_best(arms, n_samples)

    # Thompson allocation: proportional to probability of being best
    # with minimum exploration floor
    raw_alloc = {}
    for arm in arms:
        raw_alloc[arm["id"]] = max(prob_best[arm["id"]], min_per_arm)

    # Normalize to sum to 1.0
    total = sum(raw_alloc.values())
    allocations = {arm_id: alloc / total for arm_id, alloc in raw_alloc.items()}

    # Build results
    results = []
    for arm in arms:
        arm_id = arm["id"]
        expected = beta_mean(arm["alpha"], arm["beta"])
        variance = beta_variance(arm["alpha"], arm["beta"])
        ci_width = 1.96 * math.sqrt(variance)

        results.append({
            "id": arm_id,
            "alpha": arm["alpha"],
            "beta": arm["beta"],
            "impressions": arm.get("impressions", arm["alpha"] + arm["beta"] - 2),
            "conversions": arm.get("conversions", arm["alpha"] - 1),
            "expected_value": round(expected, 6),
            "ci_95_lower": round(max(0, expected - ci_width), 6),
            "ci_95_upper": round(min(1, expected + ci_width), 6),
            "prob_best": round(prob_best[arm_id], 4),
            "old_allocation": arm.get("allocated_pct", 1.0 / n_arms),
            "new_allocation": round(allocations[arm_id], 4),
            "allocation_change": round(allocations[arm_id] - arm.get("allocated_pct", 1.0 / n_arms), 4)
        })

    # Determine if we have a clear winner
    max_prob = max(r["prob_best"] for r in results)
    winner = next((r for r in results if r["prob_best"] == max_prob), None)
    confidence_in_winner = max_prob

    recommendation = "keep_exploring"
    if confidence_in_winner > 0.95:
        recommendation = f"declare_winner:{winner['id']}"
    elif confidence_in_winner > 0.80:
        recommendation = f"leaning:{winner['id']}"

    return {
        "timestamp": datetime.now().isoformat(),
        "arms": results,
        "recommendation": recommendation,
        "confidence_in_leader": round(confidence_in_winner, 4),
        "exploration_rate": exploration_rate,
        "n_samples": n_samples
    }


def format_output(result, total_budget=None):
    """Format Thompson Sampling results for human-readable output."""
    lines = []
    lines.append("=" * 60)
    lines.append("THOMPSON SAMPLING ALLOCATION UPDATE")
    lines.append("=" * 60)
    lines.append(f"Timestamp: {result['timestamp']}")
    lines.append(f"Exploration rate: {result['exploration_rate']:.0%}")
    lines.append(f"Monte Carlo samples: {result['n_samples']:,}")
    lines.append("")

    for arm in result["arms"]:
        lines.append(f"--- Arm: {arm['id']} ---")
        lines.append(f"  Impressions: {arm['impressions']:,}  |  Conversions: {arm['conversions']:,}")
        lines.append(f"  Expected CVR: {arm['expected_value']:.4%}")
        lines.append(f"  95% CI: [{arm['ci_95_lower']:.4%}, {arm['ci_95_upper']:.4%}]")
        lines.append(f"  P(best): {arm['prob_best']:.1%}")

        change = arm["allocation_change"]
        direction = "+" if change >= 0 else ""
        lines.append(f"  Allocation: {arm['old_allocation']:.1%} -> {arm['new_allocation']:.1%} ({direction}{change:.1%})")

        if total_budget:
            old_budget = total_budget * arm["old_allocation"]
            new_budget = total_budget * arm["new_allocation"]
            lines.append(f"  Budget: ${old_budget:,.0f} -> ${new_budget:,.0f}")
        lines.append("")

    lines.append(f"Recommendation: {result['recommendation']}")
    lines.append(f"Confidence in leader: {result['confidence_in_leader']:.1%}")

    if "declare_winner" in result["recommendation"]:
        winner_id = result["recommendation"].split(":")[1]
        lines.append(f"\n** WINNER IDENTIFIED: {winner_id} with {result['confidence_in_leader']:.1%} confidence **")
        lines.append("Recommend: Scale winner to 85% allocation, retire losers.")
    elif "leaning" in result["recommendation"]:
        leader_id = result["recommendation"].split(":")[1]
        lines.append(f"\nLeaning toward {leader_id} but need more data. Continue sampling.")

    lines.append("=" * 60)
    return "\n".join(lines)


def load_allocation(filepath):
    """Load allocation state from JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


def save_allocation(filepath, arms_result, exploration_rate, total_budget):
    """Save updated allocation state."""
    data = {
        "last_updated": datetime.now().isoformat(),
        "arms": [],
        "exploration_rate": exploration_rate,
        "total_budget_allocated": total_budget,
        "rebalance_frequency_hours": 6
    }
    for arm in arms_result:
        data["arms"].append({
            "id": arm["id"],
            "alpha": arm["alpha"],
            "beta": arm["beta"],
            "impressions": arm["impressions"],
            "conversions": arm["conversions"],
            "allocated_pct": arm["new_allocation"],
            "estimated_value": arm["expected_value"]
        })

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def main():
    simulate = "--simulate" in sys.argv
    filepath = ALLOCATION_FILE

    for i, arg in enumerate(sys.argv):
        if arg == "--file" and i + 1 < len(sys.argv):
            filepath = sys.argv[i + 1]

    if simulate:
        # Demo data matching EXP-008 from active experiments
        arms = [
            {"id": "V-045", "alpha": 157, "beta": 6045, "impressions": 6200, "conversions": 156, "allocated_pct": 0.35},
            {"id": "V-046", "alpha": 199, "beta": 6003, "impressions": 6200, "conversions": 198, "allocated_pct": 0.65}
        ]
        exploration_rate = 0.15
        total_budget = 25000
    else:
        data = load_allocation(filepath)
        arms = data["arms"]
        exploration_rate = data.get("exploration_rate", 0.15)
        total_budget = data.get("total_budget_allocated", 25000)

    result = thompson_allocate(arms, exploration_rate)
    output = format_output(result, total_budget)
    print(output)

    # Save updated allocation
    if not simulate:
        save_allocation(filepath, result["arms"], exploration_rate, total_budget)
        print(f"\nAllocation saved to {filepath}")
    else:
        print("\n(Simulate mode — not saving)")

    # Also output JSON for programmatic consumption
    json_output = json.dumps(result, indent=2)
    if "--json" in sys.argv:
        print("\n--- JSON OUTPUT ---")
        print(json_output)


if __name__ == "__main__":
    main()
