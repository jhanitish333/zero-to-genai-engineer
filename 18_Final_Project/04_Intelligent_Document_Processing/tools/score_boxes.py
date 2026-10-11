#!/usr/bin/env python3
"""Score a student extraction against data/ground_truth.json.

The value must match, and the value box must cover the ink. IoU is the overlap
of the two rectangles divided by the area they cover together. 1.0 is a perfect
cover. 0.5 means the box is on the right words even if the edges are loose.

Usage:
    python3 tools/score_boxes.py path/to/student.json
    python3 tools/score_boxes.py path/to/student.json --iou 0.5
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRUTH_PATH = ROOT / "data" / "ground_truth.json"
PASS_IOU = 0.5


def iou(a, b):
    ax2 = a["left"] + a["width"]
    ay2 = a["top"] + a["height"]
    bx2 = b["left"] + b["width"]
    by2 = b["top"] + b["height"]
    ix1 = max(a["left"], b["left"])
    iy1 = max(a["top"], b["top"])
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    union = a["width"] * a["height"] + b["width"] * b["height"] - inter
    if union <= 0:
        return 0.0
    return inter / union


def load_student(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if "documents" in data:
        return {doc["id"]: doc for doc in data["documents"]}
    if "id" in data:
        return {data["id"]: data}
    sys.exit("student JSON needs an id, or a documents list")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("student_json")
    parser.add_argument("--iou", type=float, default=PASS_IOU)
    args = parser.parse_args()

    truth = json.loads(TRUTH_PATH.read_text(encoding="utf-8"))
    student = load_student(args.student_json)
    failures = 0
    checks = 0

    for doc in truth["documents"]:
        got = student.get(doc["id"])
        print("\n" + doc["id"])
        if got is None:
            print("  MISSING document")
            failures += 1
            checks += 1
            continue
        checks += 1
        if got.get("doc_class") != doc["doc_class"]:
            print("  class: got {0!r}, want {1!r}".format(got.get("doc_class"), doc["doc_class"]))
            failures += 1
        else:
            print("  class: pass")

        summary = got.get("summary") or ""
        for needle in doc["summary_must_include"]:
            checks += 1
            if needle not in summary:
                print("  summary missing {0!r}".format(needle))
                failures += 1
        for banned in doc["summary_must_not_include"]:
            checks += 1
            if banned.lower() in summary.lower():
                print("  summary invented {0!r}".format(banned))
                failures += 1

        by_id = {field["id"]: field for field in got.get("fields") or []}
        for field in doc["fields"]:
            checks += 1
            found = by_id.get(field["id"])
            if found is None:
                print("  {0}: missing".format(field["id"]))
                failures += 1
                continue
            value_ok = (found.get("value") or "").strip() == field["value"]
            box = found.get("value_box")
            score = iou(box, field["value_box"]) if box else 0.0
            box_ok = score >= args.iou
            if value_ok and box_ok:
                print("  {0}: pass  IoU {1:.2f}".format(field["id"], score))
            else:
                failures += 1
                print(
                    "  {0}: fail  value {1!r} (want {2!r})  IoU {3:.2f}".format(
                        field["id"], found.get("value"), field["value"], score
                    )
                )

    print("\n{0} failed out of {1} checks".format(failures, checks))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
