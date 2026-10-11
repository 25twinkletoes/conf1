#!/usr/bin/env bash
set +e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 -m src.main --vfs "$ROOT/vfs/sample" --script "$ROOT/examples/startup_error.txt"
exit $?
