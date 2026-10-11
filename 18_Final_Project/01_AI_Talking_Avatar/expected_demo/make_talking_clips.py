#!/usr/bin/env python3
"""Bake lip-moving talking clips from the still portraits + macOS say.

The HTML plays these videos. A still JPEG is not the sample.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
OUT = ASSETS / "talk"
FPS = 24

LINES = [
    {
        "id": "beat1_c22",
        "photo": "nia-concierge.jpg",
        "voice": "Samantha",
        "text": "Gate C22 is in Terminal 2, Concourse C, Level 2. From T2 security it is about a twelve-minute walk. The nearest café is Date Palm Café, two minutes before the gate.",
    },
    {
        "id": "beat2_refuse",
        "photo": "nia-concierge.jpg",
        "voice": "Samantha",
        "text": "I can't see live flights. Please check the departure screens or the airline desk. I only know the building.",
    },
    {
        "id": "beat3_photo",
        "photo": "nia-traveler.jpg",
        "voice": "Samantha",
        "text": "Still Terminal 2, Concourse C, Level 2 — about twelve minutes from T2 security. Date Palm Café is two minutes before the gate.",
    },
    {
        "id": "beat4_hi",
        "photo": "nia-traveler.jpg",
        "voice": "Lekha",
        "text": "गेट C22 टर्मिनल 2, Concourse C, लेवल 2 पर है। T2 सिक्योरिटी से लगभग बारह मिनट की पैदल दूरी है। सबसे पास कैफ़े Date Palm Café है।",
    },
]


def detect_face(bgr: np.ndarray) -> tuple[int, int, int, int]:
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, 1.1, 5, minSize=(120, 120))
    if len(faces) == 0:
        raise RuntimeError("no face")
    return tuple(max(faces, key=lambda f: int(f[2]) * int(f[3])))


def headshot(bgr: np.ndarray, face: tuple[int, int, int, int]) -> tuple[np.ndarray, tuple[int, int, int, int]]:
    x, y, w, h = face
    pad_top = int(h * 0.55)
    pad_side = int(w * 0.45)
    pad_bot = int(h * 0.85)
    x0 = max(0, x - pad_side)
    y0 = max(0, y - pad_top)
    x1 = min(bgr.shape[1], x + w + pad_side)
    y1 = min(bgr.shape[0], y + h + pad_bot)
    crop = bgr[y0:y1, x0:x1]
    fx, fy = x - x0, y - y0
    return crop, (fx, fy, w, h)


def envelope(wav: Path, n_frames: int) -> np.ndarray:
    raw = subprocess.check_output(
        ["ffmpeg", "-i", str(wav), "-f", "f32le", "-acodec", "pcm_f32le", "-ac", "1", "-ar", "24000", "-"],
        stderr=subprocess.DEVNULL,
    )
    samples = np.frombuffer(raw, dtype=np.float32)
    if samples.size == 0:
        return np.zeros(n_frames, dtype=np.float32)
    win = max(1, samples.size // n_frames)
    rms = []
    for i in range(n_frames):
        chunk = samples[i * win : (i + 1) * win]
        rms.append(float(np.sqrt(np.mean(chunk * chunk))) if chunk.size else 0.0)
    env = np.array(rms, dtype=np.float32)
    peak = float(env.max()) or 1.0
    env = np.clip(env / (peak * 0.72), 0, 1)
    kernel = np.array([0.15, 0.7, 0.15], dtype=np.float32)
    env = np.convolve(env, kernel, mode="same")
    return np.clip(env, 0, 1)


def open_mouth(img: np.ndarray, face: tuple[int, int, int, int], amount: float) -> np.ndarray:
    """Pull the lower lip down from the photo itself. No drawn cartoon mouth."""
    if amount < 0.06:
        return img
    h, w = img.shape[:2]
    x, y, fw, fh = face
    mx = x + fw // 2
    my = y + int(fh * 0.74)
    ys = np.arange(h, dtype=np.float32)[:, None]
    xs = np.arange(w, dtype=np.float32)[None, :]
    ny = (ys - my) / (fh * 0.11)
    nx = (xs - mx) / (fw * 0.16)
    fall = np.exp(-(nx * nx + ny * ny * 1.55))
    lower = np.clip((ys - my) / (fh * 0.04), 0.0, 1.0)
    pull = amount * (26.0 + 18.0 * amount) * fall * lower
    map_x = np.repeat(xs, h, axis=0)
    map_y = np.repeat(ys, w, axis=1) - pull
    warped = cv2.remap(img, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    cavity = np.zeros((h, w), np.float32)
    cv2.ellipse(
        cavity,
        (mx, my + int(4 * amount)),
        (max(6, int(fw * 0.11)), max(3, int(2 + 11 * amount))),
        0,
        0,
        360,
        1.0,
        -1,
    )
    cavity = cv2.GaussianBlur(cavity, (13, 13), 0)
    shade = 1.0 - (0.55 * amount * cavity)
    out = np.clip(warped.astype(np.float32) * shade[..., None], 0, 255).astype(np.uint8)
    return out


def blink(img: np.ndarray, face: tuple[int, int, int, int], close: float) -> np.ndarray:
    if close < 0.2:
        return img
    out = img.copy()
    x, y, w, h = face
    for side in (-1, 1):
        ex = x + int(w * (0.5 + side * 0.18))
        ey = y + int(h * 0.39)
        rx, ry = int(w * 0.09), max(1, int(h * 0.03 * (1.2 - close)))
        lid = tuple(int(v) for v in img[ey, ex])
        cv2.ellipse(out, (ex, ey), (rx, max(1, ry)), 0, 0, 360, lid, -1)
    return out


def say(text: str, voice: str, dest: Path) -> None:
    subprocess.run(["say", "-v", voice, "-o", str(dest), "--file-format=AIFF", text], check=True)


def encode(frames: list[np.ndarray], wav: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tdir = Path(tmp)
        for i, frame in enumerate(frames):
            cv2.imwrite(str(tdir / f"{i:05d}.png"), frame)
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-framerate",
                str(FPS),
                "-i",
                str(tdir / "%05d.png"),
                "-i",
                str(wav),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-shortest",
                "-movflags",
                "+faststart",
                str(dest),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def render_line(spec: dict) -> Path:
    photo = cv2.imread(str(ASSETS / spec["photo"]))
    face = detect_face(photo)
    crop, face_c = headshot(photo, face)
    crop = cv2.resize(crop, (540, 720), interpolation=cv2.INTER_AREA)
    face_c = detect_face(crop)

    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "line.aiff"
        say(spec["text"], spec["voice"], wav)
        dur = float(
            subprocess.check_output(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nk=1:nw=1", str(wav)],
                text=True,
            ).strip()
        )
        n = max(8, int(dur * FPS) + 4)
        env = envelope(wav, n)
        frames = []
        for i, amt in enumerate(env):
            frame = crop.copy()
            # Tiny idle motion so it is not a freeze-frame.
            bob = int(round(np.sin(i / 7.0) * 1.2))
            if bob:
                m = np.float32([[1, 0, 0], [0, 1, bob]])
                frame = cv2.warpAffine(frame, m, (frame.shape[1], frame.shape[0]), borderMode=cv2.BORDER_REPLICATE)
            frame = open_mouth(frame, face_c, float(min(1.0, amt * 1.25)))
            # Occasional blink.
            if (i % 55) in (0, 1) and i > 8:
                frame = blink(frame, face_c, 1.0)
            frames.append(frame)
        dest = OUT / f"{spec['id']}.mp4"
        encode(frames, wav, dest)
        idle = OUT / spec["photo"].replace(".jpg", "-idle.jpg")
        cv2.imwrite(str(idle), crop)
        print(f"wrote {dest} ({dest.stat().st_size // 1024} KB, {dur:.1f}s)")
        return dest


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for spec in LINES:
        render_line(spec)


if __name__ == "__main__":
    main()
