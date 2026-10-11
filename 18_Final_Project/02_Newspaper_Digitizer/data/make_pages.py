"""
Draw the two fictional 1954 pages and write the answer keys next to them.

Pillow cannot shape Tamil, so this script builds a small HTML page and asks
Chrome to paint it. The gold files record article text in reading order.
They do not contain pixel boxes. Students must get boxes from PaddleOCR.

Run from this folder:  python3 make_pages.py
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# One teaching page: a headline across two columns, a story that continues
# under a different story, and a photo in the middle of a fourth column.
PAGE_W, PAGE_H = 1240, 1760


EN = {
    "language": "en",
    "paper": "The Harbour Ledger",
    "edition": "Madras, Thursday 12 August 1954",
    "image": "harbour_ledger_en.png",
    "gold": "gold_en.json",
    "font": '"Times New Roman", Times, serif',
    "masthead": "THE HARBOUR LEDGER",
    "articles": [
        {
            "id": "dock_strike",
            "title": "DOCK STRIKE ENDS AT DAWN",
            "headline": "DOCK STRIKE ENDS AT DAWN",
            "left": (
                "The night shift at the Madras harbour put down its placards before sunrise. "
                "Stevedores voted to accept the new wage and return to the cranes. Ships that "
                "had waited in the roads since Monday will begin to unload this afternoon. "
                "The port officer said the first lighter would leave the quay at four."
            ),
            "right": (
                "Families who had slept on the wharf collected their mats and walked home. "
                "Tea stalls along the First Line reopened. A clerk at the harbour office told "
                "this paper that the mail boat would keep her posted hour once the tide turned."
            ),
        },
        {
            "id": "temple_festival",
            "title": "TEMPLE FESTIVAL DRAWS CROWDS",
            "headline": "TEMPLE FESTIVAL DRAWS CROWDS",
            "left": (
                "The car festival at the Kapaleeswarar temple filled the Mylapore streets by noon. "
                "Drummers led the chariot from the east gate. Police kept a lane open for the tram, "
                "which still ran late."
            ),
            # Continues in the next column, under a different story, with no second headline.
            "right": (
                "By evening the chariot had reached the tank. Women sold jasmine at the rail. "
                "The trustee said the procession would rest there overnight and return at dawn. "
                "This paper will print the route again tomorrow."
            ),
        },
        {
            "id": "tram_fare",
            "title": "NEW TRAM FARE FROM MONDAY",
            "headline": "NEW TRAM FARE FROM MONDAY",
            "body": (
                "The city tramways will charge one anna more on the long routes from Monday. "
                "The short stage inside the Fort stays the same. Conductors were told to post "
                "the new card in each car tonight. School tickets are unchanged."
            ),
        },
        {
            "id": "monsoon",
            "title": "MONSOON WARNING FOR THE COAST",
            "headline": "MONSOON WARNING FOR THE COAST",
            "before": (
                "The weather office warned that a fresh monsoon surge will cross the coast late "
                "tonight. Fishing boats at Royapuram were asked to stay in."
            ),
            "caption": "Rain over the harbour mouth, seen from the lighthouse road yesterday evening.",
            "after": (
                "Residents of the low streets behind the beach should move their stores upstairs. "
                "The collector's office will open a shelter at the corporation school. No train "
                "has been cancelled. The warning does not name a cyclone."
            ),
        },
    ],
}

TA = {
    "language": "ta",
    "paper": "துறைமுக செய்தி",
    "edition": "சென்னை, வியாழன் 12 ஆகஸ்ட் 1954",
    "image": "harbour_ledger_ta.png",
    "gold": "gold_ta.json",
    "font": '"Tamil Sangam MN", "Tamil MN", "InaiMathi", serif',
    "masthead": "துறைமுக செய்தி",
    "articles": [
        {
            "id": "dock_strike",
            "title": "துறைமுக வேலைநிறுத்தம் விடிவில் முடிந்தது",
            "headline": "துறைமுக வேலைநிறுத்தம் விடிவில் முடிந்தது",
            "left": (
                "சென்னைத் துறைமுக இரவுப் பணியாளர்கள் சூரிய உதயத்துக்கு முன் போராட்டத்தை நிறுத்தினர். "
                "கூலி உயர்வை ஏற்றுக் கிரேன்களுக்குத் திரும்பினர். திங்கள்கிழமை முதல் கரையில் காத்திருந்த "
                "கப்பல்கள் இன்று பிற்பகலில் சரக்கை இறக்கும்."
            ),
            "right": (
                "குடும்பங்கள் துறைமுகத்தில் விரித்திருந்த பாயைச் சுருட்டி வீடு திரும்பின. "
                "முதல் வரிசையில் தேநீர் கடைகள் திறந்தன. அஞ்சல் கப்பல் தன் நேரத்தில் புறப்படும் "
                "என்று அலுவலகம் தெரிவித்தது."
            ),
        },
        {
            "id": "temple_festival",
            "title": "கோயில் திருவிழாவில் கூட்டம்",
            "headline": "கோயில் திருவிழாவில் கூட்டம்",
            "left": (
                "கபாலீசுவரர் கோயில் தேர் திருவிழா மயிலாப்பூர் வீதிகளை நண்பகலில் நிரப்பியது. "
                "கிழக்கு வாயிலிலிருந்து தேர் புறப்பட்டது. டிராம் செல்ல ஒரு பாதை திறந்து வைக்கப்பட்டது."
            ),
            "right": (
                "மாலையில் தேர் குளத்தை அடைந்தது. மலர் விற்பனை நடந்தது. தேர் இரவு அங்கே தங்கும் "
                "என்று தர்மகர்த்தா கூறினார். நாளை வழித்தடத்தை மீண்டும் அச்சிடுவோம்."
            ),
        },
        {
            "id": "tram_fare",
            "title": "திங்களிலிருந்து புதிய டிராம் கட்டணம்",
            "headline": "திங்களிலிருந்து புதிய டிராம் கட்டணம்",
            "body": (
                "நீண்ட வழித்தடங்களில் டிராம் கட்டணம் திங்கள் முதல் ஒரு அணா உயரும். "
                "கோட்டைக்குள் குறுகிய பயணம் அப்படியே இருக்கும். பள்ளிச் சீட்டு மாறாது."
            ),
        },
        {
            "id": "monsoon",
            "title": "கடலோரத்துக்குப் பருவமழை எச்சரிக்கை",
            "headline": "கடலோரத்துக்குப் பருவமழை எச்சரிக்கை",
            "before": (
                "இன்று இரவு புதிய பருவமழை கரையைக் கடக்கும் என்று வானிலை அலுவலகம் எச்சரித்தது. "
                "ராயபுரம் படகுகள் உள்ளே நிற்கும்படி கேட்டுக் கொள்ளப்பட்டன."
            ),
            "caption": "நேற்று மாலை கலங்கரை விளக்கச் சாலையிலிருந்து தெரிந்த துறைமுக வாயில் மழை.",
            "after": (
                "கடற்கரைக்குப் பின்னால் உள்ள தாழ்ந்த தெருக்கள் பொருள்களை மேலே வைக்க வேண்டும். "
                "ஆட்சியர் அலுவலகம் நகராட்சிப் பள்ளியில் ஒரு தங்குமிடம் திறக்கும். "
                "தொடர்வண்டி எதுவும் நிறுத்தப்படவில்லை."
            ),
        },
    ],
}


def article(page: dict, article_id: str) -> dict:
    return next(a for a in page["articles"] if a["id"] == article_id)


def gold_for(page: dict) -> dict:
    """Reading order inside each article. The photo is a figure, not a block of text."""
    dock = article(page, "dock_strike")
    temple = article(page, "temple_festival")
    tram = article(page, "tram_fare")
    rain = article(page, "monsoon")
    return {
        "paper": page["paper"],
        "edition": page["edition"],
        "language": page["language"],
        "image": page["image"],
        "note": "Blocks inside each article are the reading order. There are no pixel boxes here on purpose.",
        "articles": [
            {
                "id": dock["id"],
                "title": dock["title"],
                "blocks": [
                    {"role": "headline", "text": dock["headline"]},
                    {"role": "body", "text": dock["left"]},
                    {"role": "body", "text": dock["right"]},
                ],
            },
            {
                "id": temple["id"],
                "title": temple["title"],
                "blocks": [
                    {"role": "headline", "text": temple["headline"]},
                    {"role": "body", "text": temple["left"]},
                    {"role": "body", "text": temple["right"]},
                ],
            },
            {
                "id": tram["id"],
                "title": tram["title"],
                "blocks": [
                    {"role": "headline", "text": tram["headline"]},
                    {"role": "body", "text": tram["body"]},
                ],
            },
            {
                "id": rain["id"],
                "title": rain["title"],
                "blocks": [
                    {"role": "headline", "text": rain["headline"]},
                    {"role": "body", "text": rain["before"]},
                    {"role": "caption", "text": rain["caption"]},
                    {"role": "body", "text": rain["after"]},
                ],
            },
        ],
        "figures": [
            {
                "id": "monsoon_photo",
                "article_id": "monsoon",
                "caption": rain["caption"],
            }
        ],
    }


def html_for(page: dict) -> str:
    dock = article(page, "dock_strike")
    temple = article(page, "temple_festival")
    tram = article(page, "tram_fare")
    rain = article(page, "monsoon")
    lang = page["language"]
    # The vertical rule between the first two columns starts under the spanning
    # headline. It must not slice that headline in half.
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<style>
  html, body {{
    margin: 0; padding: 0;
    width: {PAGE_W}px; height: {PAGE_H}px;
    background: #f4ecd6;
    color: #1c1610;
  }}
  .sheet {{
    box-sizing: border-box;
    width: {PAGE_W}px; height: {PAGE_H}px;
    padding: 28px 40px 36px;
    font-family: {page["font"]};
  }}
  header {{
    text-align: center;
    border-top: 3px solid #3c3024;
    border-bottom: 2px solid #3c3024;
    padding: 10px 0 8px;
    margin-bottom: 14px;
  }}
  h1 {{
    font-size: 46px; font-weight: 700;
    letter-spacing: 1px; margin: 6px 0 4px;
    line-height: 1.15;
  }}
  .edition {{
    font-style: italic; font-size: 16px; margin: 0;
  }}
  .cols {{
    display: grid;
    grid-template-columns: 1.4fr 1fr 1fr;
    column-gap: 0;
    align-items: start;
  }}
  .pair {{ padding-right: 14px; }}
  .pair h2 {{
    font-size: 24px; line-height: 1.2; margin: 0 0 10px;
    letter-spacing: 0.2px;
  }}
  .split {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    column-gap: 16px;
  }}
  .split .right {{
    border-left: 1px solid #3c3024;
    padding-left: 14px;
  }}
  .mid, .last {{
    border-left: 1px solid #3c3024;
    padding-left: 14px;
  }}
  h3 {{
    font-size: 20px; line-height: 1.25; margin: 0 0 8px;
  }}
  p {{ font-size: 16px; line-height: 1.35; margin: 0 0 8px; }}
  .follow {{
    border-top: 1px solid #3c3024;
    margin-top: 12px; padding-top: 10px;
  }}
  figure {{ margin: 10px 0; }}
  svg {{ width: 100%; height: 180px; background: #c4bca8; display: block; }}
  figcaption {{
    font-style: italic; font-size: 14px; line-height: 1.3;
    margin-top: 6px;
  }}
  footer {{
    position: absolute; left: 40px; bottom: 18px;
    font-family: "Times New Roman", Times, serif;
    font-style: italic; font-size: 13px; color: #3c3024;
  }}
</style>
</head>
<body>
  <div class="sheet">
    <header>
      <h1>{page["masthead"]}</h1>
      <p class="edition">{page["edition"]}</p>
    </header>
    <div class="cols">
      <div class="pair">
        <h2>{dock["headline"]}</h2>
        <div class="split">
          <p>{dock["left"]}</p>
          <div class="right">
            <p>{dock["right"]}</p>
            <div class="follow">
              <h3>{temple["headline"]}</h3>
              <p>{temple["left"]}</p>
            </div>
          </div>
        </div>
      </div>
      <div class="mid">
        <h3>{tram["headline"]}</h3>
        <p>{tram["body"]}</p>
        <p class="follow">{temple["right"]}</p>
      </div>
      <div class="last">
        <h3>{rain["headline"]}</h3>
        <p>{rain["before"]}</p>
        <figure>
          <svg viewBox="0 0 280 180" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M40 48 C70 20, 120 20, 140 48" fill="none" stroke="#1c1610" stroke-width="2"/>
            <path d="M150 96 L174 150 L126 150 Z" fill="none" stroke="#1c1610" stroke-width="2"/>
            <rect x="158" y="78" width="16" height="22" fill="none" stroke="#1c1610" stroke-width="2"/>
            <line x1="30" y1="158" x2="250" y2="158" stroke="#1c1610" stroke-width="2"/>
          </svg>
          <figcaption>{rain["caption"]}</figcaption>
        </figure>
        <p>{rain["after"]}</p>
      </div>
    </div>
    <footer>A fictional page for this course. Not a real newspaper.</footer>
  </div>
</body>
</html>
"""


def paint(page: dict) -> None:
    if not Path(CHROME).exists():
        raise SystemExit(f"Chrome not found at {CHROME}")
    html = html_for(page)
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        src = folder / "page.html"
        src.write_text(html, encoding="utf-8")
        shot = folder / "page.png"
        subprocess.run(
            [
                CHROME,
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--force-device-scale-factor=1",
                f"--window-size={PAGE_W},{PAGE_H}",
                f"--screenshot={shot}",
                src.as_uri(),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        shutil.copy(shot, HERE / page["image"])
    gold = gold_for(page)
    (HERE / page["gold"]).write_text(
        json.dumps(gold, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    paint(EN)
    paint(TA)
    print("wrote harbour_ledger_en.png, harbour_ledger_ta.png, gold_en.json, gold_ta.json")
