# Final Project 04 — Intelligent Document Desk

**Your job:** upload a page, list the fields on the right, and when someone clicks a field, draw the box on the exact ink.

← [S18 Final Project](../) · [Course README](../../README.md)

---

## What you are building

You are building a desk for **Noor International Airport** facilities paper.

Someone uploads a scan. It may be English, Tamil, or Arabic. Your page must:

1. Show the scan on the left.
2. Show the document class, a short summary, and the attribute list on the right.
3. When they click an attribute, draw that attribute's box on the scan.
4. When they click the box, select the same attribute.
5. Answer questions about **this** page in a chat box, and make each citation clickable so it opens the box.

You already built RAG that cites a file name (S10) and a dining bot that can retrieve (S13). A file name is not enough when the fact is a number printed on a scan. The missing piece is the rectangle on the page.

Ship this against the pages in [`data/`](./data/): English, Tamil, Arabic, and one tax invoice that is **English and Arabic on the same page**. A student may also upload their own PNG. Grading uses the pages we gave you.

Open [`eval/expected.html`](./eval/expected.html) before you write the UI. It is the behavior we mark against. Pick a key or a value. Only that rectangle lights up.

---

## The decision, so you do not mix the tools

Amazon Textract reads forms and tables and returns a box for each key and each value. It reads English, Spanish, German, French, Italian, and Portuguese. It does **not** read Tamil or Arabic. Handwriting, invoices-as-a-special-API, and Queries are English only.

PaddleOCR draws boxes for Tamil (`lang="ta"`) and Arabic (`lang="ar"`). The box is the reliable part. The text inside the box is often wrong: a Tamil letter splits, an Arabic word loses a dot, a total becomes `1942.5O`.

A vision model can read the crop. It cannot be trusted to invent pixel coordinates. So the jobs stay split:

| Language | Who finds the box | Who reads the words | Who writes class, summary, and chat |
|---|---|---|---|
| English | Amazon Textract `AnalyzeDocument` with `FORMS` and `TABLES` | Textract | A Bedrock model, citing Textract block ids |
| Tamil, Arabic | PaddleOCR PP-OCRv5 on CPU | A vision model on Bedrock, which may only correct text for ids Paddle already returned | The same model, citing those ids |

The user picks the language on upload. The choices are **English**, **Tamil**, **Arabic**, and **English and Arabic**. The last choice is the bilingual tax invoice: run both pipelines and merge. Auto-detect is a stretch goal, not the pass bar.

---

## The rule you must not break

The model never outputs a coordinate.

It outputs ids. Your code looks up the box.

That is the same move as a RAG citation. In S10 the model named a chunk id and your code fetched the text. Here the model names a line id and your code fetches the rectangle. If the model names an id you never received from Textract or Paddle, drop it.

Arabic is right to left on the page. The box is still image coordinates: `left` and `top` are the top-left of the ink, as fractions of the page width and height. Do not mirror `left` because the language is Arabic. Paddle's box is already in image space.

---

## What we give you vs what you write

| We give you | You write |
|---|---|
| This assignment | The running app |
| The PNGs in [`data/documents/`](./data/documents/), including the bilingual tax invoice | Upload, the two pipelines, the click-to-box page |
| [`eval/expected.html`](./eval/expected.html) | Match this click. One chosen box, on that ink |
| [`data/ground_truth.json`](./data/ground_truth.json) | A JSON your scorer can check. The app must not read this file |
| [`data/unknown_traps.json`](./data/unknown_traps.json) | Chat that answers the `answer` list and refuses the `refuse` list |
| [`data/labels.json`](./data/labels.json) | Class labels from that list only |
| [`tools/score_boxes.py`](./tools/score_boxes.py) | Nothing. Run it as given |

Do not scrape a real company's invoices. Do not add a live payments API. If a fact is not on the page, the chat says it is not on the page.

---

## What you must ship to pass

