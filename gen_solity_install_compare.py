#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""솔리티 WP-500A '자가설치 vs 방문설치' 비교 도해 (픽얼리 자체 제작)."""
import os
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf"
ROOT = os.path.dirname(os.path.abspath(__file__))
OUTS = [
    os.path.join(ROOT, "docs", "assets", "images", "solity-wp500a-install-compare.png"),
    os.path.join(ROOT, "theme", "assets", "images", "solity-wp500a-install-compare.png"),
]

INK = (21, 23, 27)
PAPER = (251, 249, 245)
ACCENT = (226, 80, 43)
SUB = (122, 124, 130)
LINE = (206, 200, 188)
CARD = (255, 255, 255)
WARN = (150, 60, 30)
WARN_BG = (247, 233, 226)

_font_cache = {}


def f(sz):
    if sz not in _font_cache:
        _font_cache[sz] = ImageFont.truetype(FONT, sz)
    return _font_cache[sz]


def tw(d, s, sz):
    b = d.textbbox((0, 0), s, font=f(sz))
    return b[2] - b[0]


def text(d, xy, s, sz, fill, limit=None, tag=""):
    w = tw(d, s, sz)
    if limit is not None and xy[0] + w > limit:
        print(f"  ! WIDTH OVERFLOW {tag or s[:20]!r}: {xy[0] + w:.0f} > {limit}")
    d.text(xy, s, font=f(sz), fill=fill)
    return w


def main():
    W, H = 1600, 1000
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")

    # 배경 결
    for x in range(-H, W, 28):
        d.line([(x, H), (x + H, 0)], fill=(21, 23, 27, 6), width=1)

    # 상단 라벨 · 제목
    d.text((96, 84), "SOLITY WP-500A · 설치 방식 선택", font=f(30), fill=ACCENT)
    text(d, (94, 144), "38,420원은 '시간'이 아니라 '책임'의 값", 64, INK, 1504, "title")
    text(d, (96, 236), "같은 제품, 두 가지 선택 — 그 차이는 '누가 책임지는가'입니다", 34, SUB, 1504, "subtitle")
    d.text((W - 96, 92), "쿠팡 상품 페이지 · 2026-11-27 가격 기준", font=f(22), fill=SUB, anchor="ra")

    # ── 카드 두 장 ──────────────────────────────────────────────
    cy0, cy1 = 300, 742
    cards = [
        {
            "x0": 96, "x1": 760,
            "name": "고객직접설치",
            "price": "154,140", "price_fill": INK,
            "note": "정가 194,000원 · 20% 쿠폰 적용가",
            "rows": [
                ("누가 설치하나", "구매자 본인 (드라이버·수평계 필요)"),
                ("걸리는 시간", "본인 손에 따라 다름"),
                ("문제가 생기면", "제품 하자와 설치 책임 구분이 어려움"),
            ],
        },
        {
            "x0": 840, "x1": 1504,
            "name": "방문설치",
            "price": "192,560", "price_fill": ACCENT,
            "note": "고객직접설치가 +38,420원",
            "rows": [
                ("누가 설치하나", "설치 기사 방문 (설정은 본인 몫)"),
                ("걸리는 시간", "20~30분 (구매평 기준)"),
                ("문제가 생기면", "설치 이력이 남음 · 기사 편차는 변수"),
            ],
        },
    ]

    for c in cards:
        x0, x1 = c["x0"], c["x1"]
        d.rounded_rectangle([x0, cy0, x1, cy1], radius=14, fill=CARD, outline=LINE, width=2)
        text(d, (x0 + 40, cy0 + 28), c["name"], 28, SUB, x1 - 40, "card name")
        pw = text(d, (x0 + 38, cy0 + 62), c["price"], 64, c["price_fill"], x1 - 40, "price")
        text(d, (x0 + 40 + pw + 8, cy0 + 92), "원", 28, SUB, x1 - 40, "won")
        text(d, (x0 + 40, cy0 + 146), c["note"], 22, SUB, x1 - 40, "note")
        d.line([(x0 + 40, cy0 + 186), (x1 - 40, cy0 + 186)], fill=LINE, width=1)
        for i, (label, value) in enumerate(c["rows"]):
            ry = cy0 + 190 + i * 78
            text(d, (x0 + 40, ry), label, 21, SUB, x1 - 40, "row label")
            text(d, (x0 + 40, ry + 26), value, 26, INK, x1 - 40, "row value")

    # ── 하단: 어느 집에 어느 쪽인가 ─────────────────────────────
    by0, by1 = 756, 884
    decisions = [
        {
            "x0": 96, "x1": 790,
            "head": "직접설치가 맞는 집",
            "lines": ["드라이버로 손잡이를 바꿔 본 적이 있다", "기존 구멍 지름 6.8cm를 직접 확인했다"],
        },
        {
            "x0": 810, "x1": 1504,
            "head": "방문설치가 맞는 집",
            "lines": ["문이 낡았거나 문틀 규격이 확실하지 않다", "부모님 댁처럼 설정(얼굴 등록)까지 해 드려야 한다"],
        },
    ]
    for b in decisions:
        x0, x1 = b["x0"], b["x1"]
        d.rounded_rectangle([x0, by0, x1, by1], radius=14, fill=WARN_BG)
        text(d, (x0 + 36, by0 + 24), b["head"], 26, ACCENT, x1 - 36, "decide head")
        for i, line in enumerate(b["lines"]):
            text(d, (x0 + 36, by0 + 66 + i * 34), "· " + line, 22, WARN, x1 - 36, "decide line")

    # 브랜드
    d.line([(96, H - 58), (150, H - 58)], fill=ACCENT, width=4)
    d.text((164, H - 74), "PickEarly", font=f(30), fill=INK)
    d.text((316, H - 70), "얼리어답터 연구소", font=f(24), fill=SUB)
    d.text((W - 96, H - 78), "설치 전 규격 확인 — 솔리티 고객센터 1588-3641", font=f(22), fill=SUB, anchor="ra")

    for out in OUTS:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        img.save(out, optimize=True)
        print(out, img.size)


if __name__ == "__main__":
    main()
