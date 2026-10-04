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
SDK acceptance of weather/history/memory results. The suite has 139 tests.

This proves offline contracts and compatibility, not cloud reliability or real
Voice Preview playback. A bounded-audio-buffer/HA streaming-start dependency
is characterized with actual Core intent recognition and chat-log streaming
in `tests/test_pipeline_startup.py` (details below). It remains an upstream
limitation, intentionally not patched in this tool-only candidate. No claim
is made that every cutoff, timeout, wrong spoken hour or model tool omission
has been resolved. Live validation is still required, especially for short
answers, repeated greetings, long replies and conversation completion.

### Native pipeline startup limitation

Core 2026.9.4 starts streaming TTS after more than 60 assistant characters,
or a tool call following assistant text. For shorter responses it waits for
intent recognition to return before supplying the final message to TTS.
Matt's conversation handoff waits for the response transcript to finish.
Its provider receive loop awaits audio-buffer space before handling a later
transcript or turn-complete event. The default buffer holds 6400 PCM bytes.

| Synthetic case | Result |
| --- | --- |
| Transcript enabled, 60 characters, three 3200-byte audio chunks | Producer and intent recognition remain pending; TTS has not started. Explicitly starting an audio consumer releases the cycle. |
| Transcript enabled, 61 characters, same audio | Core starts streaming; the response completes. |
| Transcript enabled, 60 characters, only two audio chunks | Audio fits the buffer; the response completes. |
| Transcript disabled, same three audio chunks | Placeholder handoff returns without waiting for the transcript; the response completes. |

The tests call the actual Core `PipelineRun.recognize_intent`, `ChatLog` and
`ResultStream`, and the unchanged Matt conversation handoff and audio stream.
They simulate provider events and a TTS manager consuming PCM. They do not run
the complete STT receive coroutine, network provider, audio conversion, or
satellite playback. The passing characterization test confirms the limitation;
it does not certify the affected configuration as working. A long response may
also stall if the receive loop fills its audio buffer before enough transcript
characters arrive. Disabling interruption does not remove this buffer limit.

This candidate is not approved for transcript-enabled vocal field testing until
the upstream startup dependency is resolved or a separate transport change is
explicitly agreed. Disabling output transcription bypasses this particular
dependency but sacrifices assistant response text; it is not a fix for all
voice failures or a recommended permanent substitute for complete replies.

## Bruno's confirmed scope — 4 October 2026, 13:21 Paris

Bruno confirms: use Matt's integration and add the tools. He reports no errors
when using Matt. The reproduced transcript-enabled laboratory dependency is
not evidence of a fault in his current Matt usage, or of every earlier Élise
cutoff. No startup-buffer or other transport correction is authorized by this
scope confirmation.

Read-only HA checks on this session found both `gemini_live` and
`elise_live_test` loaded, with `gemini-3.8-live`. Matt has
`transcribe_gemini=false`; Élise Live Test has `transcribe_gemini=true`.
The `gemini_live` entities belong to Matt and `gemini_live_2` entities belong
to Élise Live Test. These are dated observations, not permanent configuration
assumptions. No settings were changed.

Direct comparison of this candidate's code at `b338616` with the pinned Matt
commit independently passed all twelve transport contracts, including both
source equality and recorded SHA-256 checks. The remaining differences in
`stt.py`, `conversation.py` and `gemini.py` were reviewed: API selection,
GetHistory declaration/dispatch and SDK result envelopes. These checks do not
run Gemini cloud or Voice Preview playback.

Field comparison should use equivalent settings, including the output
transcription setting used by the working Matt configuration. Installation,
pipeline selection and any setting change require a separate explicit HA
validation from Bruno. The candidate remains a draft; no merge or deployment
is performed by this confirmation.

## Runtime packaging compatibility

The original code review and 139-test baseline used google-genai 2.21.0.
The first test.2 packaging attempt pinned Matt's exact SDK, but Hassfest rejected
it because Home Assistant depends on google-genai 2.25.0. The reviewed runtime
candidate therefore declares google-genai>=2.25.0 (and msgpack==1.1.2): Hassfest
requires a compatible minimum, not a strict pin, for HA-shared packages. CI
installs the manifest requirements constrained to the validated SDK 2.25.0;
the test also verifies the actual installed SDK. A separate dependency contract
records the validated runtime and Matt's upstream dependency separately. The
voice source remains pinned to Matt. SDK equality with upstream is not claimed.
See RECETTE_MATT_OUTILS.md for field checks and separate HA approval.

## Deployment status

Candidate branch and draft PR only. No Home Assistant change, pipeline edit,
restart, main-branch merge or release is performed by this development step.
Installation and field validation require Bruno's explicit agreement.