Do these eight things. They must work on a **laptop CPU**, an AWS account that can call Textract and Bedrock, and no GPU.

1. **Upload.** PNG or JPG. Show the image. Keep uploads under `sessions/` (gitignored).
2. **English path.** Textract returns keys, values, and boxes. Map them onto the field ids below. Clicking **Total** on the English invoice draws a box on **1942.50**.
3. **Tamil and Arabic path.** PaddleOCR with `ocr_version="PP-OCRv5"` and `device="cpu"`. The default PP-OCRv6 model will not read these scripts. Send the page image plus the line list to a vision model. The model returns corrected text and field groups by line id. Your code attaches the boxes.
4. **Click both ways.** Click a row, see the value box. Click the box, see the row. Key box is optional and may be drawn dashed.
5. **Class.** The exact string for that page, from the classification table below.
6. **Summary.** The exact strings for that page, from the summary table below. Copy them into the summary. Leave out phone numbers and IBANs.
7. **Chat.** Every question in [`data/unknown_traps.json`](./data/unknown_traps.json), with the reply and the one box named there.
8. **Score.** `python3 tools/score_boxes.py your.json` reports IoU at least **0.5** on every value box, the value strings match, and the class matches, for every page in `ground_truth.json`, including `mixed_tax_invoice`.

Also:

- AWS keys live in `.env` only. The browser never sees them. Look up credentials the same way as S14: local `.env`, then `14_Bedrock_AgentCore/.env`, then the repo root.
- Call Textract once per upload. Chat reuses the stored extraction. Textract is paid per page after the free tier.
- Buttons in the UI stay in English.

---

## The four jobs, exactly

[`eval/expected.html`](./eval/expected.html) is the specimen for job 1 only. It draws one box. Class, summary, and chat are specified here and in the JSON files. The running app must not load `ground_truth.json`. You may read it while you build. The scorer reads it. If this README and that file ever disagree, `ground_truth.json` wins.

The file you hand the scorer is one document, or a list:

```json
{
  "documents": [
    {
      "id": "en_invoice",
      "doc_class": "invoice",
      "summary": "Invoice INV-1042 from Noor Trading LLC for Gate display repair. Total 1942.50 AED.",
      "fields": [
        {
          "id": "total",
          "key": "Total",
          "value": "1942.50",
          "value_box": { "left": 0.0, "top": 0.0, "width": 0.0, "height": 0.0 }
        }
      ]
    }
  ]
}
```

The zeros above are a shape, not a real box. A real box comes from Textract or Paddle. Document ids are exactly: `en_invoice`, `en_warehouse_receipt`, `ta_invoice`, `ta_warehouse_receipt`, `ar_invoice`, `ar_warehouse_receipt`, `mixed_tax_invoice`.

Every PNG is **1100 × 1560** pixels. Divide pixel boxes by the width and height of the bitmap you actually sent to the detector. If you resize first, divide by the resized size, and draw the overlay on that same bitmap.

---

### 1. Bounding boxes

A box is four fractions of the page:

| Field | Meaning |
|---|---|
| `left` | Distance from the left edge of the page to the left edge of the ink |
| `top` | Distance from the top edge of the page to the top edge of the ink |
| `width` | Width of the ink, as a fraction of the page width |
| `height` | Height of the ink, as a fraction of the page height |

`0, 0` is the top-left pixel. `1, 1` is the bottom-right corner. Arabic reads right to left. The box stays in this image space. Do not mirror `left`.

**What a click does.** The field list has a key and a value. Click the value, and only `value_box` lights up. Click the key, and only `key_box` lights up. Click the rectangle on the scan, and that same row is selected. One click, one rectangle.

**How a box is scored.** `tools/score_boxes.py` checks `value` and `value_box` only. The value must equal the string in the tables below after you strip spaces at the ends. `1942.50` passes. `1942.5`, `1,942.50`, and `1942.50 AED` fail. Key wording is not scored. IoU is the overlap of your rectangle and the answer rectangle, divided by the area the two rectangles cover together. The pass line is **0.5**.

