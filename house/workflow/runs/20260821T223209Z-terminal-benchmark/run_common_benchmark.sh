#!/bin/zsh
set -u

if (( $# != 1 )); then
  print -u2 -- "usage: run_common_benchmark.sh RESULT_FILE"
  exit 64
fi

result_file=$1
benchmark_bin=/Applications/kitty.app/Contents/MacOS/kitten

{
  print -- "schema=terminal-benchmark-result/1"
  print -- "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  print -- "term=${TERM:-unset}"
  print -- "term_program=${TERM_PROGRAM:-unset}"
  print -- "term_program_version=${TERM_PROGRAM_VERSION:-unset}"
  print -- "benchmark=ascii,unicode,csi"
  print -- "repetitions=5"
} >| "$result_file"

"$benchmark_bin" __benchmark__ --repetitions 5 ascii unicode csi >> "$result_file" 2>&1
status=$?

{
  print -- "exit_status=$status"
  print -- "finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} >> "$result_file"

exit "$status"
