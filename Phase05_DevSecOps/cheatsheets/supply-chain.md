# Supply chain cheatsheet (SBOM & signing)

**Use this when:** someone asks "what's in this image?" or "how do we know it came from our pipeline?"  
**Rule of thumb:** scanning finds known bad; SBOM lists ingredients; signing proves provenance. You want all three over time — start with scan + SBOM.

---

## SBOM in one minute

Software Bill of Materials = ingredients list (packages, versions, licenses sometimes).

Generate with Trivy:

```bash
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  -v "$PWD/out:/out" aquasec/trivy:0.58.1 image \
  --format spdx-json --output /out/sbom.spdx.json IMAGE:TAG
```

Or filesystem:

```bash
docker run --rm -v "$PWD:/src" -v "$PWD/out:/out" aquasec/trivy:0.58.1 fs \
  --format spdx-json --output /out/sbom-fs.spdx.json /src
```

Attach the file to the release / CI artifact. When the next Log4Shell-class event hits, you *search* the SBOM instead of guessing.

---

## Signing (Cosign) — mental model

```
CI builds image → Cosign signs digest → registry stores sig
Cluster / CD verifies signature before deploy (optional but powerful)
```

Local key pair (learning only — prefer keyless/OIDC in real orgs):

```bash
# Needs cosign installed: https://docs.sigstore.dev/cosign/system_config/installation/
cosign generate-key-pair   # creates cosign.key / cosign.pub — never commit the private key
cosign sign --key cosign.key IMAGE:TAG
cosign verify --key cosign.pub IMAGE:TAG
```

**Path A done criteria:** you can explain the flow and point to where you'd put verify in CD.  
**Stretch:** actually sign a local image and verify it.

---

## SLSA (interview signal)

[SLSA](https://slsa.dev/) describes levels of supply-chain assurance (provenance, hermetic builds, etc.). You don't need Level 4 on a learning lab — know that "we signed the image" is one step on a longer ladder.

---

## Don't confuse these

| Artifact | Answers |
|---|---|
| Scan report | Known CVEs *today* |
| SBOM | What packages were present *when we built* |
| Signature | This digest was produced/approved by *our* process |

A signed image can still have CVEs. A clean scan can still be malware you built yourself. Defense in depth.

---

## Useful links

- [Sigstore docs](https://docs.sigstore.dev/)
- [SPDX](https://spdx.dev/) / [CycloneDX](https://cyclonedx.org/)
- Phase 05 lab: `scripts/generate_sbom.sh`