**English, including the English half of the bilingual page.** Call Amazon Textract `AnalyzeDocument` with `FeatureTypes=["FORMS", "TABLES"]` in `us-east-1`. On each `KEY_VALUE_SET` block, `Geometry.BoundingBox` is already `Left`, `Top`, `Width`, `Height` as fractions. Copy them to `left`, `top`, `width`, `height`. The VALUE block is `value_box`. The KEY block is `key_box`. Use WORD and CELL blocks when the amount sits in a table. Call Textract once per upload.

**Tamil and Arabic.** PaddleOCR 3.x on Python 3.11 or 3.12, `device="cpu"`, `ocr_version="PP-OCRv5"`, `lang="ta"` or `lang="ar"`. Turn off document orientation, unwarping, and text-line orientation. For line `i`:

- draft text is `rec_texts[i]`
- `rec_boxes[i]` is `x_min, y_min, x_max, y_max` in pixels

```
left   = x_min / page_width
top    = y_min / page_height
width  = (x_max - x_min) / page_width
height = (y_max - y_min) / page_height
```

Give each line an id `L0`, `L1`, `L2`. One Bedrock vision call receives the page image and `{id, text, score}`. It may correct the text and it may group lines into fields. It returns `key_ids` and `value_ids` chosen from that list. Drop any id you did not receive from Paddle. If several lines form one value, the box is their union: the smallest rectangle that contains every cited line.

**Bilingual page.** The user picked **English and Arabic**. Run Textract for the English fields and PaddleOCR `lang="ar"` plus the vision model for the Arabic fields. Merge by field id. `quantity` and `line_amount` are printed once, in the English table. They have no Arabic twin.

**Single-language invoices.** Same ids in English, Tamil, and Arabic. Return every row.

| id | English key | English value | Tamil value | Arabic value |
|---|---|---|---|---|
| `vendor` | Vendor | Noor Trading LLC | Noor Trading LLC | Noor Trading LLC |
| `buyer` | Buyer | Harbor Desk Facilities | Harbor Desk Facilities | Harbor Desk Facilities |
| `invoice_number` | Invoice number | INV-1042 | INV-1042 | INV-1042 |
| `invoice_date` | Invoice date | 12 March 2026 | 12 மார்ச் 2026 | 12 مارس 2026 |
| `currency` | Currency | AED | AED | AED |
| `item_description` | Item | Gate display repair | வாயில் திரை பழுது | إصلاح شاشة البوابة |
| `quantity` | Qty | 1 | 1 | 1 |
| `line_amount` | Amount | 1850.00 | 1850.00 | 1850.00 |
| `tax` | Tax (5%) | 92.50 | 92.50 | 92.50 |
| `total` | Total | 1942.50 | 1942.50 | 1942.50 |
| `payment_terms` | Payment terms | Due on receipt | பெற்றவுடன் செலுத்த வேண்டியது | مستحق عند الاستلام |

Tamil keys, in the same id order: வழங்குநர், வாங்குபவர், விலைப்பட்டியல் எண், தேதி, நாணயம், பொருள், எண்ணிக்கை, தொகை, வரி (5%), மொத்தம், செலுத்தும் விதி.

Arabic keys, in the same id order: المورّد, المشتري, رقم الفاتورة, التاريخ, العملة, البند, الكمية, المبلغ, الضريبة 5%, الإجمالي, شروط الدفع. On the Arabic invoice the amount column is on the left and the item text is on the right. Use the box Paddle returns for that ink.

**Single-language warehouse receipts.** There is no `tax` and no `total`. Do not add either.

