# Episode memory cheatsheet

**Use this when:** you're deciding what a decision needs to remember about itself.
**Rule of thumb:** a stranger, six months from now, with no context, should be able to read one record and know exactly what happened and why.

---

## Audit log vs episode record

You've built a flat audit log twice already — Phase 07 and Phase 08 both append one event per thing-that-happened. That's still here in Phase 09 (`GET /v1/audit`), and it's still useful for "show me everything that happened in the last five minutes." But it's the wrong shape for "explain this one decision." For that you want everything about **one** decision collected in **one** place: the episode.

```
Audit log     →  a security camera. Great for "what happened around 3pm."
Episode record →  an incident report. Great for "what happened to THIS ticket, start to finish."
```

---

## What belongs in an episode

- **The ask** — the intent exactly as submitted, including fields that got rejected
- **Every policy decision** — not just "rejected," but *which* check failed and why, in words a human wrote (or a human would write, if it's templated)
- **Every attempt** — the action taken, the rationale behind choosing it, the measured result, and whether it met the target
- **The terminal outcome** — succeeded, denied, rejected_by_policy, escalated_needs_human — and nothing vaguer than that
- **Who approved or denied it, and when** — even in a lab, even if it's always "local-dev"

What does **not** belong: guesses about *why* the human approved it, speculation about what "probably" happened, anything you'd have to infer rather than read directly off the record.

---

## Why this compounds

Look at how much a system needs to remember to act safely, phase over phase:

```
Phase 00-02   a log line, a metric, a trace span     — what happened
Phase 07      an audit event with a policy decision  — what happened + was it allowed
Phase 08      an approval record tied to an action    — what happened + who signed off
Phase 09      a full episode: intent → policy → plan → attempts → outcome
```

Each phase didn't throw away the previous phase's memory — it added a layer. An intent platform with no episode memory is scarier than a chatbot with no memory, because it's the one actually changing things. The more authority a system has, the less optional its memory gets.

---

## A good test for "is this episode complete"

Hand the raw JSON to someone who wasn't in the room, with zero other context. If they come back with a question your record can't answer — "wait, why did it try that first?", "who said yes?", "why did it stop instead of trying once more?" — the record isn't done yet.

---

## Anti-patterns

- Logging *that* a step ran without logging *why* it was chosen
- Storing "approved" without who approved it or when
- Losing the original intent once a plan is generated (you need both, forever)
- A record that's technically complete but needs three other systems cross-referenced to make sense

---

## Lab pointer

`GET /v1/episodes/{id}` in the intent-ops-platform project. Run one intent to `succeeded` and one to `escalated_needs_human`, then read both full episodes back to back — same shape, very different story.
