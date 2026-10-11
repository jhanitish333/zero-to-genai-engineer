# Final Project 02 — Newspaper Digitizer (1954)

**Your job:** take one old newspaper page, find every text box, decide which box is read before which, and hand back one record per article.

← [S18 Final Project](../) · [S17 Decision Models](../../17_Decision_Models/) · [Course README](../../README.md)

---

## What you are building

You are digitizing **The Harbour Ledger**, a fictional Madras paper dated 12 August 1954, and the same page in Tamil (**துறைமுக செய்தி**).

A real 1950s page is not a book. A story starts under a headline, falls down a column, and often continues at the top of the next column. Sometimes it continues **under a different story**. A photograph sits in the middle of a column. The caption belongs to the story. The sentences under the photograph are the same story, not a new one.

The pages in [`data/`](./data/) are built so those traps are visible:

1. **Dock strike.** The headline crosses two columns. The story starts in the left column and continues at the top of the next column.
2. **Temple festival.** It begins under the dock story, in the same column, with its own headline. It then continues in the following column **under the tram story**, with no second headline.
3. **Tram fare.** A short story at the top of a column. The paragraph under the rule is not this story.
4. **Monsoon warning.** A photograph in the middle of the column. The italic line is the caption. The body continues underneath.

S17 gave you a decision model that picks one option and tells you how sure it is. It did not read a page. This project is that pick, repeated: **which earlier box does this box continue?**

Ship the English page. The Tamil page in [`data/`](./data/) is the same traps in another script, drawn for practice. The real scans, with the boxes and the reading order, are in [`data/ground_truth/`](./data/ground_truth/).

---

## The real pages, and the order we expect

Open [`data/ground_truth/README.md`](./data/ground_truth/README.md) for where each scan came from and which file you compare against. The file you are graded on is the El Paso Herald. The other real pages are extra examples. Their JSON names the traps, not every advertisement on the page.

**English.** [*The Newmarket Era and Express*](./data/ground_truth/newmarket_1952-01-31_p1.png), Newmarket, Ontario, Thursday 31 January 1952. Left to right.

Under the masthead, three headlines sit side by side. Each one is its own article:

1. **Sutton Drive** stays in its own column.
2. **School Board Appoints Pritchard** has a headline across two columns. Read the left of those two from top to bottom, then the right one. That right column is not the Mount Albert story. The story stops at the jump line `(Page 7, Col. 4)`.
3. **Mount Albert Man Killed** is the column on the far right. The planning headline under it is a new article.

The big photograph is not an article. The caption under it is one caption in two columns: left column, then right column. The smaller photograph under the right half of that caption belongs to the same story.

**Arabic.** [*Falastin*](./data/ground_truth/falastin_1958-10-31_p1.png), Jerusalem, Friday 31 October 1958. Right to left.

The two lines across the top are a banner. Read each line from the right. They do not flow into the speech. The speech headline is three lines, right to left, upper line first. Its body is the text column on the **right** of the photographs. The headline under the photographs, استقبالات شعبية, is the next article.

**The page you score.** [*El Paso Herald*](./data/ground_truth/elpaso_herald_1920-08-20_p1.png), El Paso, Texas, Friday evening, 20 August 1920. The microfilm is faint. OCR will get some headlines and miss the body. The answer is not the words. It is the boxes in [`elpaso_herald_1920-08-20_p1.json`](./data/ground_truth/elpaso_herald_1920-08-20_p1.json).

Each story is one entry. If `boxes` has more than one box, those boxes are the same story and must be merged. The Villa headline is one box across two columns, and its body is only the left of those two. The war story is the banner, the "Many Cities Taken" headline, then the left column of that story, then the right column, stopping before "U.S.S. Panther." The photograph, the name under it, and the Allendorf body are one story. Court Clerk and Leg Broken are two stories side by side under Ortiz. Anything in `not_a_story` stays out.

**Tamil.** [*செட்டிநாடு*](./data/ground_truth/chettinadu_1955-10_p8.png), Devakottai, October–November 1955, printed page 8. A weekly, left to right. The fictional [`harbour_ledger_ta.png`](./data/harbour_ledger_ta.png) is the easier drill.

The picture, the lines above it, and the verse under it are one plate. The large செட்டிநாடு and the date மன்மத ஜப்பசி 17 are the paper's name and the date, not a paragraph. **கமல ஞானப்பிரகாசர்** starts at that headline and stays in the left column. The right column has no headline and is still a different story: it continues from the previous page. Do not glue it onto Kamala. PaddleOCR `lang="ta"` on this page.

---

## What we give you vs what you write