| id | English key | English value | Tamil value | Arabic value |
|---|---|---|---|---|
| `receipt_number` | Receipt number | WR-88 | WR-88 | WR-88 |
| `receipt_date` | Receipt date | 4 April 2026 | 4 ஏப்ரல் 2026 | 4 أبريل 2026 |
| `warehouse` | Warehouse | T1 Cargo cage | T1 சரக்குக் கூண்டு | قفص البضائع T1 |
| `received_by` | Received by | Sara Rahman | Sara Rahman | Sara Rahman |
| `item_description` | Item | Replacement display panel | மாற்று காட்சிப் பலகை | لوحة عرض بديلة |
| `quantity` | Quantity | 2 | 2 | 2 |
| `condition` | Condition | Intact | சேதமில்லை | سليم |

Tamil keys: ரசீது எண், தேதி, கிடங்கு, பெற்றவர், பொருள், எண்ணிக்கை, நிலைமை.

Arabic keys: رقم الإيصال, التاريخ, المستودع, استلمه, البند, الكمية, الحالة.

**Bilingual tax invoice** `mixed_tax_invoice`. Each language has its own id and its own ink. Clicking **Total** and clicking **الإجمالي** are two different rectangles. Both values are the string `1942.50`.

| id | lang | key | value |
|---|---|---|---|
| `seller_en` | en | Seller | Noor Trading LLC |
| `seller_address_en` | en | Address | Cargo Village, Dubai |
| `seller_ar` | ar | البائع | نور للتجارة ذ.م.م |
| `seller_address_ar` | ar | العنوان | قرية الشحن، دبي |
| `buyer_en` | en | Buyer | Harbor Desk Facilities |
| `buyer_ar` | ar | المشتري | مكتب هاربور للمرافق |
| `invoice_number` | en | Invoice number | INV-1042 |
| `invoice_number_ar` | ar | رقم الفاتورة | INV-1042 |
| `invoice_date_en` | en | Invoice date | 12 March 2026 |
| `invoice_date_ar` | ar | التاريخ | 12 مارس 2026 |
| `trn` | en | TRN | 100287654300003 |
| `trn_ar` | ar | الرقم الضريبي | 100287654300003 |
| `item_description_en` | en | Description | Gate display repair |
| `item_description_ar` | ar | الوصف | إصلاح شاشة البوابة |
| `quantity` | en | Qty | 1 |
| `line_amount` | en | Amount | 1850.00 |
| `tax` | en | VAT 5% | 92.50 |
| `tax_ar` | ar | ضريبة 5% | 92.50 |
| `total` | en | Total | 1942.50 |
| `total_ar` | ar | الإجمالي | 1942.50 |
| `payment_terms_en` | en | Payment terms | Due on receipt |
| `payment_terms_ar` | ar | شروط الدفع | مستحق عند الاستلام |

The rate **5%** is printed inside the tax key (`Tax (5%)`, `வரி (5%)`, `الضريبة 5%`, `VAT 5%`, `ضريبة 5%`). The tax **value** is the amount `92.50`.

---

### 2. Classification

Return one string from [`data/labels.json`](./data/labels.json). The scorer checks that string exactly. `invoice` passes. `Invoice`, `receipt`, and `tax_invoice` fail.

| Uploaded page | `doc_class` |
|---|---|
| `en_invoice`, `ta_invoice`, `ar_invoice`, `mixed_tax_invoice` | `invoice` |
| `en_warehouse_receipt`, `ta_warehouse_receipt`, `ar_warehouse_receipt` | `warehouse_receipt` |
| Any other page | `unknown` |

An invoice is a bill. It has an invoice number and a total. A warehouse receipt records goods received. It has a receipt number. It has no tax line and no total. `unknown` means you will not pretend the page is either of those. The seven graded pages are never `unknown`.

Show the class as a badge above the field list. The model may suggest the class. Your code still has to return one of the three strings.

---

### 3. Summary

A short paragraph above the field list. English prose is fine on a Tamil or Arabic page. The scorer looks for substrings. It does not grade grammar.

Every summary must contain **all** of these strings, copied exactly, including the Tamil or Arabic phrase:

