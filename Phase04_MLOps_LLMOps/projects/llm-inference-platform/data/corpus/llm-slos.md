# LLM platform SLOs (example)

These are example objectives for a team-facing inference API — tune them to your product.

| SLI | SLO (30-day) |
|---|---|
| Availability (non-5xx) | 99.5% |
| Latency p99 end-to-end | < 5s for interactive chat |
| Time to first token p95 | < 1.5s |
| Rate-limit correctness | 429 only when over quota |

## Error budget policy

If more than half the monthly error budget is burned in a week: freeze model/prompt promotions except severity-1 fixes. Spend engineering time on reliability (capacity, timeouts, fallbacks) before new features.
