# Final Project 01 — AI Talking Avatar (Airport Guide)

**Your job:** build a kiosk that listens to a traveler, looks up **our** airport documents, speaks the answer, and drives that audio + a photo through **Ditto** so the face talks.

**Watch this first:** play the [expected demo video](./expected_demo/NIA_expected_demo.mp4) or open the [kiosk page](./expected_demo/). That four-beat is the bar. We grade you against [`expected_demo/golden.json`](./expected_demo/golden.json) and [`FINISH_LINE.md`](./FINISH_LINE.md), not against “it sounded fluent.”

The expected demo is **canned**. It does not call Bedrock, Wispr, Kokoro, or Ditto. Your live app must.

← [S18 Final Project](../) · [Course README](../../README.md)

---

## What the traveler can do (the product)

A traveler at the kiosk can:

| They do | What must happen |
|---|---|
| Speak a wayfinding question (“Where is gate C22?”) | You transcribe or stream their speech, search [`data/`](./data/), speak a grounded answer, and **Ditto** lip-syncs the session face to that audio |
| Speak Hindi or Spanish (or French) | They get a spoken answer in that language, still on the Ditto face, without changing a setting |
| Ask something you do not know (“What’s the status of flight NIA 442?”) | The avatar **refuses**. It points to screens / the airline desk. It does not invent a time or a gate |
| Take or upload a photo (after consent) | That face becomes the avatar for the rest of the session. Default concierge is one click away |
| Type instead of speak | Same `search_airport` tool, same citations. Needed if the mic fails |
| See the citation | The chunk file is visible (for example `gates.md`) — not hidden in the model |

They cannot: get visa advice, get a live flight status, have their photo sent to Bedrock, or hear Arabic (Sonic does not support it; Kokoro has no Arabic voice).

---

## What you (the student) do

You build the kiosk. You do **not** invent airport facts. You wire three jobs:

| Job | What does it | What it is not |
|---|---|---|
| **Hear → grounded answer → spoken WAV** | Path A or Path B below | Ditto |
| **Retrieve** | Your `search_airport` tool + ChromaDB on [`data/`](./data/) | The LLM’s memory |
| **Make the photo talk** | [Ditto](https://github.com/antgroup/ditto-talkinghead) | A still JPEG, a CSS oval, or the expected-demo warp |

Mall and customer-support versions are optional stretch (same loop, different documents).

---

## What we give you vs what you write

| We give you | You write |
|---|---|
| This assignment + [`FINISH_LINE.md`](./FINISH_LINE.md) | The running app |
| The NIA documents in [`data/`](./data/) | Ingest + `search_airport` |
| Trap questions in [`data/unknown_traps.json`](./data/unknown_traps.json) | Code that **refuses** those questions |
| [`expected_demo/`](./expected_demo/) (canned bar) | Live Sonic **or** Wispr + Kokoro, plus Ditto |
| [`.env.example`](./.env.example) | A gitignored `.env` |

Do **not** scrape a real airport. Do **not** add live flight APIs. If a fact is not in `data/`, the avatar says it does not know.

---

## Two voice paths (pick one)

You need a spoken **WAV** to feed Ditto. How you get that WAV is your choice.

### Path A — preferred: Amazon Nova Sonic (speech-to-speech)

One Bedrock bidirectional stream: microphone in, spoken audio + transcript + tool calls out. No separate STT or TTS.

- Model: `amazon.nova-2-sonic-v1:0`, or **Nova 2.5 Sonic** if the classroom account has it (better tool-calling; same price as Nova 2; check the Bedrock console — IDs move).
- API: `InvokeModelWithBidirectionalStream` on `bedrock-runtime`.
- Wrapper: Strands `BidiAgent` + `BedrockNovaSonicModel` (you used Strands in S14). Needs **Python 3.12+**.
- Regions: `us-east-1`, `us-west-2`, `eu-north-1`, `ap-northeast-1`.
- Session: about **8 minutes**. Restart or let Strands Bidi do it.
- Languages you may advertise on Path A: English (US / UK / India / Australia), French, Italian, German, Spanish, Portuguese (Brazil), Hindi. **Not Arabic. Not anything else.**
- Default voice: `tiffany` or `matthew` (polyglot — they can switch language in one session).
- RAG: Sonic emits `toolUse` → you run `search_airport` → you send `toolResult` → Sonic speaks only from that.

Docs: [conversational speech](https://docs.aws.amazon.com/nova/latest/nova2-userguide/using-conversational-speech.html) · [languages](https://docs.aws.amazon.com/nova/latest/nova2-userguide/sonic-language-support.html) · [RAG as a Sonic tool](https://docs.aws.amazon.com/nova/latest/userguide/speech-rag.html) · [Strands + Nova Sonic](https://strandsagents.com/docs/user-guide/concepts/bidirectional-streaming/models/nova_sonic/)

### Path B — if you skip Sonic: Wispr Flow (STT) + your RAG + Kokoro TTS

Three steps instead of one stream. Same product, more glue. Ditto is still required.

```
mic WAV
  → Wispr Flow transcribes it to text
  → search_airport(text) → your LLM answers only from the tool
  → Kokoro writes a WAV
  → Ditto(photo, wav) → talking head
```

**Wispr Flow is speech-to-text only.** It does not speak and it does not retrieve.

- Docs: [Voice API intro](https://api-docs.wisprflow.ai/introduction) · [REST transcribe](https://api-docs.wisprflow.ai/rest_api_transcribe) · [WebSocket](https://api-docs.wisprflow.ai/websocket_api)
- Send **16 kHz mono WAV**, base64. REST max **25 MB or 6 minutes** per request. Prefer WebSocket for the kiosk.
- API key stays on **your FastAPI** (`WISPR_API_KEY`). The browser never sees it.
- Wispr documents **100+ languages** and optional `language: ["en"]` (one code forces that language; omit for autodetect, less accurate). Do not promise a language until you have tested that turn.

**Kokoro** is the open-weight TTS ([hexgrad/Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M), Apache-2.0, `pip install kokoro`). It runs **on your machine** — no TTS API key. v1.0 voices cover American / British English, Spanish, French, Hindi, Italian, Brazilian Portuguese, Japanese, and Mandarin. That list includes the Hindi and Spanish demo. **Arabic is not a Kokoro language.** Install `espeak-ng` (needed for English OOD fallback and several non-English languages). Match `lang_code` to the voice (`a` English-US, `e` Spanish, `h` Hindi). Example:

```python
from kokoro import KPipeline
pipeline = KPipeline(lang_code="a")
for gs, ps, audio in pipeline("Gate C22 is in Terminal 2.", voice="af_heart"):
    # audio is 24 kHz — write a WAV and send that file to Ditto
    ...
```

Docs: [GitHub hexgrad/kokoro](https://github.com/hexgrad/kokoro) · [voices](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md)

Path B still needs an LLM to write the answer from `search_airport` (Bedrock text, or the provider you already use in this course). Keep answers short enough to speak.

On Path B, write the languages you actually tested on the kiosk. Hindi or Spanish is still required for the demo. Do not advertise Arabic — Kokoro cannot speak it.

---

## What you must ship to pass

Ditto wants a **GPU** (~5.5 GB VRAM; models ~2.2 GB). Classroom box, capable laptop, or Colab. PyTorch checkpoint first: `ditto_pytorch` + `v0.4_hubert_cfg_pytorch.pkl`. A CSS mouth or an OpenCV warp is **not** a pass.

1. **Listen.** Browser mic → your backend. Push-to-talk is fine at first.
2. **Retrieve.** Every factual answer goes through `search_airport(query)`. Empty tool → “I don’t know” + desk. No invented gates, times, or visa rules.
3. **Speak.** Play the spoken WAV (Sonic **or** Kokoro). Show the transcript.
4. **Cite.** Show the chunk file under the transcript.
5. **Photo face.** Webcam **or** upload. One frontal face. Session-local. **Use default concierge** always exists. Consent before the camera. No minors. Do not send the face to Bedrock / Wispr / Azure.
6. **Ditto.** `source_path` = session photo, `audio_path` = that turn’s WAV, play the output on the kiosk. Default concierge **and** the traveler photo must both talk this way.
7. **Language.** English plus Hindi or Spanish (or French) in one demo, no settings change.
8. **Guardrails.** Wayfinding only. Refuse live flights. Log every tool call.

Also:

- Typed questions work if the mic fails. Document that path in **your** README.
- Keys in `.env` only. Browser never sees them.
- Visible session timer. Keep classroom demos under 2 minutes.

---

## What you do, in order

### Milestone 1 — Grounded text kiosk

1. Read [`data/nia_airport/`](./data/nia_airport/).
2. Ingest **only** [`data/manifest.json`](./data/manifest.json) into ChromaDB (S10-style).
3. Do **not** ingest [`data/unknown_traps.json`](./data/unknown_traps.json).
4. `search_airport(query)` + a simple UI (Streamlit is fine). Type a question, see answer + citation.
5. Photo upload as a **still** face + **Use default concierge**.

**You show:** type “Where is gate C22?” and match [`data/nia_airport/gates.md`](./data/nia_airport/gates.md).

### Milestone 2 — Voice, still face

**Path A:** FastAPI + Strands `BidiAgent` + Sonic. Register `search_airport` as a tool. Headphones, ask C22 out loud.

**Path B:** FastAPI. Mic clip → Wispr → `search_airport` + LLM → Kokoro WAV → play it. Photo can sit still.

**You show:** hear the C22 answer. Citation visible.

### Milestone 3 — Ditto + photo + second language (required)

1. One HTML page for the live kiosk (Streamlit is the wrong live-mic UI).
2. Webcam + consent. Photos under `sessions/` (gitignored).
3. After each spoken turn: Ditto(photo, wav) → play the clip (or stream).
4. Same gate question in Hindi or Spanish on that Ditto face.

**You show:** a volunteer’s photo talking via **Ditto**, then a second language.

### Milestone 4 — Stretch (optional)

Stream Ditto, **or** a mall/support theme pack, **or** a report on all 10 trap questions.

---

## Architecture

**Path A**

```
Browser (HTML)  --WebSocket-->  FastAPI + Strands BidiAgent
                                   │
                                   ▼
                            Nova 2 / 2.5 Sonic
                                   │ tool: search_airport
                                   ▼
                            ChromaDB ← data/nia_airport/
                                   │
                            spoken WAV + session photo
                                   ▼
                                 Ditto  →  face on the kiosk
```

**Path B**

```
Browser  --clip/stream-->  FastAPI
                             │
                             ├─ Wispr Flow STT  →  text
                             ├─ search_airport(text) + LLM
                             ├─ Kokoro TTS  →  WAV
                             └─ Ditto(photo, wav)  →  face on the kiosk
```

Your server is the only process that holds keys.

```
webcam/upload → one-face check → sessions/avatar.png
     → Ditto(avatar.png, turn.wav) → sessions/talk.mp4
```

---

## Stack

| Layer | Path A | Path B (if you skip Sonic) |
|---|---|---|
| Hear | Nova Sonic | [Wispr Flow](https://api-docs.wisprflow.ai/introduction) STT |
| Answer | Sonic + `search_airport` tool | Your LLM + the same `search_airport` tool |
| Speak | Sonic audio out | [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) (`pip install kokoro`) |
| Face | Ditto | Ditto |
| RAG | ChromaDB + sentence-transformers | Same |
| UI | FastAPI + one HTML page | Same |
| GPU | Required for Ditto | Required for Ditto |

Do **not** make these the primary path: React, ElevenLabs, Azure Speech / Copilot TTS, LivePortrait, SadTalker, or real airline APIs.

### Ditto (required on both paths)

[Ditto](https://github.com/antgroup/ditto-talkinghead) — Ant Group, ACM MM 2025, Apache-2.0. One portrait + one audio file → lip-synced video. Checkpoints: [Hugging Face](https://huggingface.co/digital-avatar/ditto-talkinghead). Paper: [arXiv:2411.19509](https://arxiv.org/abs/2411.19509).

```bash
python inference.py \
  --data_root ./checkpoints/ditto_pytorch \
  --cfg_pkl ./checkpoints/ditto_cfg/v0.4_hubert_cfg_pytorch.pkl \
  --audio_path turn.wav \
  --source_path sessions/avatar.png \
  --output_path sessions/talk.mp4
```

Ditto does not transcribe, retrieve, or speak.

---

## Documents you retrieve from

Closed-world fictional **Noor International Airport (NIA)**. Index only `manifest.json`.

| File | Use it for |
|---|---|
| [`data/nia_airport/terminals.md`](./data/nia_airport/terminals.md) | T1 / T2 / T3, airlines, Skywalk |
| [`data/nia_airport/gates.md`](./data/nia_airport/gates.md) | Gates, including **C22** |
| [`data/nia_airport/security.md`](./data/nia_airport/security.md) | Liquids, family lane — not visa law |
| [`data/nia_airport/transport.md`](./data/nia_airport/transport.md) | Metro, taxi, car park, hotel shuttle |
| [`data/nia_airport/amenities.md`](./data/nia_airport/amenities.md) | Prayer room, lost & found, clinic, wifi |
| [`data/nia_airport/hours.md`](./data/nia_airport/hours.md) | Desk hours and phones |
| [`data/nia_airport/faq.md`](./data/nia_airport/faq.md) | Short spoken answers |
| [`data/nia_airport/hi/`](./data/nia_airport/hi/) · [`es/`](./data/nia_airport/es/) | Same facts, Hindi / Spanish |
| [`data/manifest.json`](./data/manifest.json) | Ingest list |
| [`data/unknown_traps.json`](./data/unknown_traps.json) | Refuse these — do not put this in ChromaDB |

System prompt (tighten wording, not the rule):

> You are the NIA airport guide. Answer only from `search_airport` tool results. If the tool is empty, say you do not know and send the traveler to the information desk or the airline desk. You do not know live flights, fares, or visa rulings.

---

## Rules you must not break

1. **Grounding.** A fluent wrong gate is worse than “I don’t know.”
2. **Ditto is required.** Still JPEG + speaker = fail.
3. **No Arabic** on the language list. Sonic does not speak it. Kokoro has no Arabic voice. Path B: only languages you tested from Kokoro’s list.
4. **Photos.** Consent, no minors, local disk only.
5. **Secrets.** `.env` gitignored. Lookup: local `.env`, then `14_Bedrock_AgentCore/.env`, then repo root.

---

## How you get graded

See [`FINISH_LINE.md`](./FINISH_LINE.md). Short version:

- [ ] Voice C22 matches `gates.md`
- [ ] NIA 442 is refused
- [ ] Citation visible
- [ ] Captured photo is the avatar
- [ ] **Ditto** animated that face from the turn WAV
- [ ] Hindi or Spanish spoken on that face
- [ ] No keys in the browser
- [ ] Text-only path documented

Path A or Path B both pass if those boxes tick.

---

## The 90-second demo

1. Default concierge. “Hi, where is gate C22?” → spoken answer + citation + Ditto face.
2. “What’s the status of flight NIA 442?” → refuse.
3. Capture a photo (consent). Same question — **that** face talks via Ditto.
4. Hindi or Spanish — same language back, no settings change.

---

## Suggested layout

```
01_AI_Talking_Avatar/
  README.md                 ← you are here
  FINISH_LINE.md
  .env.example
  data/                     ← we wrote this
  expected_demo/            ← canned bar, not your app
  app/                      ← you write this
    main.py                 FastAPI
    rag.py                  ingest + search_airport
    voice_sonic.py          Path A (optional if you chose B)
    voice_wispr_kokoro.py   Path B (optional if you chose A)
    ditto_run.py
    static/index.html
  sessions/                 gitignored photos + wav + mp4
  checkpoints/              gitignored Ditto weights
```

---

## References

- [Nova 2 Sonic](https://docs.aws.amazon.com/nova/latest/nova2-userguide/using-conversational-speech.html) · [languages](https://docs.aws.amazon.com/nova/latest/nova2-userguide/sonic-language-support.html) · [Nova 2.5 Sonic](https://aws.amazon.com/about-aws/whats-new/2026/10/amazon-nova-2-5-sonic/)
- [Strands Bidi](https://strandsagents.com/blog/bidi-agents-now-ga/) · [Strands + Sonic](https://strandsagents.com/docs/user-guide/concepts/bidirectional-streaming/models/nova_sonic/)
- [Sonic RAG tool](https://docs.aws.amazon.com/nova/latest/userguide/speech-rag.html)
- [Wispr Flow Voice API](https://api-docs.wisprflow.ai/introduction)
- [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) · [inference lib](https://github.com/hexgrad/kokoro) · [voices](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md)
- [Ditto](https://github.com/antgroup/ditto-talkinghead) · [paper](https://arxiv.org/abs/2411.19509)
