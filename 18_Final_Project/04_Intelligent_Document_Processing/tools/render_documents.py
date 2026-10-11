#!/usr/bin/env python3
"""Draw the classroom pages and write ground_truth.json from the same ink boxes.

The boxes in data/ground_truth.json are the rectangles this script passed to
Pillow. They are not a hand estimate. Re-run this file if you change the copy.

Arabic is reshaped and reordered for display. The stored box is the ink on the
page (image coordinates, origin at the top left), not a mirrored logical box.
"""

import json
import unicodedata
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "documents"

PAGE_W = 1100
PAGE_H = 1560

INK = (26, 26, 26)
MUTED = (70, 84, 99)
NAVY = (22, 50, 79)
PAPER = (255, 255, 255)
RULE = (196, 85, 42)
LINE = (210, 216, 224)
STAMP = (31, 122, 77)

FONT_EN = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_EN_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_TA = "/System/Library/Fonts/Supplemental/Tamil Sangam MN.ttc"
# Arial Unicode contains Arabic presentation forms. Naskh system fonts do not,
# so reshaped Arabic would draw as empty boxes.
FONT_AR = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"


def load_font(path, size):
    return ImageFont.truetype(path, size)


def display_text(text, language):
    """Return the string Pillow should paint. Arabic letters must be joined.

    A digit run such as 5% is pinned left-to-right. The invisible mark used to
    pin it is removed afterwards so the font does not draw an empty box.
    """
    if language != "ar":
        return text
    if not any("\u0600" <= ch <= "\u06FF" for ch in text):
        return text
    pinned = []
    i = 0
    while i < len(text):
        if text[i].isdigit():
            j = i
            while j < len(text) and (text[j].isdigit() or text[j] in "%."):
                j += 1
            pinned.append("\u200e" + text[i:j])
            i = j
        else:
            pinned.append(text[i])
            i += 1
    shaped = get_display(arabic_reshaper.reshape("".join(pinned)))
    return "".join(ch for ch in shaped if unicodedata.category(ch) != "Cf")


def box_from_bbox(bbox):
    left, top, right, bottom = bbox
    return {
        "left": left,
        "top": top,
        "width": right - left,
        "height": bottom - top,
    }


def draw_at(draw, text, x, y, font, fill):
    draw.text((x, y), text, font=font, fill=fill)
    return box_from_bbox(draw.textbbox((x, y), text, font=font))


def draw_right(draw, text, right, y, font, fill):
    width = draw.textlength(text, font=font)
    return draw_at(draw, text, right - width, y, font, fill)


def normalize(box):
    return {
        "left": round(box["left"] / PAGE_W, 4),
        "top": round(box["top"] / PAGE_H, 4),
        "width": round(box["width"] / PAGE_W, 4),
        "height": round(box["height"] / PAGE_H, 4),
    }


