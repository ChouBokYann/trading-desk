# Sizing Framework

Position sizing matrix mapping information quality × Jaya's conviction to a concrete size range. Use this alongside `neutral-risk-review.md` when the orchestrator asks Nina to provide an explicit size recommendation.

---

## Information Quality × Conviction Matrix

| Information Quality | Conviction 1-4 | Conviction 5-6 | Conviction 7-8 | Conviction 9-10 |
|---|---|---|---|---|
| **High** | 1-2% | 3-4% | 5-6% | 6-8% |
| **Moderate** | 0.5-1% | 2-3% | 3-5% | 4-6% |
| **Low** | 0% (avoid) | 1-2% | 2-3% | 2-4% |

- Use the lower end of each range when any of the following apply: event risk within trade horizon, elevated VIX (>25), undefined-risk structure, or existing portfolio concentration in the sector.
- Use the upper end when: vol is low and contracting, structure is defined-risk, and no correlated positions exist.
- These are Nina's neutral recommendations -- Axel will argue the upper bound, Cass will argue the lower bound. Hugo weighs all three.

---

## Undefined-Risk Cap

Regardless of conviction or information quality, undefined-risk positions (naked short options, leveraged ETFs held > 1 week) are capped at 2% under Nina's framework. This is non-negotiable -- it is not a starting point for negotiation with Axel.

---

## Missing Data Defaults

| Missing Data | Default Action |
|---|---|
| No options chain | Treat as Moderate information quality; cap at Moderate row |
| Stale fundamentals (>1 quarter) | Treat as Low information quality |
| No IV data | Cannot assess vol regime; flag and apply -1% haircut to recommended range |
| Conviction not set by Jaya | Do not size. Request verdict before proceeding. |