| We give you | You write |
|---|---|
| This assignment | The running app |
| [`data/harbour_ledger_en.png`](./data/harbour_ledger_en.png) and [`data/harbour_ledger_ta.png`](./data/harbour_ledger_ta.png) | PaddleOCR boxes for every line of type |
| [`data/gold_en.json`](./data/gold_en.json) and [`data/gold_ta.json`](./data/gold_ta.json) | Grouping that matches those practice articles, in that order |
| The scored page [`elpaso_herald_1920-08-20_p1.png`](./data/ground_truth/elpaso_herald_1920-08-20_p1.png) and [`elpaso_herald_1920-08-20_p1.json`](./data/ground_truth/elpaso_herald_1920-08-20_p1.json) | One record per story. Where that JSON lists more than one box, those boxes are the same story |
| The decision shape from S17 | The predecessor menu, the confidence gate, and the log |

Do **not** scrape another paper. Start on the Harbour Ledger if you want the traps in clean type. The page you test and score is the El Paso Herald. Do **not** copy pixel boxes out of `make_pages.py` and call them your detection.

---

## What you must ship to pass

Do these six things. They must run on a **laptop CPU**. You do **not** need a GPU. You do **not** need a vision-language model.

1. **Boxes.** Run PaddleOCR on the English page. Draw every text box on the page. A box is a line or a block of type, not a whole column you drew by hand.
2. **Predecessor.** For each box, decide which earlier box it continues, or that it starts an article. The menu is short. See the rule below.
3. **Confidence gate.** If the decision is not sure, do not glue the boxes. Leave a break a person can fix. Write down the threshold you chose.
4. **Articles.** Walk the predecessor links. Emit one record per article: title, body in order, and the caption if that story has a photograph.
5. **Show the work.** A Streamlit page shows the scan, the boxes, the articles, and the decision log (options, pick, confidence).
6. **Tamil.** Run the same grouping on [`harbour_ledger_ta.png`](./data/harbour_ledger_ta.png) with PaddleOCR `lang="ta"`. The recognition model is the small one, `ta_PP-OCRv3_mobile_rec`. Do not switch languages by sending the picture to a large model.

A typed dump of the four English articles, in gold order, must also work from the command line if Streamlit is awkward in the demo.

---

## What you do, in order

Build four milestones. Each one must run on its own. **Do not start by sending the picture to a large model.**

### Milestone 1 — Boxes on the page

**You do:**

1. Install the CPU build of PaddleOCR. The first run downloads the detection and recognition models.
2. Read [`data/harbour_ledger_en.png`](./data/harbour_ledger_en.png).
3. Draw the boxes on a copy of the page and print the text in each box.
4. Do not sort them into articles yet.

**You show:** the page with boxes, and the words "DOCK STRIKE ENDS AT DAWN" inside a box that is not glued to the tram story.

### Milestone 2 — A short menu, still no model

**You do:**

OCR returns lines. Before any model runs, glue lines that sit in the same column, with a small gap and the same rough height, into one block. That glue is geometry. The decision model runs once per block, not once per line.

Geometry may propose only these predecessors for a block:

- the block above it in the same column, when the gap is small
- the last block of the column to its left
- `NONE`, meaning this block opens an article

That is the whole menu. A block near the top of a column will not have "the block above." A headline is usually `NONE`, but you do not hardcode this page's headlines.

**You show:** for the paragraph that begins "By evening the chariot", the menu includes both the tram paragraph above it and the temple paragraph in the column to the left. You do not pick yet.

### Milestone 3 — The decision model groups the articles

**You do:**

1. For each block, ask a **decision model** to pick one predecessor from that menu.
2. The state is short: the first line of this block, and the first line of each candidate, plus a few words about where the candidate sits ("above in this column", "bottom of the column to the left").
3. Default model: **Strands Decider 2B**, on your machine, the same `choice` shape as [`17_Decision_Models/comparison/deciders.py`](../../17_Decision_Models/comparison/deciders.py). It listens on `http://127.0.0.1:8077/v1/systemone`.
4. If its confidence is below your threshold, try **Jev** for that one block (the S17 client). If Jev is also unsure, leave a break.
5. Compare the articles you built with [`data/gold_en.json`](./data/gold_en.json). The tram fare must not contain the chariot. The monsoon caption must sit with the monsoon story, between the paragraph above the photograph and the paragraph below it.

**You show:** the decision log for the chariot continuation, then the four articles in order.

### Milestone 4 — Tamil, same code

**You do:**

1. Swap the image and the recognition language.
2. Do not rewrite the grouping rules.
3. Compare with [`data/gold_ta.json`](./data/gold_ta.json).

**You show:** the Tamil temple story in one record, with the continuation that sits under the tram fare.