| id | The summary must contain each of these |
|---|---|
| `en_invoice` | `INV-1042`, `1942.50`, `Noor Trading LLC`, `Gate display repair` |
| `ta_invoice` | `INV-1042`, `1942.50`, `Noor Trading LLC`, `வாயில் திரை பழுது` |
| `ar_invoice` | `INV-1042`, `1942.50`, `Noor Trading LLC`, `إصلاح شاشة البوابة` |
| `en_warehouse_receipt` | `WR-88`, `Sara Rahman`, `Replacement display panel` |
| `ta_warehouse_receipt` | `WR-88`, `Sara Rahman`, `மாற்று காட்சிப் பலகை` |
| `ar_warehouse_receipt` | `WR-88`, `Sara Rahman`, `لوحة عرض بديلة` |
| `mixed_tax_invoice` | `INV-1042`, `1942.50`, `Noor Trading LLC`, `نور للتجارة ذ.م.م`, `100287654300003` |

A summary that passes `en_invoice`:

> Invoice INV-1042 from Noor Trading LLC for Gate display repair. The total is 1942.50 AED.

These strings fail the summary if they appear, in any case: `+971`, `IBAN`, `05x`. They are not printed on any page. A warehouse-receipt summary that mentions a tax or a total also fails the demo, even when those digits are absent from the must-not list, because the page has no such line.

---

### 4. Chat

The chat box talks about the **open** document only. The model sees the stored lines and their ids. It does not see the image again, and it does not see the other six pages. One extraction per upload. A chat turn does not call Textract or PaddleOCR.

The browser sends the question to your FastAPI. The response shape is:

```json
{
  "reply": "The total is 1942.50.",
  "citations": [{ "field_id": "total", "box": "value" }]
}
```

`box` is `value` or `key`. The chip draws that one rectangle, using the same highlight as a click on that key or that value. A second rectangle staying lit is a fail.

**Answer questions.** The reply contains `value` exactly, as a substring. Extra words are allowed. `citations` has one item, the `field_id` and `box` in this table.

| Document | Question | Reply contains | Chip |
|---|---|---|---|
| `en_invoice` | What is the total? | `1942.50` | `total` value box |
| `en_invoice` | What is the tax rate? | `5%` | `tax` **key** box. The key ink is `Tax (5%)`. The value ink is `92.50`. Do not answer `92.50` for this question. |
| `ta_invoice` | விலைப்பட்டியல் எண் என்ன? | `INV-1042` | `invoice_number` value box |
| `ar_invoice` | ما رقم الفاتورة؟ | `INV-1042` | `invoice_number` value box |
| `en_warehouse_receipt` | Who received the goods? | `Sara Rahman` | `received_by` value box |
| `ta_warehouse_receipt` | எத்தனை பலகைகள் வந்தன? | `2` | `quantity` value box |
| `ar_warehouse_receipt` | من استلم البضاعة؟ | `Sara Rahman` | `received_by` value box |
| `mixed_tax_invoice` | What is the English total? | `1942.50` | `total` value box, the English number |
| `mixed_tax_invoice` | ما هو الإجمالي؟ | `1942.50` | `total_ar` value box, the Arabic number |
| `mixed_tax_invoice` | What is the TRN? | `100287654300003` | `trn` value box |

On the bilingual page the English total and the Arabic total are the same digits in two places. The question decides which box. "What is the English total?" lights the English `1942.50`. "ما هو الإجمالي؟" lights the Arabic `1942.50`.

**Refusal questions.** The reply is exactly:

> That is not on this page.

`citations` is `[]`. No box lights up. These questions, and strings that must not appear in the reply:

