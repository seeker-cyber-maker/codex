#!/usr/bin/env bash
# Compare two capture_usb_snapshot.sh labels without changing their evidence.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: diff_usb_snapshots.sh BEFORE_LABEL AFTER_LABEL OUTPUT_DIRECTORY

Writes a single unified text diff. Exit status 1 means differences were found;
it is expected for an inserted USB device. Exit status 0 means no differences.
EOF
}

if [[ $# -ne 3 ]]; then
  usage >&2
  exit 64
fi

before="$1"
after="$2"
output_dir="$3"

for label in "$before" "$after"; do
  for suffix in system-profiler.json ioreg-usb.txt ioreg-yubico.txt ykman.txt; do
    if [[ ! -f "$output_dir/$label-$suffix" ]]; then
      echo "Missing snapshot: $output_dir/$label-$suffix" >&2
      exit 66
    fi
  done
done

status=0

compare() {
  local suffix="$1"
  if ! diff -u \
    --label "$before-$suffix" "$output_dir/$before-$suffix" \
    --label "$after-$suffix" "$output_dir/$after-$suffix"; then
    status=1
  fi
}

compare system-profiler.json
compare ioreg-usb.txt
compare ioreg-yubico.txt
compare ykman.txt

exit "$status"
