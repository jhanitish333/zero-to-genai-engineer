# Document corpus — what you extract from

Six single-language scans, plus one tax invoice with English and Arabic on the same page. Two kinds of paper. The airport is fictional. Nothing on these pages is a real invoice or a real receipt.

The pictures were drawn by [`../tools/render_documents.py`](../tools/render_documents.py). The boxes in [`ground_truth.json`](./ground_truth.json) are the same rectangles the script painted. They are not a guess.

## What you do with these files

The assignment README has the four jobs written out: bounding boxes, classification, summary, and chat. The strings below are the same strings the scorer checks.

1. Open each PNG and read it. The English invoice total is **1942.50**. The receipt number is **WR-88**.
2. Open [`../eval/expected.html`](../eval/expected.html). Click a key, then a value. Only the rectangle you chose should light up. That page is the box specimen. Class, summary, and chat are specified in the assignment README.
3. Score your JSON with [`../tools/score_boxes.py`](../tools/score_boxes.py). It checks `doc_class`, the summary substrings, each field value, and each `value_box` at IoU 0.5. It does not click the chat. You run the chat questions yourself.
4. Do **not** load [`ground_truth.json`](./ground_truth.json) inside the running app. That file is the answer key.
5. Do **not** treat [`unknown_traps.json`](./unknown_traps.json) as a document. It is the chat script: `answer` rows, `refuse` rows, and the refusal sentence `That is not on this page.`

| File | What it is |
|---|---|
| [`documents/en/invoice.png`](./documents/en/invoice.png) | English vendor invoice, INV-1042 |
| [`documents/en/warehouse_receipt.png`](./documents/en/warehouse_receipt.png) | English warehouse receipt, WR-88 |
| [`documents/ta/invoice.png`](./documents/ta/invoice.png) | The same invoice in Tamil |
| [`documents/ta/warehouse_receipt.png`](./documents/ta/warehouse_receipt.png) | The same receipt in Tamil |
| [`documents/ar/invoice.png`](./documents/ar/invoice.png) | The same invoice in Arabic, right to left |
| [`documents/ar/warehouse_receipt.png`](./documents/ar/warehouse_receipt.png) | The same receipt in Arabic |
| [`documents/mixed/tax_invoice_en_ar.png`](./documents/mixed/tax_invoice_en_ar.png) | One page, English and Arabic together |
| [`manifest.json`](./manifest.json) | Every page, with language and class |
| [`labels.json`](./labels.json) | The only class labels you may return |
| [`ground_truth.json`](./ground_truth.json) | Field ids, values, and boxes. Scoring only |
| [`unknown_traps.json`](./unknown_traps.json) | Questions to answer, and questions to refuse |

Numbers, invoice ids, and the names **Noor Trading LLC**, **Harbor Desk Facilities**, and **Sara Rahman** are the same on every single-language page. Dates and item descriptions are written in the page language.

The bilingual page adds two strings that are not on the other six: the Arabic legal name **نور للتجارة ذ.م.م** and the tax number **100287654300003**. Each of those is printed twice, once in each language, and each copy has its own box.

A warehouse receipt has no tax and no total. If the model invents one, it fails.