| Document | Question | The reply must not contain |
|---|---|---|
| `en_invoice` | What is the vendor mobile number? | `+971`, `IBAN`, `05` |
| `en_invoice` | What is the IBAN? | `IBAN`, `AE`, `+971` |
| `ta_invoice` | விற்பனையாளரின் தொலைபேசி எண் என்ன? | `+971`, `IBAN`, `05` |
| `ar_invoice` | ما رقم هاتف المورّد؟ | `+971`, `IBAN`, `05` |
| `en_warehouse_receipt` | What is the tax amount? | `92.50`, `5%`, `1942.50`, `1850.00`, `0.00` |
| `ar_warehouse_receipt` | ما هو الإجمالي؟ | `1942.50`, `1850.00`, `92.50` |
| `mixed_tax_invoice` | What is the vendor mobile number? | `+971`, `IBAN`, `05` |
| `mixed_tax_invoice` | What is the IBAN? | `IBAN`, `AE`, `+971` |

The same list is [`data/unknown_traps.json`](./data/unknown_traps.json). Run every row. The English refusal sentence is the pass, including when the question is Tamil or Arabic.

---

## What you do, in order

### Milestone 1 — English invoice, boxes that land

**You do:**

1. Read [`data/documents/en/invoice.png`](./data/documents/en/invoice.png).
2. Call Textract `AnalyzeDocument` with `FeatureTypes=["FORMS", "TABLES"]`.
3. Read `Geometry.BoundingBox` on the KEY and VALUE blocks. Those numbers are already fractions of the page. Use them as-is.
4. Show the image and the field list. Click **Total**. The box sits on `1942.50`.
5. Write `en_invoice` into a JSON file and run the scorer.

**You show:** the English invoice, the total highlighted, and a scorer line `total: pass`.

### Milestone 2 — Tamil and Arabic

**You do:**

1. Run PaddleOCR like this, once for Tamil and once for Arabic. Python **3.11 or 3.12**. Paddle's CPU wheel often fails on 3.13 and 3.14.

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    lang="ta",  # "ar" for Arabic
    ocr_version="PP-OCRv5",
    device="cpu",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)
for page in ocr.predict("data/documents/ta/invoice.png"):
    # page["rec_texts"][i]  draft text
    # page["rec_scores"][i] confidence
    # page["rec_boxes"][i]  x_min, y_min, x_max, y_max in pixels
    pass
```

2. Give each line an id: `L0`, `L1`, `L2`. Convert the pixel box to fractions of width and height. Origin is the top left.
3. One Bedrock vision call. Input: the page image, plus the JSON list of `{id, text, score}`. Output: corrected line text, `doc_class`, `summary`, and fields whose `key_ids` and `value_ids` are chosen from that list.
4. Drop any id that is not in the list. Union the cited line boxes into one `value_box` per field.
5. The Arabic invoice is right to left. Draw the box Paddle returned. Do not flip it.
6. On `mixed_tax_invoice`, run both pipelines. Return all 22 field ids from the bilingual table. **Total** and **الإجمالي** are two boxes.

**You show:** Tamil invoice, click the total, the box is on `1942.50`. Then the same click on the Arabic invoice. Then the bilingual page, with those two totals lighting two different rectangles.

### Milestone 3 — Class, summary, chat

**You do:**

1. Move the desk to **one HTML page**. The image is a canvas (or an image with an SVG overlay). Streamlit is the wrong tool for a box you click on a picture. Keep Streamlit only if you want a debug tab.
2. Class badge from the classification table, and a summary that contains every required string for that page.
3. Chat under the list. The model sees the extracted lines and their ids for this page only.
4. A citation chip calls the same highlight function as a field click. The response is `{ "reply", "citations": [{ "field_id", "box" }] }`.
5. Run every question in [`data/unknown_traps.json`](./data/unknown_traps.json).

**You show:** "What is the vendor mobile number?" replies `That is not on this page.` and lights nothing. "What is the total?" replies with `1942.50` and the chip draws the total value box. "What is the tax rate?" replies with `5%` and the chip draws the **key** `Tax (5%)`. "What is the tax amount?" on the warehouse receipt uses the same refusal sentence.

### Milestone 4 — Stretch (optional, not required to pass)

Pick one:

- Detect the language instead of asking.
- Accept a one-page PDF. Rasterize it, then use the same pipeline.
- Photograph a printout of the English invoice with your phone and still clear IoU 0.5 on the total.

---

## Architecture you must follow

```
  Browser (one HTML page)
    upload, language, image + boxes, field list, chat
           │
           ▼
  Your FastAPI
           │
           ├── English ──► Amazon Textract AnalyzeDocument
           │                 FORMS + TABLES
           │                 boxes come back as fractions
           │
           └── Tamil / Arabic ──► PaddleOCR PP-OCRv5 (CPU)
                                  line id + pixel box + draft text
                                        │
                                        ▼
                                  Bedrock vision
                                  may only cite those line ids
           │
           └── stored extraction ──► chat cites ids ──► browser draws the box
