# creative-factory

AI-powered growth marketing creative engine for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

![Python](https://img.shields.io/badge/Python-%3E%3D3.9-blue)
![Claude Code](https://img.shields.io/badge/Claude%20Code-Required-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## What it is

A self-improving creative engine that generates multi-variant ad creatives across paid search, paid social, ASO, and lifecycle channels -- then tests them, monitors performance, allocates budget via Thompson Sampling, and feeds every result back into a persistent knowledge layer. The system gets measurably better with every cycle.

Built as a Claude Code skill. Works for **any company** -- bring your own positioning document, brand config, and segments. Ships with a complete Replit example in `examples/replit/` showing 3 cycles of compound learning (26 insights, 5 meta-patterns, hypothesis generation from insight combinations).

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

## Quick start

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

Then open Claude Code and run the init wizard:

```bash
claude
# Type: /creative-factory init
```

The init wizard walks you through:
1. Brand name, product, category, tagline, colors
2. Voice attributes (tone, vocabulary, words to avoid)
3. Active channels (paid_search, paid_social, aso, lifecycle)
4. Geos with budget allocation and CPA targets
5. Customer segments with hooks, pain points, value props
6. Conversion funnel events
7. Budget and payback targets
8. Positioning document import
9. Design system generation

### Using the Replit example

To see what a fully populated system looks like:

```bash
# Copy example data over the blank templates
cp examples/replit/config.json ~/.claude/data/creative-factory/
cp examples/replit/positioning-active.json ~/.claude/data/creative-factory/positioning/active.json
cp examples/replit/replit-positioning.md ~/.claude/data/creative-factory/positioning/positioning.md
cp examples/replit/DESIGN-SYSTEM.md ~/.claude/data/creative-factory/creatives/
cp examples/replit/insights.json ~/.claude/data/creative-factory/knowledge/
cp examples/replit/creative-dna.json ~/.claude/data/creative-factory/knowledge/
cp examples/replit/fatigue-signals.json ~/.claude/data/creative-factory/knowledge/
cp examples/replit/experiments-active.json ~/.claude/data/creative-factory/experiments/active.json
cp examples/replit/experiments-completed.json ~/.claude/data/creative-factory/experiments/completed.json
cp examples/replit/hypotheses.json ~/.claude/data/creative-factory/experiments/
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

## Components

### Knowledge Layer

Append-only intelligence store. Every experiment result, every performance signal, every discovered pattern gets recorded and indexed by channel, geo, and segment. Nothing is overwritten -- history is the asset.

- **insights.json** -- insights with confidence levels, sample sizes, and applicability tags
- **creative-dna.json** -- winning and losing creative patterns extracted from completed experiments
- **fatigue-signals.json** -- patterns that predict creative decay before CTR drops

### Experiment Framework

Structured A/B testing with statistical rigor. Experiments track hypothesis, control/variant, sample size requirements, and confidence thresholds. When an experiment closes, the system extracts insights, updates creative DNA, generates new hypotheses from pattern combinations, and updates positioning signals.

### Performance Monitoring

Four alert types with configurable thresholds:

| Alert | Trigger | Window |
|-------|---------|--------|
| Creative Fatigue | CTR decline beyond threshold | Configurable (default 14 days) |
| CAC Shift | CPA increase beyond threshold | Configurable (default 7 days) |
| Payback Drift | Days-to-payback increase beyond threshold | Configurable (default 14 days) |
| Conversion Quality | Signup-to-paid decline >15% | 7 days |

Each alert includes severity, affected channel/geo, and recommended actions.

### Thompson Sampling

Multi-armed bandit budget allocation via `scripts/thompson.py`. Balances exploitation (shift budget to winners) with exploration (keep sampling underexplored arms). Shows Beta distribution parameters, expected values, allocation shifts, and confidence in winner identification. Arms with >95% confidence of losing get flagged for retirement.

### Creative Generation

Channel-aware generation pipeline that reads the full knowledge layer before producing anything. Every variant cites which insights informed it. Geo modifiers are mandatory -- one-size-fits-all is not an option.

### Design System

Brand-compliant mockup generation via Playwright. Color tokens, layout patterns, and platform-specific canvas sizes are configured during init. See `creatives/DESIGN-SYSTEM.md`.

## Data model

```
creative-factory/
  config.json                    # Brand config: channels, geos, segments, budgets, thresholds
  creatives/
    DESIGN-SYSTEM.md             # Visual design tokens, layout patterns, platform specs
    brand-assets/                # Brand screenshots, logos, mockup references
  examples/
    replit/                      # Complete Replit example (3 cycles, 26 insights)
      config.json
      positioning-active.json
      replit-positioning.md
      DESIGN-SYSTEM.md
      insights.json
      creative-dna.json
      fatigue-signals.json
      experiments-active.json
      experiments-completed.json
      hypotheses.json
  experiments/
    active.json                  # Running experiments
    completed.json               # Closed experiments with final statistics
    hypotheses.json              # Queued experiments from insight combinations
  knowledge/
    insights.json                # Insights with confidence, sample size, tags
    creative-dna.json            # Winning and losing creative patterns
    fatigue-signals.json         # Patterns that predict creative decay
  performance/
    metrics.json                 # Raw performance data by channel/geo/segment
    alerts.json                  # Active alerts with severity and actions
    allocation.json              # Thompson Sampling arm states and allocations
  positioning/
    active.json                  # Current messaging hierarchy by segment
    positioning.md               # Product positioning document (your company)
  scripts/
    thompson.py                  # Thompson Sampling implementation
    simulate_performance.py      # Mock data generator for testing
  skill/
    SKILL.md                     # Claude Code skill definition
```

## License

MIT. See [LICENSE](LICENSE).

---

Built by [Abhishek Krishnan](https://github.com/kriabhishek).
