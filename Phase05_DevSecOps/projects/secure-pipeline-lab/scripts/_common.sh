#!/usr/bin/env bash
# Shared helpers for Phase 05 Path A scripts.
# shellcheck shell=bash

require_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "ERROR: docker not found on PATH."
    echo "Install Docker Desktop (or Engine), then open a new terminal."
    echo "Check: docker --version"
    exit 1
  fi
  if ! docker info >/dev/null 2>&1; then
    echo "ERROR: cannot talk to the Docker daemon."
    echo "Start Docker Desktop and wait until it says it's running, then retry."
    echo "Check: docker info"
    exit 1
  fi
}
