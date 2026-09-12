# Bounded autonomy cheatsheet

**Use this when:** you're letting a system try more than once to fix something on its own.
**Rule of thumb:** every retry loop needs a number on it before it needs a plan.

---

## The loop

```
approve plan
  → execute step
  → verify against target
  → met?         → succeeded, stop
  → not met?     → attempts left?
                     → yes: replan from current state, try again
                     → no:  escalated_needs_human, stop
```

Two stopping conditions, both explicit. There is no third path where it just... keeps going. If your loop's exit condition is "eventually it'll work," you don't have bounded autonomy, you have a `while True`.

---

## Why one approval covers the whole loop, not each attempt

In Phase 08, one approval covered one action. Here, one approval covers "let the system try up to N times to reach this target using allowlisted actions." That's a bigger grant of trust, so it needs a bigger guardrail underneath it: the attempt cap. You're not approving "do whatever it takes" — you're approving "try, within this budget, using only moves I've already reviewed the shape of."

If an attempt would require an action or a magnitude outside what's already allowlisted (say, a replica count past your blast-radius cap), that's not "try harder" — that's an immediate rejection or escalation. Bounded autonomy bounds the *moves*, not just the *count*.

---

## Escalation is a good outcome, not a failure state

It's tempting to treat "the system couldn't do it" as a bug. It's not — it's the honest output of a system that knows its own limits. A junior engineer who tries the two things they know, then pages someone with "here's what I tried and what I measured," is doing their job correctly. `escalated_needs_human` is that page. The valuable part isn't that it succeeded or failed — it's that it stopped *cleanly*, with a full record of what was attempted, instead of thrashing.

---

## Sizing the cap

There's no universal right number for `max_attempts`. Ask instead:

- What's the cost of one wrong attempt? (A scale-up is cheap to try twice. A schema migration is not.)
- Does each retry use *new* information (updated state), or is it just running the same thing again hoping for a different result? Only the former deserves a retry budget.
- Would a human, watching live, let it try a third time? If you're not sure, the cap is too high.

Two attempts is a reasonable default for a lab. In production, this number should live in policy, be reviewed, and change slowly.

---

## Kill switches pause, they don't discard

A kill switch that silently skips a decision (Phase 07's healer) is fine when the decision was going to happen automatically anyway — skipping it just means "don't act, try again next cycle." A kill switch on an *approved plan* is different: if it silently discarded the episode, you'd lose the fact that a human already said yes. Pausing means the episode sits in `awaiting_approval` untouched — flip the switch off later, and the same approval can go through. Nothing about the human's decision gets thrown away because the switch was on.

---

## Anti-patterns

- No cap at all ("it'll converge eventually")
- A cap so high it's effectively no cap (`max_attempts: 50`)
- Retrying the exact same action with the exact same arguments, hoping for luck
- Treating escalation as something to suppress or auto-retry past
- Letting an approved episode's kill-switch pause quietly turn into a silent drop

---

## Lab pointer

`fixtures/intents/overload-recoverable.json` succeeds on attempt 2. `fixtures/intents/overload-unreachable.json` uses the same service and cause but escalates — same code path, different target, different outcome. Read both episodes side by side.
