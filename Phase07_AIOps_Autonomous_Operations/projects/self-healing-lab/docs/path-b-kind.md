# Path B — kind stretch (optional)

Path A taught the loop without Kubernetes. Path B is the same ideas against a real cluster — still keep suggest-before-auto discipline.

## Sketch

1. `kind create cluster --name phase07`
2. Deploy a deliberately flappy app (bad probe, crash on start, etc.)
3. Watch: `kubectl get pods -w`
4. **Suggest:** write the remediation you'd run (`kubectl rollout restart deploy/flappy`)
5. **Auto (careful):** a CronJob/script that only restarts if:
   - label `healing.devops-to-ai/auto=true`
   - namespace allowlist
   - cooldown ConfigMap
   - kill switch ConfigMap `data.enabled=false` stops acts

## Do not

- Grant the healer `cluster-admin`
- Auto-delete namespaces
- Skip verify (`kubectl wait` / curl via port-forward)

## Done for Path B

- [ ] You restarted something *intentionally* and verified recovery  
- [ ] You documented where the kill switch would live  
- [ ] You still prefer suggest mode for any new signal  

When this is comfortable, Phase 08 adds agents that *choose* tools — they'll need these same fences.