```

Your FastAPI process is the only thing that talks to AWS. Same rule as RAG Studio.

Box contract, for every field you return:

```json
{
  "id": "total",
  "key": "Total",
  "value": "1942.50",
  "value_box": { "left": 0.42, "top": 0.61, "width": 0.08, "height": 0.02 }
}
```

`left`, `top`, `width`, `height` are fractions of the page. `0,0` is the top left. A student file may be one document or `{"documents": [ ... ]}` with `id`, `doc_class`, `summary`, and `fields`.

---

## Stack you must use

| Layer | Use this |
|---|---|
| English boxes | Amazon Textract `AnalyzeDocument`, features `FORMS` and `TABLES` |
| Tamil and Arabic boxes | PaddleOCR 3.x, `lang` `ta` or `ar`, `ocr_version="PP-OCRv5"`, `device="cpu"` |
| Reading Tamil and Arabic words | A vision-capable model on Amazon Bedrock. Try Claude Sonnet on Bedrock first |
| Class, summary, chat | The same Bedrock account. Chat does not need the image if the lines are already corrected |
| Server | FastAPI |
| Live UI | One HTML page, canvas or SVG overlay |
| Score | [`tools/score_boxes.py`](./tools/score_boxes.py) |
| Facts | Every PNG in `data/documents/`, including the bilingual tax invoice. Field ids above |

**Do not** make these the primary path: Tesseract for Tamil or Arabic, asking the model to "guess the bounding box in pixels", React, or a second OCR call on every chat message.

### Install notes

Paddle is heavy and it downloads a model the first time.

```bash
# Python 3.11 or 3.12
python3 -m pip install paddlepaddle paddleocr boto3 fastapi uvicorn pillow
```

Use the CPU wheel from the Paddle install page if the default `paddlepaddle` line fails on your machine. First OCR run downloads the `ta` or `ar` recognition model. That download is expected.

Textract region: `us-east-1` is the safe default. The free tier covers a limited number of pages and then the API is billed. Extract each page once. That is the whole lab.

### IoU, in one line

Overlap area divided by the area of both rectangles together. The scorer's pass line is **0.5**. A box that sits on the right words and is a little loose still passes. A box on the label next door fails.

---

## Documents you extract from

Everything you are graded on is in [`data/`](./data/).

| Page | Class | A fact you should be able to click |
|---|---|---|
| `documents/en/invoice.png` | invoice | Total **1942.50**, invoice **INV-1042** |
| `documents/ta/invoice.png` | invoice | Same total, Tamil labels |
| `documents/ar/invoice.png` | invoice | Same total, Arabic labels, right to left |
| `documents/en/warehouse_receipt.png` | warehouse_receipt | **WR-88**, received by **Sara Rahman**, quantity **2** |
| `documents/ta/warehouse_receipt.png` | warehouse_receipt | Same receipt in Tamil |
| `documents/ar/warehouse_receipt.png` | warehouse_receipt | Same receipt in Arabic |
| `documents/mixed/tax_invoice_en_ar.png` | invoice | English and Arabic on one page. Total **1942.50** appears twice, once beside each language. TRN **100287654300003** |

The tax rate **5%** is printed on the invoice, in the tax label. It is not printed on the receipt.

---

## Rules you must not break

1. **The box comes from the detector.** Textract or Paddle. Never from the language model, and never from `ground_truth.json` at runtime.
2. **No GPU.** Paddle runs on CPU. Do not spend the weekend on CUDA.
3. **One extraction per upload.** Chat reads the stored lines.
4. **Refusal.** A fluent phone number that is not on the page is a fail.
5. **Secrets.** `.env` is gitignored. The browser never holds AWS keys.
6. **Arabic coordinates.** Image space. Top left is zero. Do not mirror.

---

## How you get graded

We will run this on a CPU laptop with AWS credentials. Tick every box:

- [ ] I opened the English invoice, clicked **Total**, and the box was on `1942.50`.
- [ ] `score_boxes.py` passes every page at IoU 0.5, including Tamil, Arabic, and the bilingual tax invoice. Values match the tables, including `1850.00` and `1942.50` with the two decimals.
- [ ] On the bilingual invoice, clicking **Total** and clicking **الإجمالي** highlight two different rectangles.
- [ ] Every page's `doc_class` is the string in the classification table. The warehouse receipt is `warehouse_receipt` and has no `tax` or `total` field.
- [ ] Each summary contains every string in the summary table for that page, and none of `+971`, `IBAN`, `05x`.
- [ ] "What is the vendor mobile number?" replies `That is not on this page.` and lights no box.
- [ ] "What is the total?" replies with `1942.50` and the chip draws the total value box.
- [ ] "What is the tax rate?" replies with `5%` and the chip draws the key `Tax (5%)`, not the amount `92.50`.
- [ ] "What is the tax amount?" on the warehouse receipt uses the refusal sentence and does not say `92.50` or `5%`.
- [ ] Arabic boxes were not mirrored. The total box sits on `1942.50`.
- [ ] `.env` is gitignored. Textract was not called again on each chat turn.

You can fail auto language detection and still pass.

---

## The 90-second demo you should practice

1. Upload the English invoice. Language: English. The badge says `invoice`. The summary contains `INV-1042`, `1942.50`, `Noor Trading LLC`, and `Gate display repair`. Click **1942.50**. The box is on that number.
2. Ask "What is the IBAN?" The reply is `That is not on this page.` No box lights up.
3. Ask "What is the tax rate?" The reply contains `5%`. The chip draws the key `Tax (5%)`.
4. Upload the Arabic invoice. Language: Arabic. Click the total. The box is on `1942.50`. The page is not mirrored.
5. Upload the English warehouse receipt. The badge says `warehouse_receipt`. Ask "What is the tax amount?" The reply is the refusal sentence. Click **Sara Rahman** and the box is on that name.

That sequence is the project: a box, a class, a summary, and a chat citation. A scan-line animation is polish.

---

## References

- [Amazon Textract AnalyzeDocument](https://docs.aws.amazon.com/textract/latest/dg/API_AnalyzeDocument.html)
- [Textract bounding box](https://docs.aws.amazon.com/textract/latest/dg/API_BoundingBox.html) — `Left`, `Top`, `Width`, `Height` are fractions
- [Textract language support](https://aws.amazon.com/textract/faqs/) — English, Spanish, German, French, Italian, Portuguese. Not Tamil. Not Arabic
- [PaddleOCR Python API](https://www.paddleocr.ai/latest/en/version3.x/pipeline_usage/OCR.html) — `rec_texts`, `rec_boxes`, `lang="ta"`, `lang="ar"`, PP-OCRv5
- [PP-OCRv5 multilingual models](https://www.paddleocr.ai/latest/en/version3.x/algorithm/PP-OCRv5/PP-OCRv5_multi_languages.html) — `ta_PP-OCRv5_mobile_rec`, `arabic_PP-OCRv5_mobile_rec`
