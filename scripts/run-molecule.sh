#!/usr/bin/env bash
# Run Molecule tests for ansible-infrastructure-automation-lab.
# Ephemeral Docker containers only — digest-pinned images, no real SSH hosts.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

export ANSIBLE_ROLES_PATH="${ROOT}/roles${ANSIBLE_ROLES_PATH:+:${ANSIBLE_ROLES_PATH}}"

SCENARIOS=("baseline" "orchestration")
if [[ "${#}" -gt 0 ]]; then
  SCENARIOS=("$@")
fi

if ! command -v molecule >/dev/null 2>&1; then
  echo "ERROR: molecule not found. Install requirements-dev.txt first." >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker not found. Molecule scenarios need Docker for ephemeral containers." >&2
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: docker daemon not reachable." >&2
  exit 1
fi

echo "==> Installing Galaxy collections from requirements.yml"
ansible-galaxy collection install -r "${ROOT}/requirements.yml" -p "${ROOT}/collections"

echo "==> Molecule scenarios (ephemeral only): ${SCENARIOS[*]}"
echo "    Safety: aial_environment=molecule aial_safe_to_apply=true"
echo "    Firewall: render-only (aial_firewall_apply=false)"
echo "    Images: digest-pinned (never :latest)"

for scenario in "${SCENARIOS[@]}"; do
  echo
  echo "==> molecule test -s ${scenario}"
  molecule test -s "${scenario}"
done

echo
echo "==> All requested Molecule scenarios completed."
