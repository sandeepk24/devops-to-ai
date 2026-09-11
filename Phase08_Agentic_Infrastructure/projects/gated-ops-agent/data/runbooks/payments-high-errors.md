# payments-api — elevated error rate

## Symptoms
- Error rate >> baseline for 5+ minutes
- Timeouts talking to `billing-v2`

## Safe investigation
1. Check metrics (error rate, p99, RPS)
2. Tail recent ERROR logs
3. Confirm change window / recent deploy

## Remediation (requires approval)
If a bad deploy is confirmed: **rollback** `payments-api` to the previous version.

Do **not** delete namespaces or scale to zero as a first response.
