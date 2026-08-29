# Path B stretch — optional cloud infra.
# Juniors: finish Path A (kind/k3d) before spending time here.

terraform {
  required_version = ">= 1.5.0"

  # TODO: configure a remote backend (S3 / GCS / Terraform Cloud)
  # backend "s3" {
  #   bucket         = "YOUR_TF_STATE_BUCKET"
  #   key            = "phase01/microservice-pipeline.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "tf-locks"
  #   encrypt        = true
  # }

  required_providers {
    # Pick one cloud and delete the other block when you commit for real.
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  type        = string
  description = "GCP project id for GKE Autopilot (Path B)"
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "cluster_name" {
  type    = string
  default = "phase01-api"
}

# TODO: add google_container_cluster (Autopilot) or an EKS module
# Keep cost in mind — destroy lab clusters when you're done.

output "next_steps" {
  value = "Replace this stub with a real cluster resource, then wire kubeconfig into GitHub Secrets for deploy."
}
