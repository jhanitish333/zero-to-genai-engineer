# Finish line — NIA Talking Avatar

You are finished only when **all four gates** pass. A kiosk that opens and a model that chats are not the finish line. A traveler must hear a grounded answer on a **Ditto** face.

Voice may be **Path A (Nova Sonic)** or **Path B (Wispr Flow STT + Kokoro TTS)**. The finish line does not change.

| Gate | Proves | Pass looks like |
|---|---|---|
| 1. Grounded text | RAG only uses [`data/`](./data/) | Typed C22 matches `gates.md`; citation visible |
| 2. Voice | Hear → retrieve → speak | Spoken C22; spoken refuse on NIA 442 |
| 3. Ditto face | Photo + turn WAV → talking head | Default concierge **and** a captured photo both lip-sync |
| 4. Language | Same product, second language | Hindi or Spanish spoken back on that Ditto face |

Do gate 1 before you fight Bedrock or Wispr. Do gate 2 before you fight CUDA.

---

## Gate 1 — typed RAG

| # | Do this | Pass |
|---|---|---|
| 1 | Type “Where is gate C22?” | Answer says Terminal 2, Concourse C, about 12 minutes, Date Palm Café |
| 2 | Citation | UI shows `gates.md` or `faq.md` |
| 3 | Type “What is the status of flight NIA 442?” | Refuse. No “on time”, “delayed”, or a gate number |
| 4 | Upload a photo, then “Use default concierge” | Face switches both ways |

If any of these fail, stop. Voice will not fix a wrong corpus.

---

## Gate 2 — voice (Path A or Path B)

| # | Do this | Pass |
|---|---|---|
| 1 | Say “Hi, where is gate C22?” | You **hear** the same facts as gate 1 |
| 2 | Say “What’s the status of flight NIA 442?” | You **hear** a refuse; screens or airline desk |
| 3 | Watch the log | `search_airport` ran. Browser has no API keys |
| 4 | Your README | Names Path A or Path B and how to run text-only |

Path A: Sonic audio. Path B: Wispr transcript → Kokoro WAV. Either is a pass.

---

## Gate 3 — Ditto

| # | Do this | Pass |
|---|---|---|
| 1 | Default concierge, ask C22 | The **photo talks** (Ditto clip or stream), not a still JPEG |
| 2 | Capture or upload a face (consent) | That face is now the avatar |
| 3 | Ask C22 again | **That** face is Ditto-animated from this turn’s WAV |

A CSS oval, the expected-demo warp, or LivePortrait/SadTalker is a miss. Ditto is the locked face model.

---

## Gate 4 — second language

| # | Do this | Pass |
|---|---|---|
| 1 | Ask the C22 question in Hindi **or** Spanish (or French) | Spoken answer in that language |
| 2 | Face | Still the session Ditto face |
| 3 | Path A kiosk copy | Lists only Sonic’s seven languages (no Arabic) |
| 4 | Path B kiosk copy | Lists only languages you tested |

---

## What this does not grade

How pretty the HTML is, whether Ditto is streamed or clip-after-turn, and whether you chose Path A or Path B. Those can be discussed in the demo. They are not the finish line.
