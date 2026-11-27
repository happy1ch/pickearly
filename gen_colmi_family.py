#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""COLMI R12 '가족·선물 구성' 도해 (픽얼리 자체 제작, 상품 사진 아님).
   휴대폰 화면(약 340px)에서도 글자가 읽히도록 세로형으로 그린다."""
import os
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "docs", "assets", "images", "colmi-r12-family.png")

INK = (21, 23, 27)
PAPER = (251, 249, 245)
ACCENT = (226, 80, 43)
SUB = (110, 112, 120)
LINE = (206, 200, 188)
CARD = (255, 255, 255)


def f(sz):
    return ImageFont.truetype(FONT, sz)


def main():
    W, H = 900, 1220
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")

    for x in range(-H, W, 26):
        d.line([(x, H), (x + H, 0)], fill=(21, 23, 27, 7), width=1)

    d.text((56, 46), "COLMI R12 · 가족·선물 구성", font=f(30), fill=ACCENT)
    d.text((54, 92), "링 하나에 폰 하나", font=f(64), fill=INK)
    d.text((56, 182), "폰 한 대에 링 하나씩", font=f(34), fill=SUB)
    d.text((56, 226), "각자 폰에 QRing을 깔고 따로 연결합니다", font=f(34), fill=SUB)
    d.line([(56, 288), (W - 56, 288)], fill=LINE, width=3)

    cols = [
        ("폰 1", "8호", "실버", (198, 200, 205)),
        ("폰 2", "10호", "블랙", (52, 54, 58)),
        ("폰 3", "12호", "골드", (196, 166, 108)),
        ("폰 4", "13호", "실버", (198, 200, 205)),
    ]

    row_h = 196
    y0 = 330
    for idx, (phone, size, color_name, ring_col) in enumerate(cols):
        cy = y0 + idx * row_h

        # 폰
        px0, py0, px1, py1 = 60, cy, 156, cy + 150
        d.rounded_rectangle([px0, py0, px1, py1], radius=16,
                            fill=CARD, outline=INK, width=4)
        d.rounded_rectangle([px0 + 10, py0 + 22, px1 - 10, py1 - 22], radius=7,
                            fill=(238, 240, 243), outline=LINE, width=2)
        d.rounded_rectangle([(px0 + px1) // 2 - 14, py0 + 8, (px0 + px1) // 2 + 14, py0 + 14],
                            radius=3, fill=LINE)

        # 화살표
        ax0, ax1 = 176, 250
        ay = cy + 75
        d.line([(ax0, ay), (ax1, ay)], fill=ACCENT, width=4)
        d.polygon([(ax1 - 12, ay - 10), (ax1 - 12, ay + 10), (ax1 + 2, ay)], fill=ACCENT)
        d.text(((ax0 + ax1) // 2, ay - 26), "1:1", font=f(26), fill=ACCENT, anchor="mm")

        # 링
        cx, r = 320, 52
        d.ellipse([cx - r, cy + 75 - r, cx + r, cy + 75 + r],
                  fill=CARD, outline=ring_col, width=14)
        d.ellipse([cx - r + 17, cy + 75 - r + 17, cx + r - 17, cy + 75 + r - 17],
                  fill=PAPER)
        d.rounded_rectangle([cx - 15, cy + 75 - r + 1, cx + 15, cy + 75 - r + 13],
                            radius=4, fill=INK)

        # 글자
        d.text((408, cy + 34), phone, font=f(30), fill=SUB)
        d.text((408, cy + 74), f"{size} · {color_name}", font=f(40), fill=INK)
        d.text((408, cy + 122), "QRing으로 연결", font=f(28), fill=SUB)

    d.line([(56, 1108), (W - 56, 1108)], fill=LINE, width=3)
    d.text((56, 1126), "링은 폰 없이도 7일치를 저장", font=f(30), fill=INK)
    d.text((56, 1164), "같은 특가로는 1인 3개까지", font=f(30), fill=INK)
    d.text((W - 56, 1166), "도해 · 픽얼리 제작", font=f(26), fill=SUB, anchor="ra")

    img.save(OUT, optimize=True)
    print(OUT, img.size)


if __name__ == "__main__":
    main()
