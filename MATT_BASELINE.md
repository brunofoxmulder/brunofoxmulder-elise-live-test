# Élise Live Test — Matt baseline with tools

## Scope and provenance

Bruno's requirement is to retain Matt's Gemini Live integration and add tool
capabilities. This candidate starts from `matt123p/ha-gemini-live` version 1.0.9,
commit `d4ad0e523eca92f1c395e82da14d6da0fafd71be` (27 September 2026).
The previous Élise transport changes are removed from this candidate.

The existing `elise_live_test` domain, entity identifiers, HACS repository and
configuration are retained so this is an update to the existing test integration.
The upstream MIT license and attribution are retained.

## Extensions to Matt

| Extension | Boundary | Purpose |
| --- | --- | --- |
| Saved API selection | `tools.py`, config form, API loading | Keep explicit empty choices and temporarily unavailable selections; HA performs native merging, namespacing and dispatch. |
| GetHistory | Recorder module plus declaration/dispatch hooks | Resolve exposed entity names and read history/statistics on both typed and voice paths. |
| Gemini tool-result envelope | `send_tool_responses` only | Preserve objects and wrap scalar/text weather or MCP results in `result`, as required by the SDK. |
| Packaging | Domain, marker, manifest, French labels | Preserve the Élise Live Test installation identity. |

Weather, memory, Investigator and web tools remain the selected Home Assistant
LLM APIs. No custom weather engine, mandatory wake-up tool sequence, clock
injection or extra conversation orchestrator is added.

## Transport preserved

`runtime.py`, `live.py`, `tts.py`, `openai.py`, `utils.py`, `compat.py` and integration
setup match Matt after the domain rename. The voice conversation handoff,
Gemini event reception/configuration and STT entry methods are unchanged.
`tests/matt_contract.json` records the pinned upstream contracts; CI checks them.
The STT receive loop differs only where it declares and dispatches GetHistory.
In particular, this candidate restores Matt's progressive text deltas and removes
the Élise-specific early completion on `generationComplete`.

## Validation and limitations

Local validation uses Python 3.14, real Home Assistant Core 2026.9.4 and
`google-genai==2.21.0`. Tests cover upstream session/audio behavior, pipeline
provenance, late transcript chunks, API selection, Recorder calculations and
SDK acceptance of weather/history/memory results. The suite has 135 tests.

This proves offline contracts and compatibility, not cloud reliability or real
Voice Preview playback. A bounded-audio-buffer/HA streaming-start dependency
was reproduced in isolation in the upstream implementation. It remains an
upstream risk, intentionally not patched in this tool-only candidate. No claim
is made that every cutoff, timeout, wrong spoken hour or model tool omission
has been resolved. Live validation is still required, especially for short
answers, repeated greetings, long replies and conversation completion.

## Deployment status

Candidate branch and draft PR only. No Home Assistant change, pipeline edit,
restart, main-branch merge or release is performed by this development step.
Installation and field validation require Bruno's explicit agreement.
