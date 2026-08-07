#!/usr/bin/env bash
# Safe check-mode runner for ansible-infrastructure-automation-lab.
#
# DEFAULT: --check --diff only.
# NEVER applies against inventories/synthetic (public planning inventory).
# Prefer Molecule inventory for apply validation; synthetic is check-only.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

export ANSIBLE_ROLES_PATH="${ROOT}/roles${ANSIBLE_ROLES_PATH:+:${ANSIBLE_ROLES_PATH}}"

MODE="check"
INVENTORY=""
PLAYBOOK="${ROOT}/playbooks/check.yml"
EXTRA_ARGS=()

usage() {
  cat <<'EOF'
Usage: scripts/check-lab.sh [--check|--apply] [--inventory PATH] [--playbook PATH] [--] [ansible-playbook args]

Defaults:
  --check --diff
  inventory: molecule/baseline/inventory/ (ephemeral Molecule inventory)

Safety:
  - Synthetic public inventory (inventories/synthetic) is CHECK-ONLY.
  - --apply is refused for inventories/synthetic.
  - --apply requires aial_safe_to_apply=true (Molecule inventories set this).
  - Does not reboot hosts or disable runner networking.
EOF
}

while [[ "${#}" -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --check)
      MODE="check"
      shift
      ;;
    --apply)
      MODE="apply"
      shift
      ;;
    --inventory)
      INVENTORY="${2:?--inventory requires a path}"
      shift 2
      ;;
    --playbook)
      PLAYBOOK="${2:?--playbook requires a path}"
      shift 2
      ;;
    --)
      shift
      EXTRA_ARGS+=("$@")
      break
      ;;
    *)
      EXTRA_ARGS+=("$1")
      shift
      ;;
  esac
done

if [[ -z "${INVENTORY}" ]]; then
  if [[ -d "${ROOT}/molecule/baseline/inventory" ]]; then
    INVENTORY="${ROOT}/molecule/baseline/inventory"
  else
    echo "ERROR: No default Molecule inventory found at molecule/baseline/inventory." >&2
    echo "Pass --inventory explicitly. Refusing to default to synthetic public inventory." >&2
    exit 1
  fi
fi

# Normalize for safety checks
INVENTORY_ABS="$(cd "$(dirname "${INVENTORY}")" && pwd)/$(basename "${INVENTORY}")"
case "${INVENTORY_ABS}" in
  *"inventories/synthetic"*|*"inventories\\synthetic"*)
    if [[ "${MODE}" == "apply" ]]; then
      echo "ERROR: Refusing --apply against synthetic public inventory." >&2
      echo "Synthetic inventory keeps aial_safe_to_apply=false and has no real ansible_host." >&2
      echo "Use Molecule inventory (ephemeral containers) or an untracked private inventory." >&2
      exit 2
    fi
    echo "==> Synthetic inventory: check mode only (safe)."
    ;;
esac

if [[ ! -e "${INVENTORY}" ]]; then
  echo "ERROR: inventory path does not exist: ${INVENTORY}" >&2
  exit 1
fi

CMD=(
  ansible-playbook
  --inventory "${INVENTORY}"
  "${PLAYBOOK}"
)

if [[ "${MODE}" == "check" ]]; then
  CMD+=(--check --diff)
  echo "==> Running CHECK mode (--check --diff)"
else
  echo "==> Running APPLY mode (requires aial_safe_to_apply=true in inventory)"
  echo "    Target inventory: ${INVENTORY}"
  echo "    WARNING: Only use against ephemeral Molecule containers or authorized private inventory."
fi

if [[ "${#EXTRA_ARGS[@]}" -gt 0 ]]; then
  CMD+=("${EXTRA_ARGS[@]}")
fi

echo "    inventory=${INVENTORY}"
echo "    playbook=${PLAYBOOK}"
printf '    command='
printf '%q ' "${CMD[@]}"
echo

exec "${CMD[@]}"
