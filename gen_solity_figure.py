#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""솔리티 WP-500A '무타공 설치 조건' 도해 (픽얼리 자체 제작)."""
import os
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "docs", "assets", "images", "solity-wp500a-spec.png")

INK = (21, 23, 27)
PAPER = (251, 249, 245)
ACCENT = (226, 80, 43)
SUB = (122, 124, 130)
LINE = (206, 200, 188)
CARD = (255, 255, 255)


def f(sz):
    return ImageFont.truetype(FONT, sz)


def draw_center(d, xy, s, sz, fill, anchor="mm"):
    d.text(xy, s, font=f(sz), fill=fill, anchor=anchor)


def main():
    W, H = 1600, 1000
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")

    # 배경 결
    for x in range(-H, W, 28):
        d.line([(x, H), (x + H, 0)], fill=(21, 23, 27, 6), width=1)

    # 상단 라벨 · 제목
    d.text((96, 84), "SOLITY WP-500A · 무타공 설치 조건", font=f(30), fill=ACCENT)
    d.text((94, 148), "문에 새 구멍은 뚫지 않습니다", font=f(64), fill=INK)
    d.text((96, 236), "대신 '이미 뚫려 있는 구멍'이 표준 규격이어야 합니다", font=f(34), fill=SUB)

    # 좌측: 문 단면 도해
    dx0, dy0, dx1, dy1 = 110, 360, 470, 790
    d.rounded_rectangle([dx0, dy0, dx1, dy1], radius=10, fill=(232, 226, 214), outline=LINE, width=3)
    # 도어락 실외측 / 실내측
    d.rounded_rectangle([dx0 + 26, dy0 + 190, dx0 + 96, dy0 + 330], radius=12, fill=INK)
    d.rounded_rectangle([dx1 - 96, dy0 + 190, dx1 - 26, dy0 + 330], radius=12, fill=INK)
    # 타공 구멍
    cy = dy0 + 260
    d.ellipse([dx0 + 150, cy - 46, dx0 + 290, cy + 46], fill=(255, 255, 255), outline=ACCENT, width=4)
    # 모티스
    d.rectangle([dx0 + 186, cy + 60, dx0 + 254, cy + 132], fill=(196, 198, 204), outline=(140, 142, 148), width=2)

    draw_center(d, (dx0 + 96, dy0 + 120), "실외측", 26, SUB)
    draw_center(d, (dx1 - 60, dy0 + 120), "실내측", 26, SUB)
    d.line([(dx0, dy1 + 34), (dx1, dy1 + 34)], fill=SUB, width=2)
    d.line([(dx0, dy1 + 24), (dx0, dy1 + 44)], fill=SUB, width=2)
    d.line([(dx1, dy1 + 24), (dx1, dy1 + 44)], fill=SUB, width=2)
    draw_center(d, ((dx0 + dx1) / 2, dy1 + 70), "문 두께 40~50mm", 28, INK)

    # 우측: 수치 3개
    cards = [
        ("타공 내경", "68", "mm", "기존 손잡이를 뗀 구멍의 지름"),
        ("모티스 길이", "110", "mm", "문 옆면에 보이는 잠금장치 길이"),
        ("스트라이커 길이", "105", "mm", "문틀 쪽 걸쇠 길이"),
    ]
    x0, y = 620, 362
    cw, ch = 880, 146
    for i, (label, num, unit, note) in enumerate(cards):
        yy = y + i * (ch + 20)
        d.rounded_rectangle([x0, yy, x0 + cw, yy + ch], radius=14, fill=CARD, outline=LINE, width=2)
        d.text((x0 + 40, yy + 34), label, font=f(34), fill=INK)
        d.text((x0 + 40, yy + 84), note, font=f(24), fill=SUB)
        d.text((x0 + cw - 104, yy + ch / 2 + 8), num, font=f(70), fill=ACCENT, anchor="rm")
        d.text((x0 + cw - 90, yy + ch / 2 + 14), unit, font=f(28), fill=SUB, anchor="lm")

    # 하단 주의
    d.rounded_rectangle([620, 852, 1500, 916], radius=10, fill=(247, 233, 226))
    d.text((660, 870), "표준 규격 방화문 기준 — 유리문·샷시문에는 설치할 수 없습니다", font=f(25), fill=(150, 60, 30))

    # 브랜드
    d.line([(96, H - 58), (150, H - 58)], fill=ACCENT, width=4)
    d.text((164, H - 74), "PickEarly", font=f(30), fill=INK)
    d.text((316, H - 70), "얼리어답터 연구소", font=f(24), fill=SUB)
    d.text((W - 96, H - 78), "제조사 사양 · 쿠팡 상품 문의(2026-11-16) 기준", font=f(22), fill=SUB, anchor="ra")

    img.save(OUT, optimize=True)
    print(OUT, img.size)


if __name__ == "__main__":
    main()