class Page(object):
    def __init__(self, language):
        self.language = language
        self.image = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
        self.draw = ImageDraw.Draw(self.image)
        self.fields = []
        if language == "ta":
            self.font = load_font(FONT_TA, 30)
            self.font_bold = load_font(FONT_TA, 32)
            self.font_title = load_font(FONT_TA, 40)
            self.font_small = load_font(FONT_TA, 22)
        elif language == "ar":
            self.font = load_font(FONT_AR, 34)
            self.font_bold = load_font(FONT_AR, 36)
            self.font_title = load_font(FONT_AR, 46)
            self.font_small = load_font(FONT_AR, 24)
        else:
            self.font = load_font(FONT_EN, 26)
            self.font_bold = load_font(FONT_EN_BOLD, 26)
            self.font_title = load_font(FONT_EN_BOLD, 40)
            self.font_small = load_font(FONT_EN, 18)
        self.font_header = load_font(FONT_EN_BOLD, 22)
        self.rtl = language == "ar"

    def paint(self, text, x, y, font, fill, right=None):
        shown = display_text(text, self.language)
        if right is None:
            return draw_at(self.draw, shown, x, y, font, fill)
        return draw_right(self.draw, shown, right, y, font, fill)

    def add_field(self, field_id, key, value, key_box, value_box):
        self.fields.append(
            {
                "id": field_id,
                "key": key,
                "value": value,
                "key_box": normalize(key_box),
                "value_box": normalize(value_box),
            }
        )

    def header(self, title, subtitle):
        self.draw.rectangle((0, 0, PAGE_W, 118), fill=NAVY)
        if self.rtl:
            self.paint("NOOR INTERNATIONAL AIRPORT", 0, 28, self.font_header, (255, 255, 255), right=PAGE_W - 64)
            self.paint(subtitle, 0, 64, self.font_small, (232, 196, 168), right=PAGE_W - 64)
            self.paint(title, 0, 156, self.font_title, INK, right=PAGE_W - 64)
        else:
            self.paint("NOOR INTERNATIONAL AIRPORT", 64, 28, self.font_header, (255, 255, 255))
            self.paint(subtitle, 64, 64, self.font_small, (232, 196, 168))
            self.paint(title, 64, 156, self.font_title, INK)
        self.draw.rectangle((64, 214, PAGE_W - 64, 220), fill=RULE)

    def field_row(self, field_id, key, value, y):
        if self.rtl:
            key_box = self.paint(key, 0, y, self.font, MUTED, right=PAGE_W - 64)
            value_box = self.paint(value, 0, y, self.font_bold, INK, right=560)
        else:
            key_box = self.paint(key, 64, y, self.font, MUTED)
            value_box = self.paint(value, 460, y, self.font_bold, INK)
        self.add_field(field_id, key, value, key_box, value_box)
        self.draw.line((64, y + 46, PAGE_W - 64, y + 46), fill=LINE, width=1)

    def table(self, columns, row, y):
        """columns: list of (field_id or None, header, x or 'right'). row matches columns."""
        self.draw.rectangle((64, y, PAGE_W - 64, y + 48), fill=(244, 246, 248))
        for field_id, header, anchor in columns:
            if anchor == "right":
                self.paint(header, 0, y + 10, self.font_small, MUTED, right=PAGE_W - 80)
            else:
                self.paint(header, anchor, y + 10, self.font_small, MUTED)
        value_y = y + 64
        self.draw.line((64, value_y + 44, PAGE_W - 64, value_y + 44), fill=LINE, width=1)
        for (field_id, header, anchor), cell in zip(columns, row):
            if anchor == "right":
                value_box = self.paint(cell, 0, value_y, self.font_bold, INK, right=PAGE_W - 80)
                key_box = self.paint(header, 0, y + 10, self.font_small, MUTED, right=PAGE_W - 80)
            else:
                value_box = self.paint(cell, anchor, value_y, self.font_bold, INK)
                key_box = self.paint(header, anchor, y + 10, self.font_small, MUTED)
            # Header was already painted above. Paint it again only to measure
            # would double the ink. Measure with textbbox without a second draw.
            if field_id:
                shown_header = display_text(header, self.language)
                if anchor == "right":
                    width = self.draw.textlength(shown_header, font=self.font_small)
                    hx = (PAGE_W - 80) - width
                else:
                    hx = anchor
                key_box = box_from_bbox(
                    self.draw.textbbox((hx, y + 10), shown_header, font=self.font_small)
                )
                self.add_field(field_id, header, cell, key_box, value_box)
        return value_y + 70

    def footer(self, text):
        if self.rtl:
            self.paint(text, 0, PAGE_H - 56, self.font_small, MUTED, right=PAGE_W - 64)
        else:
            self.paint(text, 64, PAGE_H - 56, self.font_small, MUTED)

    def save(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.image.save(path, "PNG")


def build_invoice(language, copy):
    page = Page(language)
    page.header(copy["title"], copy["subtitle"])
    y = 260
    for field_id, key, value in copy["rows"]:
        page.field_row(field_id, key, value, y)
        y += 58
    y += 24
    page.table(copy["columns"], copy["line"], y)
    y = y + 160
    for field_id, key, value in copy["totals"]:
        page.field_row(field_id, key, value, y)
        y += 58
    page.footer(copy["footer"])
    return page


def build_receipt(language, copy):
    page = Page(language)
    page.header(copy["title"], copy["subtitle"])
    # A stamp, not a scored field. It tells a person which form this is.
    # On an Arabic page the title sits on the right, so the stamp sits on the left.
    stamp = display_text(copy["stamp"], language)
    if page.rtl:
        page.draw.rounded_rectangle((64, 142, 380, 200), radius=6, outline=STAMP, width=3)
        draw_at(page.draw, stamp, 88, 152, page.font_bold, STAMP)
    else:
        page.draw.rounded_rectangle((PAGE_W - 340, 142, PAGE_W - 64, 200), radius=6, outline=STAMP, width=3)
        draw_right(page.draw, stamp, PAGE_W - 84, 152, page.font_bold, STAMP)
    y = 280
    for field_id, key, value in copy["rows"]:
        page.field_row(field_id, key, value, y)
        y += 64
    page.footer(copy["footer"])
    return page


INVOICE = {
    "en": {
        "title": "Vendor invoice",
        "subtitle": "Facilities desk",
        "footer": "Classroom copy. Not a real invoice.",
        "rows": [
            ("vendor", "Vendor", "Noor Trading LLC"),
            ("buyer", "Buyer", "Harbor Desk Facilities"),
            ("invoice_number", "Invoice number", "INV-1042"),
            ("invoice_date", "Invoice date", "12 March 2026"),
            ("currency", "Currency", "AED"),
        ],
        "columns": [
            ("item_description", "Item", 80),
            ("quantity", "Qty", 700),
            ("line_amount", "Amount", "right"),
        ],
        "line": ["Gate display repair", "1", "1850.00"],
        "totals": [
            ("tax", "Tax (5%)", "92.50"),
            ("total", "Total", "1942.50"),
            ("payment_terms", "Payment terms", "Due on receipt"),
        ],
    },
    "ta": {
        "title": "விலைப்பட்டியல்",
        "subtitle": "வசதிகள் பணிப்பிரிவு",
        "footer": "வகுப்பறை நகல். இது உண்மையான விலைப்பட்டியல் அல்ல.",
        "rows": [
            ("vendor", "வழங்குநர்", "Noor Trading LLC"),
            ("buyer", "வாங்குபவர்", "Harbor Desk Facilities"),
            ("invoice_number", "விலைப்பட்டியல் எண்", "INV-1042"),
            ("invoice_date", "தேதி", "12 மார்ச் 2026"),
            ("currency", "நாணயம்", "AED"),
        ],
        "columns": [
            ("item_description", "பொருள்", 80),
            ("quantity", "எண்ணிக்கை", 640),
            ("line_amount", "தொகை", "right"),
        ],
        "line": ["வாயில் திரை பழுது", "1", "1850.00"],
        "totals": [
            ("tax", "வரி (5%)", "92.50"),
            ("total", "மொத்தம்", "1942.50"),
            ("payment_terms", "செலுத்தும் விதி", "பெற்றவுடன் செலுத்த வேண்டியது"),
        ],
    },
    "ar": {
        "title": "فاتورة المورّد",
        "subtitle": "قسم المرافق",
        "footer": "نسخة للصف. ليست فاتورة حقيقية.",
        "rows": [
            ("vendor", "المورّد", "Noor Trading LLC"),
            ("buyer", "المشتري", "Harbor Desk Facilities"),
            ("invoice_number", "رقم الفاتورة", "INV-1042"),
            ("invoice_date", "التاريخ", "12 مارس 2026"),
            ("currency", "العملة", "AED"),
        ],
        "columns": [
            ("line_amount", "المبلغ", 80),
            ("quantity", "الكمية", 420),
            ("item_description", "البند", "right"),
        ],
        "line": ["1850.00", "1", "إصلاح شاشة البوابة"],
        "totals": [
            ("tax", "الضريبة 5%", "92.50"),
            ("total", "الإجمالي", "1942.50"),
            ("payment_terms", "شروط الدفع", "مستحق عند الاستلام"),
        ],
    },
}

RECEIPT = {
    "en": {
        "title": "Warehouse receipt",
        "subtitle": "Facilities desk",
        "stamp": "RECEIVED",
        "footer": "Classroom copy. Not a real receipt.",
        "rows": [
            ("receipt_number", "Receipt number", "WR-88"),
            ("receipt_date", "Receipt date", "4 April 2026"),
            ("warehouse", "Warehouse", "T1 Cargo cage"),
            ("received_by", "Received by", "Sara Rahman"),
            ("item_description", "Item", "Replacement display panel"),
            ("quantity", "Quantity", "2"),
            ("condition", "Condition", "Intact"),
        ],
    },
    "ta": {
        "title": "கிடங்கு ரசீது",
        "subtitle": "வசதிகள் பணிப்பிரிவு",
        "stamp": "பெறப்பட்டது",
        "footer": "வகுப்பறை நகல். இது உண்மையான ரசீது அல்ல.",
        "rows": [
            ("receipt_number", "ரசீது எண்", "WR-88"),
            ("receipt_date", "தேதி", "4 ஏப்ரல் 2026"),
            ("warehouse", "கிடங்கு", "T1 சரக்குக் கூண்டு"),
            ("received_by", "பெற்றவர்", "Sara Rahman"),
            ("item_description", "பொருள்", "மாற்று காட்சிப் பலகை"),
            ("quantity", "எண்ணிக்கை", "2"),
            ("condition", "நிலைமை", "சேதமில்லை"),
        ],
    },
    "ar": {
        "title": "إيصال المستودع",
        "subtitle": "قسم المرافق",
        "stamp": "تم الاستلام",
        "footer": "نسخة للصف. ليس إيصالاً حقيقياً.",
        "rows": [
            ("receipt_number", "رقم الإيصال", "WR-88"),
            ("receipt_date", "التاريخ", "4 أبريل 2026"),
            ("warehouse", "المستودع", "قفص البضائع T1"),
            ("received_by", "استلمه", "Sara Rahman"),
            ("item_description", "البند", "لوحة عرض بديلة"),
            ("quantity", "الكمية", "2"),
            ("condition", "الحالة", "سليم"),
        ],
    },
}


def build_mixed_invoice():
    """One UAE-style tax invoice with English and Arabic on the same page.

    A value that is printed once (the invoice number, the amounts) is stored on
    both the English field and the Arabic field, pointing at that same ink.
    """
    image = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(image)
    en = load_font(FONT_EN, 22)
    en_b = load_font(FONT_EN_BOLD, 24)
    en_title = load_font(FONT_EN_BOLD, 28)
    ar = load_font(FONT_AR, 28)
    ar_b = load_font(FONT_AR, 30)
    small = load_font(FONT_EN, 16)
    fields = []

    def paint(text, language, x, y, font, fill, right=None):
        shown = display_text(text, language)
        if right is None:
            return draw_at(draw, shown, x, y, font, fill)
        return draw_right(draw, shown, right, y, font, fill)

    def add(field_id, key, value, key_box, value_box, lang):
        fields.append(
            {
                "id": field_id,
                "key": key,
                "value": value,
                "lang": lang,
                "key_box": normalize(key_box),
                "value_box": normalize(value_box),
            }
        )

    draw.rectangle((0, 0, PAGE_W, 132), fill=NAVY)
    paint("NOOR INTERNATIONAL AIRPORT", "en", 48, 28, load_font(FONT_EN_BOLD, 20), (255, 255, 255))
    paint("Facilities desk  ·  Tax invoice", "en", 48, 72, en, (232, 196, 168))
    paint("مطار نور الدولي", "ar", 0, 24, ar_b, (255, 255, 255), right=PAGE_W - 48)
    paint("فاتورة ضريبية", "ar", 0, 74, ar, (232, 196, 168), right=PAGE_W - 48)

    paint("TAX INVOICE", "en", 48, 160, en_title, INK)
    paint("فاتورة ضريبية", "ar", 0, 156, ar_b, INK, right=PAGE_W - 48)
    draw.rectangle((48, 214, PAGE_W - 48, 220), fill=RULE)

    # Seller and buyer, English on the left, Arabic on the right.
    draw.rectangle((48, 248, 520, 470), outline=LINE, width=2)
    draw.rectangle((580, 248, PAGE_W - 48, 470), outline=LINE, width=2)
    key = paint("Seller", "en", 68, 264, en, MUTED)
    val = paint("Noor Trading LLC", "en", 68, 304, en_b, INK)
    add("seller_en", "Seller", "Noor Trading LLC", key, val, "en")
    key = paint("Address", "en", 68, 352, en, MUTED)
    val = paint("Cargo Village, Dubai", "en", 68, 390, en_b, INK)
    add("seller_address_en", "Address", "Cargo Village, Dubai", key, val, "en")

    key = paint("البائع", "ar", 0, 264, ar, MUTED, right=PAGE_W - 68)
    val = paint("نور للتجارة ذ.م.م", "ar", 0, 308, ar_b, INK, right=PAGE_W - 68)
    add("seller_ar", "البائع", "نور للتجارة ذ.م.م", key, val, "ar")
    key = paint("العنوان", "ar", 0, 360, ar, MUTED, right=PAGE_W - 68)
    val = paint("قرية الشحن، دبي", "ar", 0, 404, ar_b, INK, right=PAGE_W - 68)
    add("seller_address_ar", "العنوان", "قرية الشحن، دبي", key, val, "ar")

    y = 500
    rows = [
        ("buyer_en", "Buyer", "Harbor Desk Facilities", "en", False),
        ("buyer_ar", "المشتري", "مكتب هاربور للمرافق", "ar", True),
        ("invoice_number", "Invoice number", "INV-1042", "en", False),
        ("invoice_number_ar", "رقم الفاتورة", "INV-1042", "ar", True),
        ("invoice_date_en", "Invoice date", "12 March 2026", "en", False),
        ("invoice_date_ar", "التاريخ", "12 مارس 2026", "ar", True),
        ("trn", "TRN", "100287654300003", "en", False),
        ("trn_ar", "الرقم الضريبي", "100287654300003", "ar", True),
    ]
    # Stack each label above its value, English in the left column and Arabic
    # in the right, so the two languages never share a line.
    left_y = y
    right_y = y
    for field_id, label, value, lang, on_right in rows:
        if on_right:
            key_box = paint(label, "ar", 0, right_y, ar, MUTED, right=PAGE_W - 64)
            value_box = paint(value, "ar", 0, right_y + 36, ar_b, INK, right=PAGE_W - 64)
            add(field_id, label, value, key_box, value_box, "ar")
            right_y += 88
        else:
            key_box = paint(label, "en", 56, left_y, en, MUTED)
            value_box = paint(value, "en", 56, left_y + 34, en_b, INK)
            add(field_id, label, value, key_box, value_box, "en")
            left_y += 84

    table_y = max(left_y, right_y) + 28
    draw.rectangle((48, table_y, PAGE_W - 48, table_y + 46), fill=(244, 246, 248))
    headers = [
        ("item_description_en", "Description", "Gate display repair", 64, "en"),
        ("item_description_ar", "الوصف", "إصلاح شاشة البوابة", 430, "ar"),
        ("quantity", "Qty", "1", 780, "en"),
        ("line_amount", "Amount", "1850.00", "right", "en"),
    ]
    for field_id, header, cell, anchor, lang in headers:
        font_h = ar if lang == "ar" else small
        font_v = ar_b if lang == "ar" else en_b
        hy = table_y + 12
        vy = table_y + 64
        if anchor == "right":
            key_box = paint(header, lang, 0, hy, font_h, MUTED, right=PAGE_W - 72)
            value_box = paint(cell, lang, 0, vy, font_v, INK, right=PAGE_W - 72)
        else:
            key_box = paint(header, lang, anchor, hy, font_h, MUTED)
            value_box = paint(cell, lang, anchor, vy, font_v, INK)
        add(field_id, header, cell, key_box, value_box, lang)
    draw.line((48, table_y + 112, PAGE_W - 48, table_y + 112), fill=LINE, width=1)

    total_y = table_y + 140
    pairs = [
        ("tax", "VAT 5%", "92.50", "en"),
        ("tax_ar", "ضريبة 5%", "92.50", "ar"),
        ("total", "Total", "1942.50", "en"),
        ("total_ar", "الإجمالي", "1942.50", "ar"),
        ("payment_terms_en", "Payment terms", "Due on receipt", "en"),
        ("payment_terms_ar", "شروط الدفع", "مستحق عند الاستلام", "ar"),
    ]
    for field_id, label, value, lang in pairs:
        font_k = ar if lang == "ar" else en
        font_v = ar_b if lang == "ar" else en_b
        if lang == "ar":
            key_box = paint(label, "ar", 0, total_y, font_k, MUTED, right=780)
            value_box = paint(value, "ar", 0, total_y, font_v, INK, right=PAGE_W - 64)
        else:
            key_box = paint(label, "en", 560, total_y, font_k, MUTED)
            value_box = paint(value, "en", 0, total_y, font_v, INK, right=PAGE_W - 64)
        add(field_id, label, value, key_box, value_box, lang)
        total_y += 52

    paint("Classroom copy. Not a real tax invoice.", "en", 48, PAGE_H - 64, small, MUTED)
    paint("نسخة للصف. ليست فاتورة حقيقية.", "ar", 0, PAGE_H - 64, load_font(FONT_AR, 22), MUTED, right=PAGE_W - 48)

    class Mixed(object):
        pass

    page = Mixed()
    page.image = image
    page.fields = fields
    page.save = lambda path: image.save(path, "PNG")
    return page


def summary_rules(doc_class, language):
    if doc_class == "invoice":
        must = ["INV-1042", "1942.50", "Noor Trading LLC"]
        if language == "en":
            must.append("Gate display repair")
        elif language == "ta":
            must.append("வாயில் திரை பழுது")
        else:
            must.append("إصلاح شاشة البوابة")
    else:
        must = ["WR-88", "Sara Rahman"]
        if language == "en":
            must.append("Replacement display panel")
        elif language == "ta":
            must.append("மாற்று காட்சிப் பலகை")
        else:
            must.append("لوحة عرض بديلة")
    return must


def main():
    documents = []
    jobs = [
        ("invoice", "invoice", INVOICE, build_invoice),
        ("warehouse_receipt", "warehouse_receipt", RECEIPT, build_receipt),
    ]
    for language in ("en", "ta", "ar"):
        for filename, doc_class, copies, builder in jobs:
            page = builder(language, copies[language])
            rel = Path("documents") / language / (filename + ".png")
            page.save(OUT / language / (filename + ".png"))
            documents.append(
                {
                    "id": language + "_" + filename,
                    "path": rel.as_posix(),
                    "language": language,
                    "doc_class": doc_class,
                    "width": PAGE_W,
                    "height": PAGE_H,
                    "summary_must_include": summary_rules(doc_class, language),
                    "summary_must_not_include": ["+971", "IBAN", "05x"],
                    "fields": page.fields,
                }
            )
            print(rel.as_posix(), len(page.fields), "fields")

    mixed = build_mixed_invoice()
    mixed_rel = Path("documents") / "mixed" / "tax_invoice_en_ar.png"
    (OUT / "mixed").mkdir(parents=True, exist_ok=True)
    mixed.save(OUT / "mixed" / "tax_invoice_en_ar.png")
    documents.append(
        {
            "id": "mixed_tax_invoice",
            "path": mixed_rel.as_posix(),
            "language": "en+ar",
            "doc_class": "invoice",
            "width": PAGE_W,
            "height": PAGE_H,
            "summary_must_include": [
                "INV-1042",
                "1942.50",
                "Noor Trading LLC",
                "نور للتجارة ذ.م.م",
                "100287654300003",
            ],
            "summary_must_not_include": ["+971", "IBAN", "05x"],
            "fields": mixed.fields,
        }
    )
    print(mixed_rel.as_posix(), len(mixed.fields), "fields")

    truth = {
        "coordinate_space": "normalized",
        "origin": "top-left",
        "note": "left, top, width, height are fractions of the page. 0,0 is the top left pixel. Do not mirror Arabic.",
        "documents": documents,
    }
    truth_path = ROOT / "data" / "ground_truth.json"
    truth_path.write_text(json.dumps(truth, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "pages": [
            {"id": doc["id"], "path": doc["path"], "language": doc["language"], "doc_class": doc["doc_class"]}
            for doc in documents
        ]
    }
    (ROOT / "data" / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("wrote", truth_path)
    write_eval_sample(truth)


def write_eval_sample(truth):
    """One HTML file that shows the expected click: one field, one box."""
    payload = json.dumps(truth, ensure_ascii=False).replace("<", "\\u003c")
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Expected result · Document desk</title>
<style>
  :root { --ink:#1a1a1a; --muted:#5c6b7a; --navy:#16324f; --rule:#c4552a; --paper:#f3f1ec; }
  * { box-sizing: border-box; }
  body { margin:0; font:16px/1.45 "Iowan Old Style", Palatino, Georgia, serif; color:var(--ink); background:var(--paper); }
  header { background:var(--navy); color:#fff; padding:18px 28px 16px; }
  header h1 { margin:0; font-size:22px; font-weight:700; letter-spacing:-.01em; }
  header p { margin:6px 0 0; color:#d5dde6; font-size:14px; max-width:70ch; }
  .layout { display:grid; grid-template-columns: minmax(280px, 420px) 1fr; gap:0; min-height: calc(100vh - 92px); }
  aside { border-right:1px solid #ddd; background:#fff; padding:16px 14px 40px; }
  main { padding:18px 22px 48px; }
  .docs { display:flex; flex-direction:column; gap:6px; margin:8px 0 16px; }
  .docs button, .hit { font:600 13px/1.3 ui-sans-serif, system-ui, sans-serif; text-align:left; border:1px solid #ddd; background:#fff; border-radius:6px; padding:8px 10px; cursor:pointer; color:var(--ink); }
  .docs button.on { border-color:var(--navy); background:#eef3f8; }
  .field { display:grid; grid-template-columns: 1fr 1fr; gap:6px; margin:0 0 8px; }
  .hit small { display:block; color:var(--muted); font-weight:500; font-size:11px; }
  .hit.on { border-color:var(--rule); background:#fff4ee; }
  .stage { position:relative; display:inline-block; background:#fff; box-shadow:0 10px 30px rgba(22,50,79,.12); }
  .stage img { display:block; width:min(640px, 72vw); height:auto; }
  .box { position:absolute; border:3px solid var(--rule); background:rgba(196,85,42,.22); box-shadow:0 0 0 1px rgba(255,255,255,.8); pointer-events:none; }
  .readout { margin:0 0 12px; font:600 14px/1.4 ui-sans-serif, system-ui, sans-serif; }
  .readout b { color:var(--rule); }
  h2 { margin:0 0 4px; font-size:15px; }
  @media (max-width: 900px) { .layout { grid-template-columns: 1fr; } aside { border-right:0; border-bottom:1px solid #ddd; } }
</style>
</head>
<body>
<header>
  <h1>What the click must do</h1>
  <p>Pick a document, then pick one key or one value. Only that rectangle lights up. These rectangles are the ground truth painted with the words, not a model guess. Your app has to land on the same ink.</p>
</header>
<div class="layout">
  <aside>
    <h2>Document</h2>
    <div class="docs" id="docs"></div>
    <h2>Fields</h2>
    <div id="fields"></div>
  </aside>
  <main>
    <p class="readout" id="readout">Choose a key or a value.</p>
    <div class="stage" id="stage">
      <img id="page" alt="">
      <div class="box" id="box" hidden></div>
    </div>
  </main>
</div>
<script>
const TRUTH = __TRUTH__;
const docs = document.getElementById('docs');
const fields = document.getElementById('fields');
const page = document.getElementById('page');
const box = document.getElementById('box');
const readout = document.getElementById('readout');
let current = TRUTH.documents[0];

function showBox(rect, label) {
  box.hidden = false;
  box.style.left = (rect.left * 100) + '%';
  box.style.top = (rect.top * 100) + '%';
  box.style.width = (rect.width * 100) + '%';
  box.style.height = (rect.height * 100) + '%';
  readout.innerHTML = 'Highlighting <b>' + label + '</b>';
}

function drawFields() {
  fields.innerHTML = '';
  current.fields.forEach(function (field) {
    const row = document.createElement('div');
    row.className = 'field';
    [['key', field.key, field.key_box], ['value', field.value, field.value_box]].forEach(function (part) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'hit';
      btn.innerHTML = '<small>' + part[0] + (field.lang ? ' · ' + field.lang : '') + '</small>' + part[1];
      btn.onclick = function () {
        document.querySelectorAll('.hit.on').forEach(function (el) { el.classList.remove('on'); });
        btn.classList.add('on');
        showBox(part[2], field.id + ' · ' + part[0] + ' · ' + part[1]);
      };
      row.appendChild(btn);
    });
    fields.appendChild(row);
  });
}

function selectDoc(doc, btn) {
  current = doc;
  document.querySelectorAll('.docs button').forEach(function (el) { el.classList.remove('on'); });
  btn.classList.add('on');
  page.src = '../data/' + doc.path;
  page.alt = doc.id;
  box.hidden = true;
  readout.textContent = doc.id + ' · ' + doc.language + ' · ' + doc.doc_class + '. Choose a key or a value.';
  drawFields();
}

TRUTH.documents.forEach(function (doc, i) {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.textContent = doc.id;
  btn.onclick = function () { selectDoc(doc, btn); };
  docs.appendChild(btn);
  if (i === 0) selectDoc(doc, btn);
});
</script>
</body>
</html>
"""
    html = html.replace("__TRUTH__", payload)
    out = ROOT / "eval" / "expected.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
