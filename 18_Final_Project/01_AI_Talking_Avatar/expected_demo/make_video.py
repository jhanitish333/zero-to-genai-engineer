#!/usr/bin/env python3
"""Build the classroom MP4 of the expected four-beat demo.

Uses macOS `say` for speech and ffmpeg to assemble stills.
Run from this folder:  python3 make_video.py
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
OUT = ROOT / "NIA_expected_demo.mp4"
W, H = 1280, 720
NAVY = (7, 16, 24)
PANEL = (14, 26, 36)
AMBER = (240, 162, 2)
MINT = (61, 186, 139)
FOG = (197, 212, 222)
MUTE = (125, 147, 163)
WHITE = (255, 255, 255)
CORAL = (224, 90, 79)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    # Arial Unicode covers Latin + Devanagari so beat 4 is not tofu.
    candidates = [
        Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
        Path("/Library/Fonts/Arial Unicode.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt, width: int) -> list[str]:
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or [""]


def portrait(path: Path, box: tuple[int, int]) -> Image.Image:
    img = Image.open(path).convert("RGB")
    tw, th = box
    src_w, src_h = img.size
    scale = max(tw / src_w, th / src_h)
    img = img.resize((int(src_w * scale), int(src_h * scale)), Image.Resampling.LANCZOS)
    left = (img.width - tw) // 2
    top = max(0, int((img.height - th) * 0.12))
    return img.crop((left, top, left + tw, top + th))


def frame(
    face_path: Path,
    beat: str,
    traveler: str,
    avatar: str,
    cite: str,
    face_label: str,
    talking: bool,
) -> Image.Image:
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 46), fill=AMBER)
    d.text((24, 14), "EXPECTED OUTPUT  ·  this is the bar for your demo", fill=NAVY, font=font(18, True))
    d.text((24, 64), "NOOR INTERNATIONAL  ·  NIA GUIDE", fill=AMBER, font=font(14, True))
    d.text((24, 86), beat, fill=WHITE, font=font(28, True))

    face = portrait(face_path, (360, 480))
    im.paste(face, (40, 140))
    d.rounded_rectangle((40, 140, 400, 620), 8, outline=(30, 53, 68), width=2)
    d.rounded_rectangle((52, 580, 248, 606), 12, fill=(7, 16, 24))
    label = face_label.upper() + ("  ·  SPEAKING" if talking else "")
    d.text((64, 584), label, fill=MINT if talking or "SESSION" in face_label.upper() else MUTE, font=font(12, True))

    x = 440
    d.rounded_rectangle((x, 140, 1240, 250), 10, fill=PANEL)
    d.text((x + 16, 152), "TRAVELER", fill=AMBER, font=font(12, True))
    y = 176
    for line in wrap(d, traveler, font(20), 760):
        d.text((x + 16, y), line, fill=WHITE, font=font(20))
        y += 26

    d.rounded_rectangle((x, 266, 1240, 520), 10, fill=PANEL)
    d.text((x + 16, 278), "AVATAR  ·  spoken from search_airport", fill=MINT, font=font(12, True))
    y = 306
    for line in wrap(d, avatar, font(22), 760):
        d.text((x + 16, y), line, fill=FOG, font=font(22))
        y += 30
    d.rounded_rectangle((x + 16, 470, x + 16 + min(760, d.textlength(cite, font=font(14)) + 24), 502), 12, fill=(20, 51, 40))
    d.text((x + 28, 476), cite, fill=MINT, font=font(14, True))

    d.text((x, 548), "Pass if the facts, citation, face, mouth, and language match this beat.", fill=MUTE, font=font(16))
    d.text((x, 640), "Ditto is stretch. Inventing a status for NIA 442 is a fail.", fill=CORAL, font=font(16))
    return im


def say(text: str, voice: str, dest: Path) -> None:
    subprocess.run(["say", "-v", voice, "-o", str(dest), "--file-format=AIFF", text], check=True)


def silence(dest: Path, seconds: float) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=22050:cl=mono", "-t", str(seconds), str(dest)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def duration(path: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nk=1:nw=1", str(path)],
        text=True,
    )
    return float(out.strip())


def main() -> None:
    concierge = ASSETS / "nia-concierge.jpg"
    traveler = ASSETS / "nia-traveler.jpg"
    beats = [
        {
            "face": concierge,
            "beat": "Beat 1  ·  grounded gate answer",
            "traveler": "Hi, where is gate C22?",
            "avatar": "Gate C22 is in Terminal 2, Concourse C, Level 2. From T2 security it is about a twelve-minute walk. The nearest café is Date Palm Café, two minutes before the gate.",
            "cite": "cited  ·  gates.md  ·  Gate C22",
            "face_label": "Default concierge",
            "user_voice": "Rishi",
            "guide_voice": "Samantha",
        },
        {
            "face": concierge,
            "beat": "Beat 2  ·  refuse live flights",
            "traveler": "What's the status of flight NIA 442?",
            "avatar": "I can't see live flights. Please check the departure screens or the airline desk. I only know the building.",
            "cite": "cited  ·  faq.md  ·  no live operations in corpus",
            "face_label": "Default concierge",
            "user_voice": "Rishi",
            "guide_voice": "Samantha",
        },
        {
            "face": traveler,
            "beat": "Beat 3  ·  photo becomes the avatar",
            "traveler": "Where is gate C22?",
            "avatar": "Still Terminal 2, Concourse C, Level 2 — about twelve minutes from T2 security. Date Palm Café is two minutes before the gate.",
            "cite": "cited  ·  gates.md  ·  Gate C22",
            "face_label": "Session photo",
            "user_voice": "Rishi",
            "guide_voice": "Samantha",
        },
        {
            "face": traveler,
            "beat": "Beat 4  ·  answer in the traveler's language",
            "traveler": "गेट C22 कहाँ है?",
            "avatar": "गेट C22 टर्मिनल 2, Concourse C, लेवल 2 पर है। T2 सिक्योरिटी से लगभग बारह मिनट की पैदल दूरी है। सबसे पास कैफ़े Date Palm Café है।",
            "cite": "cited  ·  hi/gates.md  ·  गेट C22",
            "face_label": "Session photo",
            "user_voice": "Lekha",
            "guide_voice": "Lekha",
        },
    ]

    with tempfile.TemporaryDirectory() as tmp:
        tdir = Path(tmp)
        parts = []
        title = Image.new("RGB", (W, H), NAVY)
        td = ImageDraw.Draw(title)
        td.rectangle((0, 0, W, 46), fill=AMBER)
        td.text((24, 14), "EXPECTED OUTPUT  ·  NIA talking avatar", fill=NAVY, font=font(18, True))
        td.text((80, 220), "This is what a passing demo looks like.", fill=WHITE, font=font(40, True))
        td.text((80, 290), "Four beats. Grounded. Cited. Photo face. Same language back.", fill=FOG, font=font(24))
        td.text((80, 360), "Your app must do this live with Nova Sonic and search_airport.", fill=MUTE, font=font(22))
        title_png = tdir / "title.png"
        title.save(title_png)
        title_a = tdir / "title.aiff"
        say("This is the expected NIA talking avatar demo. Four beats. Grounded, cited, photo face, and the same language back.", "Samantha", title_a)

        def clip(png: Path, audio: Path, name: str) -> Path:
            dest = tdir / f"{name}.mp4"
            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-loop", "1", "-i", str(png),
                    "-i", str(audio),
                    "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-shortest", "-r", "24",
                    str(dest),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return dest

        parts.append(clip(title_png, title_a, "00_title"))

        for i, b in enumerate(beats, start=1):
            listen = frame(b["face"], b["beat"], b["traveler"], "…", "waiting for search_airport", b["face_label"], False)
            listen_png = tdir / f"{i:02d}_listen.png"
            listen.save(listen_png)
            user_a = tdir / f"{i:02d}_user.aiff"
            say(b["traveler"], b["user_voice"], user_a)
            parts.append(clip(listen_png, user_a, f"{i:02d}_user"))

            talk = frame(b["face"], b["beat"], b["traveler"], b["avatar"], b["cite"], b["face_label"], True)
            talk_png = tdir / f"{i:02d}_talk.png"
            talk.save(talk_png)
            guide_a = tdir / f"{i:02d}_guide.aiff"
            say(b["avatar"], b["guide_voice"], guide_a)
            parts.append(clip(talk_png, guide_a, f"{i:02d}_guide"))

        end = Image.new("RGB", (W, H), NAVY)
        ed = ImageDraw.Draw(end)
        ed.rectangle((0, 0, W, 46), fill=AMBER)
        ed.text((24, 14), "THAT FOUR-BEAT IS A PASS", fill=NAVY, font=font(18, True))
        ed.text((80, 220), "If beat 2 invents a flight status, it fails.", fill=WHITE, font=font(34, True))
        ed.text((80, 290), "Ditto lip-sync is stretch. A moving mouth on a photo is enough.", fill=FOG, font=font(22))
        end_png = tdir / "end.png"
        end.save(end_png)
        end_a = tdir / "end.aiff"
        say("That four beat is a pass. If beat two invents a flight status, it fails. Ditto is optional.", "Samantha", end_a)
        parts.append(clip(end_png, end_a, "99_end"))

        lst = tdir / "list.txt"
        lst.write_text("".join(f"file '{p}'\n" for p in parts))
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(OUT)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"Wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
