#!/usr/bin/env bash
set -euo pipefail
TP4_SCRIPT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
source "$TP4_SCRIPT_ROOT/scripts/use-lab-env.sh"
exec python3 "$TP4_SCRIPT_ROOT/scripts/lab.py" test-leadingkeys "$@"
