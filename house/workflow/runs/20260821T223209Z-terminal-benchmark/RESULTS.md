# Local terminal benchmark results

## Verdict

This run does **not** establish a five-terminal winner. It produced useful
bounded measurements for iTerm2, Kitty, and Ghostty, but Warp and Wave lacked a
safe arbitrary-command lane under the frozen rules. The retained numbers are
terminal-response-loop throughput from Kitty's benchmark, not startup time,
keyboard latency, frame pacing, GPU use, energy, or a complete rendering score.

The strongest engineering result is architectural: iTerm2's typed Python API
was the cleanest automation seam. It created and closed one exact benchmark
window while preserving the user's live sessions, which supports keeping
iTerm2 as the Dream House host even though its throughput numbers were lower in
this particular tool.

## Retained measurements

Each case sends five payload repetitions inside one benchmark invocation. MB/s
is the tool's reported payload bytes divided by the interval ending after three
terminal device-status responses.

### Default benchmark mode

| Terminal | ASCII MB/s | Unicode MB/s | CSI MB/s | Comparability note |
| --- | ---: | ---: | ---: | --- |
| iTerm2 3.7.0beta9 | 4.3 | 6.5 | 1.0 | synchronized-output suppression had no material effect in the paired run; likely includes work omitted by supporting terminals |
| Kitty 0.48.2 | 73.3 | 106.4 | 38.2 | fresh `--config NONE`; clean fixed-command receipt |
| Ghostty 1.3.1 | 46.1 | 91.8 | 34.4 | default files and saved-window restoration disabled; bundle lifecycle still required cleanup |

Raw canonical receipts: `iterm-common.txt`, `kitty-common.txt`, and
`ghostty-common-clean.txt`.

### Explicit `--render` proxy

| Terminal | ASCII MB/s | Unicode MB/s | CSI MB/s | Interpretation |
| --- | ---: | ---: | ---: | --- |
| iTerm2 3.7.0beta9 | 4.5 | 6.4 | 0.9 | essentially unchanged from default mode |
| Kitty 0.48.2 | 71.4 | 30.8 | 37.0 | Unicode slowed; asynchronous rendering prevents a frame-pacing claim |
| Ghostty 1.3.1 | 79.4 | 106.0 | 41.5 | faster than its default-mode sample, directly demonstrating single-run/asynchronous proxy noise |

Raw canonical receipts: `iterm-render.txt`, `kitty-render.txt`, and
`ghostty-render-clean.txt`.

The Ghostty reversal is why these figures must not become a terminal ranking.
At least five independent invocations, fixed geometry/font, a dedicated frame
capture method, and controlled foreground state are still required for a
performance publication. Human-gated permission prompts make launch and
time-to-first-token unsuitable on the current host unless separately
instrumented and explicitly annotated.

## Dream House implications

1. Keep iTerm2 as the main host. Its exact object API and session preservation
   matter more to the harness than winning a parser microbenchmark.
2. Keep parser throughput, rendered frame pacing, input latency, resource use,
   correctness, and aesthetics as separate scorecards. Never collapse them
   into one “fastest terminal” score.
3. Add a benchmark preflight that detects human-gated dialogs and foreground
   requirements, then marks launch timing unavailable instead of waiting on a
   misleading clock.
4. Preserve an explicit terminal target handle. Kitty's focus stall and
   Ghostty's post-command lifecycle show why ambient focus and process-name
   cleanup are insufficient.
5. The visual fixture remains human-reviewed. The future dashboard should let
   the user score legibility, grouping, focus recovery, and fatigue without
   giving the harness arbitrary terminal input authority.

## Non-canonical exploratory files

`ghostty-common.txt` and `ghostty-render.txt` came from earlier Ghostty launches
before the saved-window-restoration control was added. They are retained as
lineage but excluded from the tables.
