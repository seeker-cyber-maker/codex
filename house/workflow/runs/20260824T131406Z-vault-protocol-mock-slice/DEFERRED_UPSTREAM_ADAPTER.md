# Deferred Chrome/app-server adapter investigation

## Verified seam

The installed Chrome extension `hehggadaopoacecdllhhajmbjkdcmajg`, version
`1.2.27268.51612`, connects through native messaging to
`com.openai.codexextension`. The signed proprietary host launches the signed
Codex plugin app-server selected by `~/.codex/chrome-native-hosts-v2.json`.
Live process/socket inspection established this topology:

```text
Chrome extension -> native messaging host -> Codex app-server
```

This proves an upstream Codex app-server seam. It does not prove a ChatGPT
Chat/Work prompt-submission or response-retrieval lane.

## Architectural disposition

Keep browser/native-host compatibility outside upstream core as a Dream House
adapter. Do not edit the live registry or native-host manifest. A future test
may point a disposable isolated registry/manifest at the Dream House source
build and verify only protocol-v2 handshake compatibility.

## Reopen trigger

Reopen after the current vault candidate receives independent review and only
with an isolated test home. The browser seam grants no secret, provider,
dispatch, or promotion authority.
