# Alert noise cheatsheet

**Use this when:** pages are constant and someone wants to "just auto-ack" or auto-restart everything.  
**Rule of thumb:** automate toil *after* you make signals trustworthy — not instead.

---

## Noise patterns juniors hit

| Pattern | Fix before automating |
|---|---|
| Same outage → 40 alerts | Group / inhibit / route by service |
| Flappy threshold | Longer window, hysteresis, burn-rate alerts |
| No owner | Every alert needs a team page / Slack |
| Alert on causes not symptoms | Prefer user-pain (SLO) over raw CPU when you can |
| Staging pages at 2am | Separate routes; silence non-prod overnight |

---

## When *not* to auto-remediate

- You don't know if the action helps (no runbook)  
- The signal is flappy (you'll restart forever)  
- The failure is safety/security related  
- Blast radius is unclear  
- Verify step isn't defined  

**Detect + suggest + page** is still a win. Full auto is optional.

---

## Tiny noise-reduction checklist

- [ ] Alert has a runbook link  
- [ ] Alert has an owner  
- [ ] Duplicate paths inhibited  
- [ ] You've watched it fire correctly in a game day  
- [ ] Suggest-mode healer has seen it without acting  

---

## Lab pointer

Inject both `crashloop` (actionable) and `high_latency` (suggest-only) fixtures in the Phase 07 lab — notice how policy differs.
