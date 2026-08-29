# Terraform cheatsheet

**Use this when:** creating cloud (or local) infrastructure as code.  
**Golden rule:** always read `terraform plan` before `apply`.

---

## Mental model

```
.tf files  →  plan (diff)  →  apply (create/change/destroy)
                 ↑
              state file = Terraform's memory of what it owns
```

If someone changes a resource in the console, state drifts. Fix through code, or `import` carefully.

---

## Everyday workflow

```bash
terraform init                 # download providers / modules
terraform fmt                  # format
terraform validate
terraform plan -out=tfplan     # review!
terraform apply tfplan
terraform destroy              # tear down lab resources
```

```bash
terraform state list
terraform state show aws_s3_bucket.logs
terraform output
```

---

## File layout (keep it boring)

```
terraform/
├── main.tf          # resources
├── variables.tf
├── outputs.tf
├── providers.tf
├── backend.tf       # remote state
└── terraform.tfvars # values (don't commit secrets)
```

For bigger work, split into **modules** later. One folder is fine for the Phase 01 capstone.

---

## Tiny examples

**Provider + resource (AWS S3 sketch):**

```hcl
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "logs" {
  bucket = var.bucket_name
}

resource "aws_s3_bucket_versioning" "logs" {
  bucket = aws_s3_bucket.logs.id
  versioning_configuration {
    status = "Enabled"
  }
}
```

**Variables / outputs:**

```hcl
variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "bucket_name" {
  type = string
}

output "bucket_arn" {
  value = aws_s3_bucket.logs.arn
}
```

---

## State (don't skip this)

| Approach | When |
|---|---|
| Local state | Throwaway laptop experiments only |
| Remote state (S3 + lock / GCS / Terraform Cloud) | Anything shared or "real" |

**Never commit** `terraform.tfstate` or `.terraform/` to Git. Put them in `.gitignore`.

Remote backend sketch (AWS):

```hcl
terraform {
  backend "s3" {
    bucket         = "my-tf-state-bucket"
    key            = "phase01/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tf-locks"
    encrypt        = true
  }
}
```

---

## Modules (when copy-paste hurts)

```hcl
module "network" {
  source = "./modules/network"
  cidr   = "10.0.0.0/16"
}
```

Pin module versions when you pull from a registry or Git tag.

---

## Safety habits

```bash
# Who am I about to bill?
aws sts get-caller-identity    # or gcloud config get-value project

# Plan with an explicit var file
terraform plan -var-file=dev.tfvars

# Protect prod with separate state / workspaces / folders — not vibes
```

- Don't put secrets in `.tf` or `.tfvars` committed to Git — use env vars or a secret manager
- Prefer small PRs: one logical change per plan
- Run `tflint` in CI when you can

---

## Common footguns

| Symptom | Likely cause |
|---|---|
| State lock errors | Another apply running, or crashed apply left a lock |
| "Resource already exists" | Created in console; need import or rename |
| Huge blast radius plan | Wrong workspace / wrong backend key |
| Credentials errors | Env vars / profile not set for the provider |

---

## Phase 01 tip

You can finish the capstone on **kind/k3d** without Terraform at all (Path A). Use Terraform when you're ready for Path B (cloud cluster / remote state). Don't let cloud account setup block learning Docker and Kubernetes.

---

*Part of [devops-to-ai](../../README.md) — Phase 01: Core DevOps*
