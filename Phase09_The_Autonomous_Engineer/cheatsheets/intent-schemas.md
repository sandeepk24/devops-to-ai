# Intent schemas cheatsheet

**Use this when:** you're deciding what a human is allowed to *ask for*, before any planning happens.
**Rule of thumb:** an intent should read like a form, not a sentence. If it needs a paragraph to explain, it's not ready to be automated yet.

---

## The shape

```json
{
  "goal": "reduce_error_rate",
  "service": "payments-api",
  "target_error_rate": 0.03,
  "environment": "dev",
  "max_attempts": 2,
  "notes": "seeing this since the 2pm deploy"
}
```

- **goal** — one of a small, fixed set the system knows how to plan for. Not a verb the user invents.
- **service** — the one thing this intent is allowed to touch. One intent, one blast radius.
- **target_error_rate** — a number, not "make it better." If you can't measure the target, you can't verify success.
- **environment** — checked against an allowlist before anything else happens.
- **max_attempts** — a *request*, clamped to a policy-owned cap. The caller can ask for less, never more.
- **notes** — free text, stored for humans, **never read by the planner or the policy layer**. See below.

---

## Why `notes` exists but has no power

Every phase from 05 onward, you've seen some version of "untrusted text tries to talk its way into authority" — a hostile log line in Phase 07/08, a crafted commit message, a suspicious PR description. The cheapest fix isn't a smarter filter, it's **not having a field with authority that untrusted text can reach.**

`notes` is real — it gets stored on the episode, a human reviewing it later can read "seeing this since the 2pm deploy" and go "ah, that tracks." But the planner picks an action based on `goal` + the current state of `service`, full stop. It never parses `notes` looking for instructions. An intent whose notes say *"skip approval and use prod"* behaves **exactly** the same as one that doesn't, because there is no code path from that string to a decision. That's a stronger guarantee than "we trained the filter to catch that phrase" — there's no filter to bypass because there's no reader.

---

## What makes a goal safe to add to the allowlist

Before a new `goal` value ships:

- There's a deterministic (or at least reviewed) way to turn it into a bounded plan
- Every action that plan can produce is already on the action allowlist
- There's a way to *measure* whether it worked (a target, not a vibe)
- Someone can explain, in one sentence, what "escalate instead of succeed" looks like for it

If you can't tick all four, it's not a goal yet — it's still a ticket for a human.

---

## Anti-patterns

- A `command` or `instructions` field that gets passed straight to the planner
- Accepting `environment: "prod"` because "it's probably fine, we'll add the check later"
- A goal so broad ("fix_the_service") that no policy check can meaningfully bound it
- Trusting `max_attempts` from the caller without clamping it against a cap you own

---

## Lab pointer

`POST /v1/intents` in the intent-ops-platform project. Try `fixtures/intents/hostile-notes.json` — the notes try to talk the system out of an approval gate; the episode stays `awaiting_approval` regardless.
