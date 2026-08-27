# Model canary rollback

## When to roll back

Roll back the canary model version when any of the following are true during the canary window:

- Error rate on canary exceeds stable by more than 1 percentage point for 10 minutes
- p99 end-to-end latency regresses by more than 20% vs stable
- Offline eval score drops on the golden set
- Elevated refusal rate or safety-filter triggers without a product reason
- GPU OOM / restart loop on the canary Deployment

## Rollback steps

1. Set gateway traffic to stable only:
   - Send `X-Model-Version: stable` from clients, **or**
   - Set `CANARY_PERCENT=0` and restart the gateway
2. Confirm Grafana: canary RPS falls to zero; stable absorbs traffic
3. Keep the canary Deployment running for debug **or** scale it to 0 if it is harming the node
4. File an incident note: model version, prompt version, eval diff, dashboards
5. Do not delete canary artifacts until root cause is written down

## Promote canary → stable

Only after the canary window passes eval + SLOs:

1. Point `INFERENCE_URL` at the canary upstream (or retag the model artifact as `stable`)
2. Set `CANARY_PERCENT=0` (or remove the canary upstream)
3. Bump the recorded model version in your registry / CHANGELOG
