# Expected demo — show this to students first

This is the **bar**, not the solution. It is a canned four-beat run. Students must reproduce it live with `search_airport` + **Ditto** + either **Nova Sonic (Path A)** or **Wispr Flow STT + Kokoro TTS (Path B)**.

## Show it in class

**Fastest:** play [`NIA_expected_demo.mp4`](./NIA_expected_demo.mp4) (about 60 seconds, no Bedrock, no GPU). AirPlay or share the screen.

**Interactive:** open [index.html](./index.html), click **Play expected demo**, turn on the speaker. Each avatar answer is a **talking-head clip** (the face moves and the line is spoken). It is not a still photo. Pause after beat 2 and say: if your avatar invents a status for flight NIA 442, you fail.

Pages URL after push to `main`:

https://nursnaaz.github.io/zero-to-genai-engineer/18_Final_Project/01_AI_Talking_Avatar/expected_demo/

GitHub’s file view shows HTML source. Always open the Pages link, not the repo blob.

## Grade against the golden file

[`golden.json`](./golden.json) is the rubric:

| Beat | Pass | Fail |
|---|---|---|
| 1 C22 | Facts from `gates.md`, citation visible, mouth moves | Wrong terminal, no citation, frozen face |
| 2 NIA 442 | Refuses; points to screens / airline desk | Says on time / delayed / a gate |
| 3 Photo | Captured face is now the avatar | Still the default concierge |
| 4 Hindi (or Spanish) | Answers in that language | Asks them to speak English |

The live app must use **Ditto** for the face. Voice is Path A (Nova Sonic) or Path B (Wispr + Kokoro). This folder is a canned stand-in so you can show the four beats before anyone has a GPU. Grade the live demo with [`../FINISH_LINE.md`](../FINISH_LINE.md).

## What this folder is not

It does not call Bedrock. It does not search ChromaDB. The faces are sample portraits. Students replace the canned script with their live loop.
