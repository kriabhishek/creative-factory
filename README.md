# creative-factory

AI-powered growth marketing creative engine for Claude Code.

![Python](https://img.shields.io/badge/Python-%3E%3D3.9-blue)
![Claude Code](https://img.shields.io/badge/Claude%20Code-Required-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## What it is

A self-improving creative engine that generates multi-variant ad creatives across paid search, paid social, ASO, and lifecycle channels -- then tests them, monitors performance, allocates budget via Thompson Sampling, and feeds every result back into a persistent knowledge layer. The system gets measurably better with every cycle.

Built as a [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill. After 4 simulated cycles: 26 insights, 5 meta-patterns, and hypothesis generation from insight combinations -- all without manual analysis.

## The system

```
                          CREATIVE FACTORY
                     Compound Learning Loops

  LOOP 1: Creative Quality
  ========================
  Generate ---> Test ---> Learn what works ---> Generate better
       ^                                            |
       |   [insights.json + creative-dna.json       |
       +----  grow every cycle]  <------------------+

  LOOP 2: Experiment Velocity
  ===========================
  Learn ---> Hypothesize ---> Test faster ---> Learn more
       ^                                          |
       |   [hypotheses.json populated from        |
       +----  pattern combinations, not guesses] -+

  LOOP 3: Positioning Evolution
  =============================
  Test ---> Discover segment/geo truths ---> Update positioning
       ^                                          |
       |   [active.json performance_signals       |
       +----  update the source-of-truth] --------+

  After N cycles:
    - Proven patterns by channel x geo x segment
    - Fatigue signatures that predict creative decay
    - Auto-generated hypotheses from insight combinations
    - Positioning that reflects reality, not assumptions
    - Budget allocation mathematically optimized for ROI
```

## Components

### Knowledge Layer

Append-only intelligence store. Every experiment result, every performance signal, every discovered pattern gets recorded and indexed by channel, geo, and segment. Nothing is overwritten -- history is the asset.

- **insights.json** -- 26+ insights with confidence levels, sample sizes, and applicability tags
- **creative-dna.json** -- winning and losing patterns extracted from completed experiments
- **fatigue-signals.json** -- patterns that predict creative decay before CTR drops

### Experiment Framework

Structured A/B testing with statistical rigor. Experiments track hypothesis, control/variant, sample size requirements, and confidence thresholds. When an experiment closes, the system extracts insights, updates creative DNA, generates new hypotheses from pattern combinations, and updates positioning signals.

- **active.json** -- running experiments with live metrics
- **completed.json** -- closed experiments with final statistics and extracted insights
- **hypotheses.json** -- queued experiments generated from insight combinations

### Performance Monitoring

Four alert types with configurable thresholds:

| Alert | Trigger | Window |
|-------|---------|--------|
| Creative Fatigue | CTR decline >20% | 14 days |
| CAC Shift | CPA increase >30% | 7 days |
| Payback Drift | Days-to-payback increase >25% | 14 days |
| Conversion Quality | Signup-to-paid decline >15% | 7 days |

Each alert includes severity, affected channel/geo, and recommended actions.

### Thompson Sampling

Multi-armed bandit budget allocation via `scripts/thompson.py`. Balances exploitation (shift budget to winners) with exploration (keep sampling underexplored arms). Shows Beta distribution parameters, expected values, allocation shifts, and confidence in winner identification. Arms with >95% confidence of losing get flagged for retirement.

### Creative Generation

Channel-aware generation pipeline that reads the full knowledge layer before producing anything. Every variant cites which insights informed it. Geo modifiers are mandatory -- one-size-fits-all is not an option.

**Channels:** Paid Search (30-char headlines, 90-char descriptions), Paid Social (platform-routed to Meta/LinkedIn/X/YouTube), ASO (keyword-optimized titles), Lifecycle (5-stage activation sequences).

**Geo rules:** US (social proof, no price), India ("Free" in first 3 words), EU (security qualifiers), LATAM (community framing).

### Design System

Brand-compliant mockup generation via Playwright. Six color tokens, four layout patterns (Orange Feature Panel, Dark Product Showcase, Light Testimonial Grid, Hero Banner), platform-specific canvas sizes. See `creatives/DESIGN-SYSTEM.md` for the full spec.

## Getting started

```bash
git clone https://github.com/kriabhishek/creative-factory.git
cd creative-factory

# Copy the skill into Claude Code
mkdir -p ~/.claude/skills/creative-factory
cp skill/SKILL.md ~/.claude/skills/creative-factory/

# Copy data files to the expected location
mkdir -p ~/.claude/data/creative-factory
cp -r config.json positioning knowledge experiments performance scripts creatives \
  ~/.claude/data/creative-factory/
```

Then open Claude Code:

```bash
claude
# Type: /creative-factory status
```

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (Anthropic's CLI)
- Python >= 3.9 (for Thompson Sampling scripts)

## Invocations

| Command | What it does |
|---------|-------------|
| `/creative-factory` | Full pipeline: load positioning, read knowledge, generate creatives, set up experiments |
| `/creative-factory init` | Initialize brand config, import positioning document, set channels/geos/segments/budgets |
| `/creative-factory generate [channel]` | Generate creative variants for a channel (paid_search, paid_social, aso, lifecycle) or all |
| `/creative-factory ingest` | Load performance data from paste, simulation, or file |
| `/creative-factory monitor` | Run performance monitoring, check alert thresholds, flag issues |
| `/creative-factory allocate` | Run Thompson Sampling budget allocation across active arms |
| `/creative-factory learn` | Close mature experiments, extract insights, generate hypotheses, update positioning |
| `/creative-factory report` | Generate daily performance digest with compound effect tracking |
| `/creative-factory status` | Dashboard: knowledge layer size, active experiments, alerts, budget, compound growth |

## How it works

The engine runs in cycles. Each cycle:

1. **Generate** -- reads the full knowledge layer (insights, creative DNA, fatigue signals) and produces channel/geo/segment-specific creative variants. Every variant cites which insights informed it.
2. **Test** -- variants run as structured A/B experiments with pre-registered hypotheses, sample size requirements, and confidence thresholds.
3. **Monitor** -- performance data is ingested and checked against four alert types. Fatigue, CAC shifts, payback drift, and conversion quality issues are flagged with recommended actions.
4. **Allocate** -- Thompson Sampling redistributes budget across active arms, balancing exploitation and exploration.
5. **Learn** -- mature experiments close. The system extracts insights, updates winning/losing patterns, generates new hypotheses from pattern combinations, and updates the positioning document.

The key property: cycle N is strictly better than cycle N-1, because the knowledge layer only grows. Insights compound. Hypotheses are derived from proven patterns, not guesses. Positioning reflects observed performance, not assumptions.

## Data model

```
creative-factory/
  config.json                    # Brand config: channels, geos, segments, budgets, thresholds
  creative-factory-guide.pdf     # Walkthrough PDF
  creatives/
    DESIGN-SYSTEM.md             # Visual design tokens, layout patterns, platform specs
    *.png                        # Brand screenshots and mockup references
  experiments/
    active.json                  # Running experiments
    completed.json               # Closed experiments with final statistics
    hypotheses.json              # Queued experiments from insight combinations
  knowledge/
    insights.json                # 26+ insights with confidence, sample size, tags
    creative-dna.json            # Winning and losing creative patterns
    fatigue-signals.json         # Patterns that predict creative decay
  performance/
    metrics.json                 # Raw performance data by channel/geo/segment
    alerts.json                  # Active alerts with severity and actions
    allocation.json              # Thompson Sampling arm states and allocations
  positioning/
    active.json                  # Current messaging hierarchy by segment
    replit-positioning.md        # Product positioning document
  scripts/
    thompson.py                  # Thompson Sampling implementation
    simulate_performance.py      # Mock data generator for testing
  skill/
    SKILL.md                     # Claude Code skill definition (~330 lines)
```

## License

MIT. See [LICENSE](LICENSE).

---

Built by [Abhishek Krishnan](https://github.com/kriabhishek).
