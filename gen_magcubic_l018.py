#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Magcubic L018 글의 자체 제작 도해 2장 + OG 카드 + 대표 사진 정리.

본문 figure 는 폭 600px 로 표시되므로 1080px 캔버스에 글자를 크게 잡았다
(표시 배율 0.55 → 본문 28px 는 화면에서 약 15px).
"""
import os
from PIL import Image, ImageDraw, ImageFont

REG = "/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf"
BOLD = "/workspace/handoffs/📖-복음적-예배-성서공회-저작권-표기-반영-재빌드/work/fonts/NotoSansCJKkr-Bold.otf"
ROOT = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(ROOT, "docs", "assets", "images")
OG = os.path.join(ROOT, "docs", "assets", "og")

INK = (21, 23, 27)
PAPER = (251, 249, 245)
ACCENT = (226, 80, 43)
SUB = (122, 124, 130)
LINE = (206, 200, 188)
CARD = (255, 255, 255)
WARN = (150, 60, 30)
WARN_BG = (247, 233, 226)
TINT = (241, 237, 229)

W = 1080
M = 72          # 좌우 여백
R = W - M

_fc = {}


def f(sz, bold=False):
    key = (sz, bold)
    if key not in _fc:
        _fc[key] = ImageFont.truetype(BOLD if bold else REG, sz)
    return _fc[key]


def tw(d, s, sz, bold=False):
    b = d.textbbox((0, 0), s, font=f(sz, bold))
    return b[2] - b[0]


def text(d, xy, s, sz, fill, limit=None, bold=False, tag=""):
    w = tw(d, s, sz, bold)
    if limit is not None and xy[0] + w > limit:
        print(f"  ! OVERFLOW {tag or s[:18]!r}: {xy[0] + w:.0f} > {limit}")
    d.text(xy, s, font=f(sz, bold), fill=fill)
    return w


def wrap(d, s, sz, maxw, bold=False):
    """공백 기준 줄바꿈 (한국어 문장)."""
    out, cur = [], ""
    for token in s.split(" "):
        cand = (cur + " " + token).strip()
        if tw(d, cand, sz, bold) <= maxw or not cur:
            cur = cand
        else:
            out.append(cur)
            cur = token
    if cur:
        out.append(cur)
    return out


def para(d, xy, s, sz, fill, maxw, lead=1.45, bold=False, tag=""):
    x, y = xy
    for line in wrap(d, s, sz, maxw, bold):
        text(d, (x, y), line, sz, fill, x + maxw, bold, tag)
        y += int(sz * lead)
    return y


def texture(d, w, h, alpha=7):
    for x in range(-h, w, 26):
        d.line([(x, h), (x + h, 0)], fill=(21, 23, 27, alpha), width=1)


def brand(d, h, note):
    d.line([(M, h - 66), (M + 52, h - 66)], fill=ACCENT, width=4)
    wm = text(d, (M + 64, h - 84), "PickEarly", 28, INK, bold=True)
    text(d, (M + 64 + wm + 18, h - 80), "얼리어답터 연구소", 22, SUB)
    d.text((R, h - 80), note, font=f(20), fill=SUB, anchor="ra")


# ---------------------------------------------------------------- 도해 1
def figure_spec():
    H = 1470
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")
    texture(d, W, H)

    text(d, (M, 56), "MAGCUBIC L018 · 사양과 설치 거리", 27, ACCENT, R, bold=True)
    text(d, (M - 2, 96), "화면 크기는 '거리'로 정해집니다", 52, INK, R + 40, bold=True)
    text(d, (M, 168), "투사비 1.2:1 — 100인치(16:9)를 채우려면 벽에서 2.65m", 25, SUB, R)

    # 스펙 카드 2열 x 3행
    specs = [
        ("해상도", "1920×1080", "네이티브 FHD · 8K는 디코딩"),
        ("밝기", "650 ANSI", "규격란 '6000루멘'과 다른 값"),
        ("시스템", "Android 14", "Allwinner H726 · 구글 플레이"),
        ("자동 보정", "초점·키스톤", "장애물 회피 · 2초(제조사)"),
        ("크기·무게", "224×151×173mm", "1.3kg(제조사) / 1.7kg(알리)"),
        ("전원", "어댑터 80W", "배터리 없음 · 전원선 필수"),
    ]
    y0 = 232
    cw = (R - M - 24) // 2
    ch = 150
    for i, (k, v, note) in enumerate(specs):
        cx = M + (i % 2) * (cw + 24)
        cy = y0 + (i // 2) * (ch + 18)
        d.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=14, fill=CARD, outline=LINE, width=2)
        text(d, (cx + 26, cy + 20), k, 22, SUB, cx + cw - 26)
        text(d, (cx + 24, cy + 52), v, 36, INK, cx + cw - 20, bold=True, tag=k)
        text(d, (cx + 26, cy + 106), note, 19, SUB, cx + cw - 26, tag=k + " note")

    # 거리 표
    ty = y0 + 3 * (ch + 18) + 26
    d.rounded_rectangle([M, ty, R, ty + 400], radius=16, fill=CARD, outline=LINE, width=2)
    text(d, (M + 30, ty + 24), "16:9 화면을 채우는 거리", 28, INK, R - 30, bold=True)
    text(d, (M + 30, ty + 64), "화면 폭 × 1.2 = 투사 거리 (제조사 표기 투사비 기준)", 20, SUB, R - 30)

    cols = [("화면", M + 30), ("화면 폭", M + 300), ("필요한 거리", M + 560)]
    hy = ty + 106
    for label, cx in cols:
        text(d, (cx, hy), label, 21, SUB, R - 20)
    d.line([(M + 24, hy + 34), (R - 24, hy + 34)], fill=LINE, width=2)
    rows = [("80인치", "177 cm", "2.1 m"), ("100인치", "221 cm", "2.7 m"), ("120인치", "266 cm", "3.2 m")]
    for n, (a, b, c) in enumerate(rows):
        ry = hy + 44 + n * 74
        text(d, (cols[0][1], ry), a, 32, INK, R - 20, bold=True)
        text(d, (cols[1][1], ry + 2), b, 28, SUB, R - 20)
        text(d, (cols[2][1], ry + 2), c, 32, ACCENT, R - 20, bold=True)
        if n < 2:
            d.line([(M + 24, ry + 60), (R - 24, ry + 60)], fill=(232, 227, 217), width=1)
    text(d, (M + 30, ty + 352), "50~100% 디지털 줌으로 화면만 줄일 수 있습니다(거리는 그대로).", 20, SUB, R - 30)

    # 주의 상자
    wy = ty + 424
    lines = [
        "판매처는 40~300인치, 제조사 사양표는 40~120인치, 제조사 소개문은 80~150인치로 적혀 있습니다.",
        "실사용은 100인치 이하가 안전합니다. 120인치를 넘기면 밝기가 눈에 띄게 떨어집니다.",
        "포트는 HDMI · USB · 3.5mm 이어폰 단자, 무선은 WiFi 6 · 블루투스 5.4 입니다.",
    ]
    d.rounded_rectangle([M, wy, R, wy + 190], radius=16, fill=WARN_BG)
    text(d, (M + 30, wy + 22), "표기가 서로 다른 숫자", 26, ACCENT, R - 30, bold=True)
    yy = wy + 64
    for ln in lines:
        yy = para(d, (M + 30, yy), "· " + ln, 21, WARN, R - 60, 1.5)

    brand(d, H, "판매 페이지 · 제조사 사양 대조 (2026-11-27)")

    out = os.path.join(IMG, "magcubic-l018-spec.png")
    img.save(out, optimize=True)
    print(out, img.size)


# ---------------------------------------------------------------- 도해 2
def figure_usage():
    H = 1420
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")
    texture(d, W, H)

    text(d, (M, 56), "MAGCUBIC L018 · 쓰는 자리와 한계", 27, ACCENT, R, bold=True)
    text(d, (M - 2, 96), "천장에 눕혀 쏘는 재미,", 50, INK, R + 40, bold=True)
    text(d, (M - 2, 156), "낮에는 못 쓰는 밝기", 50, INK, R + 40, bold=True)

    # 이렇게 씁니다
    y = 250
    text(d, (M, y), "이렇게 씁니다", 32, INK, R, bold=True)
    y += 52
    uses = [
        ("01", "침실 벽 정면", "침대 맞은편 2.7m면 100인치. 벽지에 구멍 낼 일 없이 그대로 쏩니다."),
        ("02", "천장 투사", "본체를 위로 젖혀 누워서 봅니다. 제조사 사양은 180° 가동이라고 적습니다."),
        ("03", "캠핑·야외", "해 진 뒤에만. 배터리가 없어 80W 전원(보조배터리·인버터)이 필요합니다."),
    ]
    for num, head, body in uses:
        d.rounded_rectangle([M, y, R, y + 132], radius=14, fill=CARD, outline=LINE, width=2)
        text(d, (M + 26, y + 30), num, 30, ACCENT, M + 90, bold=True)
        text(d, (M + 92, y + 26), head, 30, INK, R - 20, bold=True)
        para(d, (M + 92, y + 74), body, 22, SUB, R - M - 120, 1.4)
        y += 148

    # 여기서 걸립니다
    y += 6
    d.rounded_rectangle([M, y, R, y + 560], radius=16, fill=WARN_BG)
    text(d, (M + 30, y + 24), "사기 전에 걸리는 지점", 30, ACCENT, R - 30, bold=True)
    traps = [
        ("플러그 기본값이 US", "한국 220V 콘센트는 EU(C/F)형입니다. 주문할 때 EU를 골라야 어댑터가 필요 없습니다."),
        ("KC 인증 표기가 없습니다", "FCC ID 2BFIZ-L018, CE 표기만 확인됩니다. 국내 전파인증 표기는 보이지 않습니다."),
        ("고휘도 모드 팬 소음", "알리 3점 후기 2건, 제조사몰 후기가 같은 말을 합니다. 조용한 방엔 부담입니다."),
        ("밝은 낮에는 못 봅니다", "'낮에 쓰기 힘들다'는 후기가 있습니다. 커튼 치고 저녁에 보는 기기입니다."),
        ("내장 안드로이드가 느립니다", "후기 다수가 HDMI 셋톱(구글 TV)을 붙여 쓰라고 권합니다."),
        ("스피커는 3W 하나", "영화용으로는 부족합니다. 블루투스 스피커나 유선 스피커를 함께 보세요."),
    ]
    yy = y + 74
    for i, (head, body) in enumerate(traps):
        text(d, (M + 30, yy), "· " + head, 24, WARN, R - 30, bold=True, tag=head)
        yy = para(d, (M + 44, yy + 32), body, 20, (120, 52, 30), R - M - 90, 1.38)
        yy += 8
        if i < len(traps) - 1:
            d.line([(M + 30, yy - 2), (R - 30, yy - 2)], fill=(226, 208, 196), width=1)
            yy += 8

    brand(d, H, "알리 · 제조사몰 후기와 판매 페이지 기준 (2026-11-27)")

    out = os.path.join(IMG, "magcubic-l018-usage.png")
    img.save(out, optimize=True)
    print(out, img.size)


# ---------------------------------------------------------------- 대표 사진
def product_photo():
    src = "/workspace/downloads/pickearly-candidates/2026-11-27/ali3_magcubic_l018.jpg"
    im = Image.open(src).convert("RGB")
    out = os.path.join(IMG, "magcubic-l018.jpg")
    im.save(out, quality=90, optimize=True)
    print(out, im.size)


# ---------------------------------------------------------------- OG
def og_card():
    w, h = 1200, 630
    img = Image.new("RGB", (w, h), INK)
    d = ImageDraw.Draw(img, "RGBA")
    for x in range(-h, w, 22):
        d.line([(x, h), (x + h, 0)], fill=(255, 255, 255, 10), width=1)
    d.rectangle([w - 300, 0, w, 8], fill=ACCENT)

    text(d, (64, 62), "알리 · AI 아이디어 기기", 23, ACCENT, bold=True)
    text(d, (62, 112), "8만 8천 원대 650ANSI,", 60, PAPER, bold=True)
    text(d, (62, 186), "'360°'인지 '180°'인지", 60, PAPER, bold=True)
    text(d, (64, 290), "Magcubic L018 · ₩88,768 · 네이티브 1080P · 자동초점/자동키스톤", 24, SUB)

    # 오른쪽: 스펙 칩 (오른쪽 정렬)
    chips = ["650 ANSI", "네이티브 1080P", "1.2:1 · 100인치 2.7m"]
    cy = 236
    for c in chips:
        wd = tw(d, c, 24)
        x1 = w - 64
        x0 = x1 - wd - 48
        d.rounded_rectangle([x0, cy, x1, cy + 56], radius=28, outline=(255, 255, 255, 55), width=2)
        d.text((x0 + 24, cy + 14), c, font=f(24), fill=(228, 224, 216))
        cy += 72

    d.line([(64, h - 128), (116, h - 128)], fill=ACCENT, width=4)
    text(d, (130, h - 146), "PickEarly", 30, PAPER, bold=True)
    text(d, (282, h - 142), "얼리어답터 연구소", 24, SUB)
    d.text((w - 64, h - 140), "pickearly.com", font=f(22), fill=SUB, anchor="ra")

    out = os.path.join(OG, "og-magcubic-l018.png")
    img.save(out, optimize=True)
    print(out, img.size)


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    os.makedirs(OG, exist_ok=True)
    product_photo()
    figure_spec()
    figure_usage()
    og_card()
