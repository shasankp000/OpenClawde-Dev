#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${OPENCLAW_SUPERVISOR_HOME:-}" ]]; then
  echo "❌ OPENCLAW_SUPERVISOR_HOME is not set."
  echo "Run install.sh to install the dev supervisor."
  exit 1
fi

cd "$OPENCLAW_SUPERVISOR_HOME"

CMD="${1:-}"
shift || true

case "$CMD" in
  run)
    python supervisor.py "$@"
    ;;
  status)
    python supervisor.py status
    ;;
  approve)
    python supervisor.py approve
    ;;
  reject)
    python supervisor.py reject
    ;;
  *)
    echo "Usage:"
    echo "  /dev run <task>"
    echo "  /dev status"
    echo "  /dev approve"
    echo "  /dev reject"
    exit 1
    ;;
esac
