#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PickEarly OG / 썸네일 이미지 생성 (PIL)."""

import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_OG = os.path.join(ROOT, "docs", "assets", "og")
OUT_IMG = os.path.join(ROOT, "docs", "assets", "images")
FONT = "/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf"

INK = (21, 23, 27)
PAPER = (251, 249, 245)
ACCENT = (226, 80, 43)
SUB = (150, 152, 158)


def f(size):
    return ImageFont.truetype(FONT, size)


def text(draw, xy, s, size, fill, bold=0, anchor="la", spacing=None):
    draw.text(xy, s, font=f(size), fill=fill, anchor=anchor,
              stroke_width=bold, stroke_fill=fill)


def multiline(draw, xy, lines, size, fill, bold=0, leading=1.18):
    x, y = xy
    step = int(size * leading)
    for i, ln in enumerate(lines):
        text(draw, (x, y + i * step), ln, size, fill, bold=bold)
    return y + step * len(lines)


def mark(draw, x, y, scale=1.0, color=ACCENT):
    """PickEarly 로고 마크 (해 돋는 선 + 점)"""
    w = int(46 * scale)
    lw = max(2, int(4 * scale))
    draw.line([(x, y + w * 0.62), (x + w, y + w * 0.62)], fill=color, width=lw)
    draw.line([(x + w / 2, y + w * 0.62), (x + w / 2, y + w * 0.24)], fill=color, width=lw)
    draw.arc([(x + w * 0.13, y + w * 0.02), (x + w * 0.87, y + w * 0.62)], 180, 360, fill=color, width=lw)
    r = w * 0.07
    draw.ellipse([(x + w / 2 - r, y + w * 0.24 - r - w * 0.1), (x + w / 2 + r, y + w * 0.24 + r - w * 0.1)], fill=color)


def brand_block(draw, W, H, dark=False, size=30):
    pad = 64
    y = H - pad - size
    mx = pad + 4
    mark(draw, mx, y + 3, scale=size / 34.0, color=ACCENT)
    col = PAPER if dark else INK
    tx = mx + int(size * 1.25) + 20
    text(draw, (tx, y), "PickEarly", size, col, bold=1)
    text(draw, (tx + 2, y + size + 5), "얼리어답터 연구소", int(size * 0.5), SUB if dark else (120, 122, 128))
    return tx


def grain_like(draw, W, H):
    """아주 옅은 대각선 패턴 (밋밋함 방지)"""
    for x in range(-H, W, 26):
        draw.line([(x, H), (x + H, 0)], fill=(255, 255, 255, 6), width=1)


def og_card(path, kicker, lines, footnote, dark=True, brand_tail="pickearly.com"):
    W, H = 1200, 630
    bg = INK if dark else PAPER
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img, "RGBA")

    # background texture
    for x in range(-H, W, 22):
        d.line([(x, H), (x + H, 0)], fill=((255, 255, 255, 10) if dark else (21, 23, 27, 8)), width=1)
    # accent block top-right
    d.rectangle([W - 300, 0, W, 8], fill=ACCENT)

    fg = PAPER if dark else INK
    text(d, (64, 62), kicker, 22, ACCENT, bold=1)
    y = 118
    y = multiline(d, (64, y), lines, 62 if dark else 60, fg, bold=2, leading=1.16)
    text(d, (64, y + 26), footnote, 25, SUB if dark else (110, 112, 118))

    brand_block(d, W, H, dark=dark, size=30)
    text(d, (W - 64, H - 64 - 12), brand_tail, 22, SUB if dark else (140, 142, 148), anchor="ra")

    img.save(path, optimize=True)
    print(path, img.size)


def thumb_bespoke(path):
    W, H = 1600, 900
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img, "RGBA")
    for x in range(-H, W, 24):
        d.line([(x, H), (x + H, 0)], fill=(255, 255, 255, 9), width=1)

    text(d, (96, 92), "ROBOT VACUUM · 자동 급배수", 26, ACCENT, bold=1)
    multiline(d, (92, 168), ["물통을 버리는", "로봇청소기"], 104, PAPER, bold=2, leading=1.14)

    # model chips
    y = 500
    x = 96
    for name in ["VR70 일반형", "VR80 플러스", "VR90 울트라"]:
        w = int(d.textlength(name, font=f(28))) + 44
        d.rounded_rectangle([x, y, x + w, y + 58], radius=29, outline=(255, 255, 255, 60), width=2)
        text(d, (x + 22, y + 14), name, 28, (235, 232, 224))
        x += w + 14

    text(d, (96, 596), "1,487,700원  ·  1,590,000원  ·  1,590,000원", 30, SUB)
    text(d, (96, 650), "직배수는 성능이 아니라 '설치'의 문제 — 리폼비 포함 여부까지", 26, (205, 201, 193))

    # right: schematic station
    cx, cy = 1230, 300
    d.rounded_rectangle([cx - 170, cy - 120, cx + 170, cy + 210], radius=26, outline=(255, 255, 255, 46), width=2)
    d.rounded_rectangle([cx - 120, cy + 40, cx + 120, cy + 150], radius=16, fill=(255, 255, 255, 14))
    for i in range(6):
        d.line([(cx - 96 + i * 40, cy - 70), (cx - 96 + i * 40, cy + 10)], fill=(255, 255, 255, 28), width=3)
    d.line([(cx + 170, cy + 96), (cx + 260, cy + 96)], fill=ACCENT, width=5)
    d.line([(cx - 260, cy - 40), (cx - 170, cy - 40)], fill=ACCENT, width=5)
    text(d, (cx + 176, cy + 60), "배수", 22, ACCENT)
    text(d, (cx - 320, cy - 72), "급수", 22, ACCENT)

    brand_block(d, W, H, dark=True, size=32)
    img.save(path, optimize=True)
    print(path, img.size)


def main():
    os.makedirs(OUT_OG, exist_ok=True)
    os.makedirs(OUT_IMG, exist_ok=True)

    og_card(
        os.path.join(OUT_OG, "og-home.png"),
        "PICKEARLY · 얼리어답터 연구소",
        ["남보다 반 발 먼저 사는", "사람의 연구소"],
        "쿠팡 · 알리 — 사기 전에 알아야 할 것부터 정리합니다",
        dark=True,
        brand_tail="2026 · ISSUE 01",
    )
    og_card(
        os.path.join(OUT_OG, "og-bespoke-ai-steam.png"),
        "쿠팡 · AI 스마트 가전",
        ["물통을 버리는", "로봇청소기의 조건"],
        "비스포크 AI 스팀 자동 급배수 · VR70 / VR80 / VR90 비교",
        dark=True,
    )
    og_card(
        os.path.join(OUT_OG, "og-ai-voice-recorder.png"),
        "알리 · AI 아이디어 기기",
        ["명함보다 얇은", "AI 녹음기 2종"],
        "BOYA Notra Neo ₩94,800 · NEWYES Ailog ₩56,700",
        dark=False,
    )
    thumb_bespoke(os.path.join(OUT_IMG, "thumb-bespoke-ai-steam.png"))


if __name__ == "__main__":
    main()
