# Pages for the newspaper project

The real pages are in [`ground_truth/`](./ground_truth/). The page to score is the faint El Paso Herald front page. Each story in its JSON is one or more boxes that must be merged.

The two files below are fictional practice pages, drawn so the same traps are easy to see.

Two fictional papers from 12 August 1954. Same four stories, same traps, two scripts.

| File | What it is |
|---|---|
| [`harbour_ledger_en.png`](./harbour_ledger_en.png) | English page. This is the one you must pass. |
| [`harbour_ledger_ta.png`](./harbour_ledger_ta.png) | Tamil page. Same layout, so the same code should group it. |
| [`gold_en.json`](./gold_en.json) | Reading order of the English articles. No pixel boxes. |
| [`gold_ta.json`](./gold_ta.json) | Reading order of the Tamil articles. No pixel boxes. |
| [`make_pages.py`](./make_pages.py) | Redraws the pages. You do not need to run it. |

The gold files are the answer key for **this** page. Your boxes still have to come from PaddleOCR. A hardcoded map of this one page does not pass: the demo has to show the predecessor decisions.

`make_pages.py` paints with Chrome on this Mac, because Pillow does not shape Tamil. The pictures are already saved, so students do not need Chrome.
