# Test receipt

```text
python3 -m unittest discover -s house/terminal_companion/tests -v  # 4 passed
ruff check house/terminal_companion                                # passed
python3 -m compileall -q house/terminal_companion                 # passed
git diff --check                                                   # passed
```

The source seam was verified against the pinned Codex source's app-server
`item/completed` notifications and command-item builder. No live client or
provider was contacted.