---

## Architecture you must follow

```
  harbour_ledger_en.png  or  harbour_ledger_ta.png
           │
           ▼
  PaddleOCR on CPU          boxes + text     (local, no key)
           │
           ▼
  Geometry                  at most 3 predecessor choices
           │
           ▼
  Strands Decider 2B        pick + confidence  (local)
           │  only if unsure
           ▼
  Jev                       the same choice, one box
           │
           ▼
  Article records           title, body in order, caption
```

The decision model never sees the whole page and never sees the image. PaddleOCR is the only thing that looks at pixels.

---

## Stack you must use

| Layer | Use this |
|---|---|
| Boxes and text | PaddleOCR on CPU. English: the default English recognition model. Tamil: `lang="ta"` (`ta_PP-OCRv3_mobile_rec`) |
| Next-box pick | Strands Decider 2B, local |
| Unsure boxes only | Jev, the S17 `choice` call |
| UI | Streamlit |
| Answer key | [`data/gold_en.json`](./data/gold_en.json), [`data/gold_ta.json`](./data/gold_ta.json) |

**Do not** make these the reader: a vision-language model, GPT, Claude, Gemini, PP-StructureV3's built-in reading order, or a sort by y-then-x. PP-StructureV3 can already guess reading order on clean modern documents. That guess is the thing this project replaces, because a 1950s page breaks it. You may use Paddle only for boxes and text.

A rule printed on the page is ink. It is not an article boundary.

### Why the model stays small

A wrong letter is a typo. A wrong join mixes two news stories. The join is a **pick from two or three options**, which is what a decision model is for. A large model that reads the whole scan will do it, and it will cost more than this project is allowed to cost.

One page, English or Tamil, must stay **under $0.50**. A page that only uses PaddleOCR and Strands Decider 2B costs nothing. Call Jev only for boxes the local model will not take. Do not add a second paid model. Do not send the image anywhere.

---

## Rules you must not break

1. **The menu is short.** Above, previous column, or none. Never "here are all 80 boxes, pick one."
2. **Low confidence is a break**, not a guess you hope is right.
3. **The photograph is not an article.** If OCR emits nothing inside the picture, leave it as a figure. The caption stays with the monsoon story.
4. **Log every pick.** Options, choice, confidence. A perfect gold match with an empty log does not pass.
5. **No extra scans.** The three pages in `data/ground_truth/` are the real papers. If you bring another page for the stretch, you need the right to use it.
6. **Keys.** A Jev key lives in `.env`, the same way as S17. The browser never sees it.

---

## How you get graded

We will run this on a CPU laptop. Tick every box:

- [ ] The English page shows PaddleOCR boxes, not boxes copied from `make_pages.py`.
- [ ] "By evening the chariot…" is in the temple story, not in the tram story.
- [ ] The monsoon caption sits between the two monsoon paragraphs, and the lighthouse drawing is not its own article.
- [ ] I can read the decision log for that chariot join: the options, the pick, and the confidence.
- [ ] A join below the threshold is left broken, not forced.
- [ ] The Tamil practice page groups with the same code and `lang="ta"`.
- [ ] On the El Paso Herald page, every story matches the boxes in `elpaso_herald_1920-08-20_p1.json`. Boxes listed under one article are merged. A box from another article is not. The Villa body is not "Ain't It Wonderful." The war story stops before "U.S.S. Panther."
- [ ] The page did not go to a vision model, and a local run did not need a paid call.

You can miss a few OCR letters and still pass. You cannot merge two stories and pass.

---

## The demo you should practice

1. English page on screen, boxes drawn.
2. Open the log on the chariot continuation. Show the two candidates and the pick.
3. Read out the four articles. The tram fare is only the fare. The temple story includes both pieces.
4. Switch to the Tamil page. Same four stories, no new grouping code.

---

## Stretch (optional, not required to pass)

- A yellowed scan you have the right to use. Same pipeline. Write down what the mobile OCR model got wrong, and do not "fix" it with a vision model.
- A "continued on page 4" line that must **not** be glued to the story on this page.

---

## References

- [PaddleOCR](https://www.paddleocr.ai/) — PP-OCRv5 for English, `ta_PP-OCRv3_mobile_rec` for Tamil
- [PP-StructureV3](https://www.paddleocr.ai/latest/en/version3.x/pipeline_usage/PP-StructureV3.html) — read this so you know the reading-order feature you are **not** using as the answer
- [S17 decision models](../../17_Decision_Models/README.md) — `choice` plus a confidence gate
- [S17 comparison client](../../17_Decision_Models/comparison/deciders.py) — Strands Decider 2B and Jev behind one shape
