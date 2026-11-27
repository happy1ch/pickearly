#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""힘펠 휴젠뜨2.5 FHD-P150S1 글의 도해 2장 + OG 카드 + 대표 사진 정리.

모바일에서도 읽히도록 캔버스를 좁게(840px) 잡고 글자를 크게 썼다.
본문 figure 는 폭 600px(모바일 약 350px)로 표시된다.
600px 표시 → 0.71배, 350px 표시 → 0.42배. 본문 24px 는 각각 17px / 10px.
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
ACCENT = (196, 40, 62)
SUB = (116, 118, 124)
LINE = (204, 198, 186)
CARD = (255, 255, 255)
WARN = (146, 56, 28)
WARN_BG = (247, 233, 226)
BLUE = (40, 72, 112)

W = 840
M = 56
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


def para(d, xy, s, sz, fill, maxw, lead=1.42, bold=False, tag=""):
    x, y = xy
    for line in wrap(d, s, sz, maxw, bold):
        text(d, (x, y), line, sz, fill, x + maxw, bold, tag)
        y += int(sz * lead)
    return y


def texture(d, w, h, alpha=7):
    for x in range(-h, w, 26):
        d.line([(x, h), (x + h, 0)], fill=(21, 23, 27, alpha), width=1)


def brand(d, h, note):
    d.line([(M, h - 62), (M + 44, h - 62)], fill=ACCENT, width=4)
    wm = text(d, (M + 54, h - 78), "PickEarly", 26, INK, bold=True)
    text(d, (M + 54 + wm + 14, h - 74), "얼리어답터 연구소", 20, SUB)
    d.text((R, h - 74), note, font=f(18), fill=SUB, anchor="ra")


# ---------------------------------------------------------------- 도해 1
def figure_spec():
    H = 1424
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")
    texture(d, W, H)

    text(d, (M, 48), "힘펠 휴젠뜨2.5 · FHD-P150S1", 24, ACCENT, R, bold=True)
    text(d, (M - 2, 84), "환풍기가 아니라", 44, INK, R + 30, bold=True)
    text(d, (M - 2, 136), "'욕실 기계' 하나입니다", 44, INK, R + 30, bold=True)
    text(d, (M, 200), "환기 · 온풍 · 제습 · 드라이를 한 몸에", 23, SUB, R)

    specs = [
        ("환기", "3단 · 120 CMH", "10/7/6W · 26~38dB"),
        ("온풍", "2단 · 1,200W", "90/70 CMH · PTC 히터"),
        ("제습·건조", "1단 · 600W", "80 CMH · 51dB"),
        ("드라이", "2단 · 1,500W", "190/150 CMH · 61dB"),
    ]
    y0 = 246
    cw = (R - M - 18) // 2
    ch = 128
    for i, (k, v, note) in enumerate(specs):
        cx = M + (i % 2) * (cw + 18)
        cy = y0 + (i // 2) * (ch + 16)
        d.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=12, fill=CARD, outline=LINE, width=2)
        text(d, (cx + 22, cy + 16), k, 21, SUB, cx + cw - 22)
        text(d, (cx + 20, cy + 44), v, 32, INK, cx + cw - 18, bold=True, tag=k)
        text(d, (cx + 22, cy + 92), note, 23, SUB, cx + cw - 22, tag=k + " note")

    # 라인업
    ty = y0 + 2 * (ch + 16) + 22
    text(d, (M, ty), "같은 '휴젠뜨'라도 네 가지입니다", 30, INK, R, bold=True)
    text(d, (M, ty + 44), "쿠팡 표시가 · 2026년 11월 27일 밤", 20, SUB, R)

    hy = ty + 84
    cols = [("모델", M), ("가격", M + 300), ("타공", M + 470), ("환기", M + 620)]
    for label, cx in cols:
        text(d, (cx, hy), label, 20, SUB, R)
    d.line([(M, hy + 30), (R, hy + 30)], fill=LINE, width=2)

    rows = [
        ("휴젠뜨2.5", "FHD-P150S1", "376,000", "405×265", "3단", "온도센서만 · 이 글"),
        ("노바", "FHD2-C150P", "429,000", "400×250", "4단", "습도 표시 · 음성안내"),
        ("팔레트", "FHD2-C150P", "569,000", "405×265", "4단", "5색 그릴 · 블루투스"),
        ("휴젠뜨3", "FHD3-C150P", "770,000", "405×265", "4단", "무드 LED · 블루투스"),
    ]
    ry = hy + 42
    for n, (name, model, price, hole, fan, feat) in enumerate(rows):
        bold = n == 0
        text(d, (cols[0][1], ry), name, 26, INK if bold else (58, 60, 66), R, bold=bold, tag=name)
        text(d, (cols[0][1], ry + 30), model, 21, SUB, M + 296, tag=model)
        text(d, (cols[1][1], ry), price, 24, ACCENT if bold else (58, 60, 66), R, bold=bold)
        text(d, (cols[2][1], ry + 2), hole, 22, (58, 60, 66), R)
        text(d, (cols[3][1], ry + 2), fan, 22, (58, 60, 66), R)
        text(d, (M, ry + 52), feat, 22, SUB, R, tag=feat)
        ry += 92
        if n < len(rows) - 1:
            d.line([(M, ry - 6), (R, ry - 6)], fill=(232, 227, 217), width=1)
    text(d, (M, ry + 2), "휴젠뜨3는 방문설치 840,000원 · 노바F는 노바에 블루투스를 더한 모델", 21, SUB, R, tag="price-note")

    # 본체 높이
    wy = ry + 52
    d.rounded_rectangle([M, wy, R, wy + 240], radius=12, fill=WARN_BG)
    text(d, (M + 24, wy + 20), "본체 높이, 149mm인가 180mm인가", 27, ACCENT, R - 24, bold=True)
    para(d, (M + 24, wy + 62),
         "공식 표기는 477×313×149mm이고 천장 안쪽은 150mm 이상이면 된다고 안내합니다. "
         "가격비교·딜러 표에는 180mm로 적힌 곳도 있는데, 사진 오른쪽 전동댐퍼·덕트 접속구까지 포함한 높이로 보입니다. "
         "빠듯한 집은 180mm로 재십시오.",
         24, WARN, R - M - 48, 1.38, tag="height")

    brand(d, H, "힘펠 공식몰 · 딜러 성능표")

    out = os.path.join(IMG, "himpel-huezentte-spec.png")
    img.save(out, optimize=True)
    print(out, img.size)


