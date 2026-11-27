#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""솔리티 WP-500A '자가설치 vs 방문설치' 비교 도해 (픽얼리 자체 제작).

본문 figure 는 폭 600px 로 표시되므로, 1200px 캔버스(표시 배율 0.5)에
글자를 크게 잡아 화면에서도 읽히도록 만들었다.
"""
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
        print(f"  ! WIDTH OVERFLOW {tag or s[:16]!r}: {xy[0] + w:.0f} > {limit}")
    d.text(xy, s, font=f(sz), fill=fill)
    return w


def card(d, x0, x1, y0, h, c):
    d.rounded_rectangle([x0, y0, x1, y0 + h], radius=16, fill=CARD, outline=LINE, width=2)
    text(d, (x0 + 40, y0 + 26), c["name"], 30, SUB, x1 - 40, "card name")
    pw = text(d, (x0 + 38, y0 + 64), c["price"], 74, c["price_fill"], x1 - 40, "price")
    text(d, (x0 + 40 + pw + 10, y0 + 104), "원", 30, SUB, x1 - 40, "won")
    text(d, (x0 + 40, y0 + 158), c["note"], 24, SUB, x1 - 40, "note")
    d.line([(x0 + 40, y0 + 196), (x1 - 40, y0 + 196)], fill=LINE, width=1)
    for i, (label, value) in enumerate(c["rows"]):
        ry = y0 + 212 + i * 90
        if i:
            d.line([(x0 + 40, ry - 20), (x1 - 40, ry - 20)], fill=(234, 230, 222), width=1)
        text(d, (x0 + 40, ry), label, 24, SUB, x1 - 40, "row label")
        text(d, (x0 + 40, ry + 34), value, 34, INK, x1 - 40, "row value")


def main():
    W, H = 1200, 1700
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")
    L, R = 70, W - 70

    # 배경 결
    for x in range(-H, W, 26):
        d.line([(x, H), (x + H, 0)], fill=(21, 23, 27, 6), width=1)

    # 상단 라벨 · 제목
    d.text((L, 58), "SOLITY WP-500A · 설치 방식 선택", font=f(30), fill=ACCENT)
    text(d, (L - 2, 102), "38,420원은 '시간'이 아니라 '책임'의 값", 56, INK, R, "title")
    text(d, (L, 184), "같은 제품, 두 가지 선택 — 누가 설치하고, 문제가 생기면 누가 책임지는가", 26, SUB, R, "subtitle")

    cw0, cw1 = L, R
    cards = [
        {
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
    CH = 500
    card(d, cw0, cw1, 240, CH, cards[0])
    card(d, cw0, cw1, 760, CH, cards[1])

    # 하단: 어느 집에 어느 쪽인가
    decisions = [
        {
            "head": "직접설치가 맞는 집",
            "lines": [
                "드라이버로 손잡이를 바꿔 본 적이 있고, 기존 구멍 지름 6.8cm를 확인했다",
                "당장 급하지 않고 주말 반나절을 쓸 수 있다",
            ],
        },
        {
            "head": "방문설치가 맞는 집",
            "lines": [
                "현관문이 낡았거나 문틀 깊이·모티스 규격이 확실하지 않다",
                "부모님 댁처럼 설정(얼굴 등록)까지 해 드려야 한다",
            ],
        },
    ]
    for i, b in enumerate(decisions):
        by = 1288 + i * 150
        d.rounded_rectangle([L, by, R, by + 134], radius=16, fill=WARN_BG)
        text(d, (L + 36, by + 20), b["head"], 28, ACCENT, R - 36, "decide head")
        for j, line in enumerate(b["lines"]):
            text(d, (L + 36, by + 62 + j * 34), "· " + line, 24, WARN, R - 36, "decide line")

    # 브랜드
    d.line([(L, H - 62), (L + 54, H - 62)], fill=ACCENT, width=4)
    d.text((L + 68, H - 80), "PickEarly", font=f(30), fill=INK)
    d.text((L + 220, H - 76), "얼리어답터 연구소", font=f(24), fill=SUB)
    d.text((R, H - 82), "쿠팡 상품 페이지 가격·구매평 기준 (2026-11-27)", font=f(22), fill=SUB, anchor="ra")

    for out in OUTS:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        img.save(out, optimize=True)
        print(out, img.size)


if __name__ == "__main__":
    main()
