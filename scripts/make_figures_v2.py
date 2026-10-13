#!/usr/bin/env python3
"""Redraw figure1 from results.json. Claim order stays the frozen source order."""
import json
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RESULT = ROOT / "results.json"
SOURCE = "results.json"
OUT = ROOT / "figures" / "figure1.png"
NAVY, GREEN, GRAY = "#1f4e79", "#3a9a5b", "#6b7280"
ORDER = ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]


def use_cjk():
    from matplotlib import font_manager

    listed = subprocess.check_output(["fc-list", "Noto Sans CJK SC", "file"], text=True)
    paths = [line.split(":")[0].strip() for line in listed.splitlines() if line.strip()]
    if not paths:
        raise SystemExit("Noto Sans CJK SC is not installed")
    for path in paths:
        font_manager.fontManager.addfont(path)
    plt.rcParams.update({
        "font.family": "Noto Sans CJK SC",
        "font.weight": "regular",
        "axes.titleweight": "regular",
        "axes.labelweight": "regular",
        "axes.unicode_minus": False,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#333333",
        "text.color": "#222222",
        "axes.labelcolor": "#222222",
        "xtick.color": "#222222",
        "ytick.color": "#222222",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "font.size": 8,
    })


def strip_png_text(path):
    data = Path(path).read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("not a png")
    out = bytearray(data[:8])
    i = 8
    while i + 8 <= len(data):
        length = int.from_bytes(data[i:i + 4], "big")
        ctype = data[i + 4:i + 8]
        end = i + 12 + length
        if ctype not in (b"tEXt", b"iTXt", b"zTXt"):
            out += data[i:end]
        i = end
        if ctype == b"IEND":
            break
    Path(path).write_bytes(out)
    width = int.from_bytes(out[16:20], "big")
    if width != 1600:
        raise SystemExit(f"width {width} != 1600")


def gloss(claim):
    """Short bilingual tag built only from fields stored on the claim."""
    source = claim["source"] or {}
    kind = source.get("input_kind")
    filename = source.get("file") or ""
    trials = (claim.get("facts") or {}).get("trials") or {}
    trial_note = "N 未知 unknown" if trials.get("state") == "缺失" else f"试次 trials: {trials.get('literal')}"
    if kind == "not_read":
        where = "X 原文未读 X original unread"
    elif kind == "rendered_record":
        where = "OpenAI 渲染记录 OpenAI rendered record"
    elif "vals_home" in filename:
        where = "Vals 页面记录 Vals page record"
    elif "science_board" in filename:
        where = "官方榜单 JSON Official board JSON"
    elif "anthropic" in filename or "pdftotext" in (source.get("extraction_path") or ""):
        where = "Anthropic PDF"
    else:
        where = kind or "source"
    return f"{where}；{trial_note}"


def main():
    use_cjk()
    if not RESULT.is_file():
        raise SystemExit(f"missing {SOURCE}")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    labels, values, displays, colors, sizes = [], [], [], [], []
    for sid in ORDER:
        claim = result["claims"][sid]
        labels.append(f"{sid} {claim['system']} {claim['display']}｜{claim['main_label']}\n{gloss(claim)}")
        values.append(float(claim["display"]))
        displays.append(claim["display"] + "%")
        colors.append(GRAY)
        sizes.append(42)
    for system in ("Astra", "Fable"):
        official = result["official"][system]
        labels.append(f"重加总 Recount {system}｜{official['K']}/{official['N']}\n一位展示 Display {official['percentage_one_decimal']}%")
        values.append(float(official["percentage_decimal50"]))
        displays.append(official["percentage_one_decimal"] + "%")
        colors.append(GREEN)
        sizes.append(70)

    fig, ax = plt.subplots(figsize=(8.0, 6.4))
    y = list(range(len(values)))
    ax.scatter(values, y, c=colors, s=sizes, zorder=3)
    for i, (value, display) in enumerate(zip(values, displays)):
        ax.annotate(display, (value, i), xytext=(6, 0), textcoords="offset points", va="center", fontsize=8)
    ax.set_yticks(y, labels, fontsize=7)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("报告百分比 / 公开试次重加总（%）\nReported percentage / recount of public trial labels (%)")
    ax.set_title("七条冻结说法与两次官方重加总\nSeven frozen claims and two official recounts", loc="left", fontsize=11, pad=10)
    ax.grid(axis="x", color="#e5e7eb")
    ax.set_axisbelow(True)
    fig.text(0.01, 0.035, "按冻结来源顺序，不排新榜。未重跑模型。灰点为说法，绿点为重加总。\n"
             "Frozen source order; no new ranking. No model reruns. Gray = claims, green = recounts.",
             fontsize=7, color="#333333")
    fig.text(0.01, 0.008, f"数据来源 Source: {SOURCE}", fontsize=7, color=GRAY)
    fig.subplots_adjust(left=0.42, right=0.97, top=0.88, bottom=0.18)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200)
    plt.close(fig)
    strip_png_text(OUT)
    print("wrote figures/figure1.png")


if __name__ == "__main__":
    main()