# ---------------------------------------------------------------- 도해 2
def figure_install():
    H = 1452
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")
    texture(d, W, H)

    text(d, (M, 48), "힘펠 휴젠뜨 · 설치 조건", 24, ACCENT, R, bold=True)
    text(d, (M - 2, 84), "사기 전에 천장부터", 44, INK, R + 30, bold=True)
    text(d, (M - 2, 136), "재십시오", 44, INK, R + 30, bold=True)
    text(d, (M, 200), "'교체'가 아니라 '타공 확장'이 붙는 교체입니다", 23, SUB, R)

    # 도해 카드
    dy = 246
    d.rounded_rectangle([M, dy, R, dy + 452], radius=12, fill=CARD, outline=LINE, width=2)
    text(d, (M + 24, dy + 18), "천장에서 보는 치수 (mm)", 25, INK, R - 24, bold=True)

    # 축척 1px = 1.26mm → 본체 477×313 = 379×248, 타공 405×265 = 321×210
    sc = 379 / 477
    sw, sh = 379, int(313 * sc)
    hw, hh = int(405 * sc), int(265 * sc)
    cx0, cy0 = M + 40, dy + 66
    hx = cx0 + (sw - hw) // 2
    hyy = cy0 + (sh - hh) // 2
    d.rounded_rectangle([cx0, cy0, cx0 + sw, cy0 + sh], radius=8, fill=(232, 235, 239), outline=(168, 174, 182), width=2)
    d.rectangle([hx, hyy, hx + hw, hyy + hh], fill=(255, 255, 255), outline=ACCENT, width=3)
    for x in range(hx + 7, hx + hw, 15):
        d.line([(x, hyy + 4), (x, hyy + hh - 4)], fill=(240, 212, 216), width=1)
    d.text((hx + hw // 2, hyy + hh // 2 - 40), "타공", font=f(25, True), fill=ACCENT, anchor="ma")
    d.text((hx + hw // 2, hyy + hh // 2 - 6), "405 × 265", font=f(30, True), fill=ACCENT, anchor="ma")
    d.text((hx + hw // 2, hyy + hh // 2 + 32), "±5mm", font=f(21), fill=(190, 90, 100), anchor="ma")
    d.line([(hx, hyy + hh + 22), (hx + hw, hyy + hh + 22)], fill=SUB, width=2)
    for xx in (hx, hx + hw):
        d.line([(xx, hyy + hh + 15), (xx, hyy + hh + 29)], fill=SUB, width=2)
    text(d, (hx + 4, hyy + hh + 28), "405", 20, SUB)
    d.line([(cx0 + sw + 20, hyy), (cx0 + sw + 20, hyy + hh)], fill=SUB, width=2)
    text(d, (cx0 + sw + 30, hyy + hh // 2 - 12), "265", 20, SUB)

    # 오른쪽 설명
    ex = cx0 + sw + 84
    notes = [("Ø100 덕트", "배기관 지름"), ("안쪽 150mm", "댐퍼까지 180mm"), ("220V 전원", "기존 전선 사용"), ("4.3kg", "보강대 2개 동봉")]
    ny = cy0 + 6
    for head, body in notes:
        text(d, (ex, ny), head, 22, BLUE, R - 10, bold=True, tag=head)
        text(d, (ex, ny + 30), body, 19, SUB, R - 10, tag=head + "b")
        ny += 62

    text(d, (M + 24, dy + 372), "본체(그릴) 477×313 — 타공보다 가로 36mm, 세로 24mm 넓게 덮습니다", 20, SUB, R - 24, tag="grille")

    # 체크리스트
    cy = dy + 472
    d.rounded_rectangle([M, cy, R, cy + 300], radius=12, fill=WARN_BG)
    text(d, (M + 24, cy + 20), "기존 환풍기 자리에 그대로 들어갈까?", 27, ACCENT, R - 24, bold=True)
    yy = cy + 62
    for ln in [
        "기존 타공이 405×265보다 작으면 확장 공사가 필요합니다. 힘펠 일반형(제로크H)은 225×225입니다.",
        "타공이 같아도 덕트 위치·전원선·천장 안쪽 장애물 때문에 설치 불가 판정이 날 수 있습니다.",
        "신축 아파트 화장실 두 곳 모두 '불가' 판정을 받았다는 구매 후기가 힘펠몰에 있습니다.",
    ]:
        yy = para(d, (M + 24, yy), "· " + ln, 21, WARN, R - M - 48, 1.38)
        yy += 10

    # 옵션 비교
    oy = cy + 322
    d.rounded_rectangle([M, oy, R, oy + 336], radius=12, fill=CARD, outline=LINE, width=2)
    text(d, (M + 24, oy + 18), "단품인가, 설치 포함인가 — 2만 원 차이", 26, INK, R - 24, bold=True)
    c1, c2 = M + 220, M + 470
    text(d, (c1, oy + 60), "직접설치", 21, SUB, R, bold=True)
    text(d, (c2, oy + 60), "방문설치", 21, SUB, R, bold=True)
    rows = [
        ("쿠팡 가격", "376,000원", "396,000원"),
        ("기본 설치", "없음", "포함 표기"),
        ("타공 확장", "직접", "포함(공식몰)"),
        ("현장 추가비", "—", "별도"),
        ("어울리는 분", "공구 있는 분", "처음 교체"),
    ]
    ry = oy + 96
    for k, a, b in rows:
        text(d, (M + 24, ry + 2), k, 19, SUB, c1 - 10)
        text(d, (c1, ry), a, 21, INK, c2 - 10, bold=(k == "쿠팡 가격"), tag=k + "a")
        text(d, (c2, ry), b, 21, INK, R - 20, bold=(k == "쿠팡 가격"), tag=k + "b")
        ry += 40
    text(d, (M + 24, oy + 300), "설치 불가로 철수하면 출장비 22,000원 + 반품 배송비 12,000원(공식몰 안내)", 18, SUB, R - 24)

    brand(d, H, "힘펠 공식몰 FAQ · 쿠팡")

    out = os.path.join(IMG, "himpel-huezentte-install.png")
    img.save(out, optimize=True)
    print(out, img.size)


# ---------------------------------------------------------------- 대표 사진
def product_photo():
    src = os.path.join(ROOT, "..", "img", "p150s1-1000x1000ex.jpg")
    im = Image.open(src).convert("RGB")
    out = os.path.join(IMG, "himpel-huezentte-2-5.jpg")
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

    text(d, (64, 62), "쿠팡 · AI 스마트 가전", 23, ACCENT, bold=True)
    text(d, (62, 112), "타공 405×265mm,", 60, PAPER, bold=True)
    text(d, (62, 186), "37만 원대 욕실 환풍기", 60, PAPER, bold=True)
    text(d, (64, 290), "힘펠 휴젠뜨2.5 FHD-P150S1 · ₩376,000 · 후기 357건", 24, SUB)

    chips = ["환기·온풍·제습·드라이", "BLDC · 전동댐퍼 6단계", "본체 477×313×149"]
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

    out = os.path.join(OG, "og-himpel-huezentte.png")
    img.save(out, optimize=True)
    print(out, img.size)


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    os.makedirs(OG, exist_ok=True)
    product_photo()
    figure_spec()
    figure_install()
    og_card()
