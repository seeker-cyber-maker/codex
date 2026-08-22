#!/usr/bin/env bash
# Capture a read-only macOS USB snapshot for before/after device-enumeration
# diagnosis. It never opens a YubiKey credential, changes device state, or
# overwrites an existing snapshot.

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: capture_usb_snapshot.sh LABEL OUTPUT_DIRECTORY

LABEL must contain only letters, digits, underscores, or hyphens.
OUTPUT_DIRECTORY is created if needed. A label may be captured only once in a
given directory so a before/after comparison cannot be overwritten by mistake.

The snapshot contains USB registry and system-report facts. It may contain
hardware serial numbers, so keep the directory local and share only targeted
diff excerpts when asking for analysis.
EOF
}

if [[ $# -ne 2 ]]; then
  usage >&2
  exit 64
fi

label="$1"
output_dir="$2"

if [[ ! "$label" =~ ^[A-Za-z0-9_-]+$ ]]; then
  echo "LABEL may contain only letters, digits, underscores, or hyphens." >&2
  exit 64
fi

mkdir -p "$output_dir"

for suffix in metadata.txt system-profiler.json ioreg-usb.txt ioreg-yubico.txt ykman.txt sha256.txt; do
  if [[ -e "$output_dir/$label-$suffix" ]]; then
    echo "Refusing to overwrite existing snapshot: $output_dir/$label-$suffix" >&2
    exit 73
  fi
done

capture() {
  local destination="$1"
  shift
  {
    "$@"
  } >"$destination" 2>&1 || true
}

{
  printf 'label=%s\n' "$label"
  printf 'captured_utc='
  date -u '+%Y-%m-%dT%H:%M:%SZ'
  printf 'host='
  hostname
  printf 'os_version='
  sw_vers -productVersion
  printf 'kernel='
  uname -a
} >"$output_dir/$label-metadata.txt"

capture "$output_dir/$label-system-profiler.json" system_profiler SPUSBDataType -json
capture "$output_dir/$label-ioreg-usb.txt" ioreg -p IOUSB -l -w 0

{
  ioreg -p IOUSB -l -w 0 | grep -i -C 4 -E 'Yubico|YubiKey|0x1050|idVendor.*1050' || true
  ioreg -p IOService -l -w 0 | grep -i -C 4 -E 'Yubico|YubiKey|0x1050|idVendor.*1050' || true
} >"$output_dir/$label-ioreg-yubico.txt" 2>&1

if [[ -x /opt/homebrew/bin/ykman ]]; then
  capture "$output_dir/$label-ykman.txt" /opt/homebrew/bin/ykman list --serials
elif command -v ykman >/dev/null 2>&1; then
  capture "$output_dir/$label-ykman.txt" ykman list --serials
else
  printf 'ykman not found on PATH or at /opt/homebrew/bin/ykman\n' >"$output_dir/$label-ykman.txt"
fi

(cd "$output_dir" && shasum -a 256 "$label-metadata.txt" "$label-system-profiler.json" "$label-ioreg-usb.txt" "$label-ioreg-yubico.txt" "$label-ykman.txt") >"$output_dir/$label-sha256.txt"

printf 'Captured %s in %s\n' "$label" "$output_dir"
