#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""벨킨 부스트업 프로 200W 4포트 GaN 충전기(WCH015krWH) 글의 도해 2장 + 썸네일 + OG 카드.

도해는 모바일에서도 읽히도록 캔버스를 좁게(840px) 잡고 글자를 크게 쓴다.
본문 figure 는 폭 600px(모바일 약 350px)로 표시된다.
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
GREEN = (32, 92, 70)

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


def charger(d, x, y, w, h, ports, labels, note=None, dark=False):
    """충전기 본체 + 4포트 그림. ports: [(power, color), ...] 4개"""
    body = (44, 47, 54) if dark else (238, 232, 222)
    edge = (70, 74, 82) if dark else (206, 199, 187)
    d.rounded_rectangle([x, y, x + w, y + h], radius=18, fill=body, outline=edge, width=2)
    d.text((x + w * 0.82, y + h * 0.34), "belkin", font=f(int(h * 0.062), True),
           fill=(120, 122, 128) if dark else (176, 170, 159), anchor="mm")
    d.text((x + w * 0.82, y + h * 0.52), "200W", font=f(int(h * 0.072), True),
           fill=(140, 142, 148) if dark else (188, 181, 169), anchor="mm")
    pw = (w * 0.64) / 4
    for i, (power, color) in enumerate(ports):
        px = x + w * 0.04 + i * pw
        d.rounded_rectangle([px + 3, y + h * 0.36, px + pw - 9, y + h * 0.64], radius=6,
                            fill=(30, 32, 37) if dark else (255, 255, 255),
                            outline=color, width=3)
        d.text((px + (pw - 3) / 2, y + h * 0.50), labels[i], font=f(int(h * 0.058), True),
               fill=color, anchor="mm")
        d.text((px + (pw - 3) / 2, y + h * 0.75), power, font=f(int(h * 0.072), True),
               fill=(240, 236, 228) if dark else INK, anchor="mm")


# ---------------------------------------------------------------- 도해 1
def figure_split():
    H = 1220
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")
    texture(d, W, H)

    text(d, (M, 48), "벨킨 부스트업 프로 · WCH015krWH", 24, ACCENT, R, bold=True)
    text(d, (M - 2, 84), "‘200W’는 합계이고,", 44, INK, R + 30, bold=True)
    text(d, (M - 2, 136), "한 포트는 140W입니다", 44, INK, R + 30, bold=True)
    text(d, (M, 200), "4포트를 다 꽂으면 C1·C2 70W, C3·C4 30W로 나뉩니다", 22, SUB, R)

    # 본체 그림
    cy = 240
    d.rounded_rectangle([M, cy, R, cy + 238], radius=14, fill=CARD, outline=LINE, width=2)
    charger(d, M + 26, cy + 24, R - M - 52, 142, [("140W", ACCENT), ("140W", ACCENT), ("60W", BLUE), ("60W", BLUE)],
            ["C1", "C2", "C3", "C4"])
    text(d, (M + 28, cy + 180), "한 개만 꽂을 때 — C1·C2는 140W, C3·C4는 60W", 22, INK, R - 28, bold=True)
    text(d, (M + 28, cy + 212), "벨킨 공식 사양표(FAQ) 기준", 17, SUB, R - 28)

    # 4포트 동시 사용 막대
    by = cy + 260
    d.rounded_rectangle([M, by, R, by + 332], radius=14, fill=CARD, outline=LINE, width=2)
    text(d, (M + 26, by + 20), "네 개를 다 꽂으면 — 합계 200W", 27, INK, R - 26, bold=True)

    base = by + 252
    maxh = 110
    bars = [("C1", 70, ACCENT), ("C2", 70, ACCENT), ("C3", 30, BLUE), ("C4", 30, BLUE)]
    bw = 108
    gap = 26
    x0 = M + 44
    for i, (lab, p, col) in enumerate(bars):
        bx = x0 + i * (bw + gap)
        bh = int(maxh * p / 70)
        d.rounded_rectangle([bx, base - bh, bx + bw, base], radius=6, fill=col)
        d.text((bx + bw / 2, base - bh - 34), f"{p}W", font=f(26, True), fill=INK, anchor="ma")
        d.text((bx + bw / 2, base + 10), lab, font=f(21), fill=SUB, anchor="ma")
    d.line([(x0 - 6, base), (x0 + 4 * (bw + gap) - gap + 6, base)], fill=SUB, width=2)
    text(d, (x0 + 4 * (bw + gap) + 6, base - 96), "합계", 20, SUB)
    text(d, (x0 + 4 * (bw + gap) + 6, base - 66), "200W", 30, ACCENT, bold=True)
    text(d, (M + 26, by + 296), "포트별 배분은 판매처(다나와·노써치) 표기. 벨킨은 배분표를 공개하지 않습니다.",
         18, WARN, R - 26, tag="split-note")

    # 16인치 맥북
    my = by + 350
    d.rounded_rectangle([M, my, R, my + 262], radius=14, fill=WARN_BG)
    text(d, (M + 26, my + 20), "16형 맥북프로를 140W로 채우려면", 26, WARN, R - 26, bold=True)
    yy = my + 62
    for ln in [
        "C1이나 C2에 노트북을 단독으로 꽂아야 140W가 나옵니다. 나머지 포트를 쓰면 70W로 내려갑니다.",
        "70W로도 충전은 되지만, 16형 맥북프로의 최고 속도는 아닙니다. 편집·렌더링 중이 아니라면 체감 차이는 작습니다.",
        "140W는 PD 3.1(EPR) 28V·5A입니다. 100W(20V·5A) 케이블로는 140W가 나오지 않습니다(다음 장).",
    ]:
        yy = para(d, (M + 26, yy), "· " + ln, 21, WARN, R - M - 52, 1.38)
        yy += 8

    brand(d, H, "벨킨 FAQ · 다나와 · 노써치")
    out = os.path.join(IMG, "belkin-200w-power-split.png")
    img.save(out, optimize=True)
    print(out, img.size)


# ---------------------------------------------------------------- 도해 2
def figure_checklist():
    H = 1640
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")
    texture(d, W, H)

    text(d, (M, 48), "벨킨 200W · 사기 전 확인", 24, ACCENT, R, bold=True)
    text(d, (M - 2, 84), "값을 내기 전에", 44, INK, R + 30, bold=True)
    text(d, (M - 2, 136), "다섯 가지만 보십시오", 44, INK, R + 30, bold=True)
    text(d, (M, 200), "이 다섯 개에서 갈리면, 이 충전기는 사지 않는 편이 낫습니다", 22, SUB, R)

    items = [
        ("01", "C to C 케이블은 따로 삽니다", "구성품은 본체와 1.5m 전원 코드뿐입니다. 140W를 받으려면 240W(EPR) 케이블이 필요합니다.", ACCENT, WARN_BG),
        ("02", "접지 콘센트 자리가 필요합니다", "플러그가 접지형(3구)입니다. 책상 옆 콘센트가 접지 3구인지 먼저 보십시오.", BLUE, (232, 237, 244)),
        ("03", "660g, 책상에 두는 물건입니다", "118.4×92×35.5mm에 660g. 가방에 넣고 다닐 크기가 아닙니다.", GREEN, (231, 240, 235)),
        ("04", "네 개 꽂으면 70W입니다", "노트북·태블릿·폰·워치를 한꺼번에 꽂으면 노트북 몫은 70W입니다.", INK, (238, 236, 232)),
        ("05", "해외 사용은 확인이 필요합니다", "벨킨 글로벌 사양은 100–240V지만, 쿠팡 답변은 ‘220V 전용’(2026.5)과 ‘프리볼트’(2026.7)로 갈립니다.", WARN, WARN_BG),
    ]
    y = 246
    for num, head, body, col, bg in items:
        d.rounded_rectangle([M, y, R, y + 176], radius=12, fill=bg)
        d.text((M + 26, y + 26), num, font=f(30, True), fill=col)
        text(d, (M + 88, y + 26), head, 26, INK, R - 26, bold=True, tag=head)
        para(d, (M + 88, y + 72), body, 21, (72, 74, 80), R - M - 114, 1.38, tag=head + "b")
        y += 192

    # 가격 카드
    py = y + 10
    d.rounded_rectangle([M, py, R, py + 296], radius=12, fill=CARD, outline=LINE, width=2)
    text(d, (M + 26, py + 20), "가격, 이 셋만 확인하십시오", 26, INK, R - 26, bold=True)
    rows = [
        ("쿠팡 표시가", "109,000원", "5,000원 쿠폰 적용 · 결제 전 ‘쿠폰받기’ 필요"),
        ("다른 판매자", "157,300원", "와이엠마켓 · 12/3 도착"),
        ("시장 최저가", "125,100원", "노써치 집계 · 현대Hmall (최근 30일)"),
    ]
    ry = py + 62
    for k, v, note in rows:
        text(d, (M + 26, ry), k, 19, SUB, M + 300)
        d.text((R - 26, ry - 4), v, font=f(26, True),
               fill=ACCENT if v == "109,000원" else (58, 60, 66), anchor="ra")
        text(d, (M + 30, ry + 32), note, 18, SUB, R - 26, tag=k + " note")
        ry += 68
    text(d, (M + 26, py + 268), "표시가는 2026년 11월 28일 밤 쿠팡 상품 페이지 기준입니다.", 17, SUB, R - 26)

    brand(d, H, "쿠팡 · 벨킨 FAQ · 다나와")
    out = os.path.join(IMG, "belkin-200w-checklist.png")
    img.save(out, optimize=True)
    print(out, img.size)


# ---------------------------------------------------------------- 대표 사진
def product_photo():
    src = os.path.join(ROOT, "..", "downloads", "pickearly-candidates-2026-11-28", "coupang2-belkin-200w.jpg")
    im = Image.open(src).convert("RGB")
    out = os.path.join(IMG, "belkin-200w-4port.jpg")
    im.save(out, quality=90, optimize=True)
    print(out, im.size)


# ---------------------------------------------------------------- 썸네일
def thumb_card():
    w, h = 1600, 900
    img = Image.new("RGB", (w, h), INK)
    d = ImageDraw.Draw(img, "RGBA")
    for x in range(-h, w, 22):
        d.line([(x, h), (x + h, 0)], fill=(255, 255, 255, 10), width=1)
    d.rectangle([w - 360, 0, w, 10], fill=ACCENT)

    text(d, (72, 78), "CHARGER · 4-PORT GaN", 28, ACCENT, bold=True)
    text(d, (70, 150), "200W는 합계,", 92, PAPER, bold=True)
    text(d, (70, 262), "한 포트는 140W", 92, PAPER, bold=True)
    text(d, (72, 396), "벨킨 부스트업 프로 200W · WCH015krWH · 109,000원", 30, SUB)
    text(d, (72, 448), "4포트를 다 꽂으면 70·70·30·30W로 나뉩니다", 30, (206, 200, 190))

    charger(d, 70, 520, 700, 200, [("140W", ACCENT), ("140W", ACCENT), ("60W", (120, 166, 210)), ("60W", (120, 166, 210))],
            ["C1", "C2", "C3", "C4"], dark=True)

    chips = ["후기 216건", "2년 보증 · 접지형", "660g · 책상용"]
    cx, cy = 830, 530
    for i, c in enumerate(chips):
        wd = tw(d, c, 28)
        x0 = cx
        d.rounded_rectangle([x0, cy, x0 + wd + 44, cy + 58], radius=29, outline=(255, 255, 255, 55), width=2)
        d.text((x0 + 22, cy + 13), c, font=f(28), fill=(228, 224, 216))
        cy += 76

    d.line([(72, h - 108), (128, h - 108)], fill=ACCENT, width=4)
    text(d, (142, h - 128), "PickEarly", 32, PAPER, bold=True)
    text(d, (312, h - 124), "얼리어답터 연구소", 26, SUB)

    out = os.path.join(IMG, "thumb-belkin-200w.png")
    img.save(out, optimize=True)
    print(out, img.size)


# ---------------------------------------------------------------- OG
def og_card():
    w, h = 1200, 630
    img = Image.new("RGB", (w, h), INK)
    d = ImageDraw.Draw(img, "RGBA")
    for x in range(-h, w, 22):
        d.line([(x, h), (x + h, 0)], fill=(255, 255, 255, 10), width=1)
    d.rectangle([w - 300, 0, w, 8], fill=ACCENT)

    text(d, (64, 62), "쿠팡 · 충전기", 23, ACCENT, bold=True)
    text(d, (62, 112), "200W는 합계,", 62, PAPER, bold=True)
    text(d, (62, 190), "한 포트는 140W", 62, PAPER, bold=True)
    text(d, (64, 292), "벨킨 부스트업 프로 200W WCH015krWH · 109,000원 · 후기 216건", 23, SUB, w - 64)

    chips = ["C1·C2 140W · C3·C4 60W", "4포트 70·70·30·30W", "케이블 240W 별매"]
    cy = 232
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

    out = os.path.join(OG, "og-belkin-200w.png")
    img.save(out, optimize=True)
    print(out, img.size)


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    os.makedirs(OG, exist_ok=True)
    product_photo()
    figure_split()
    figure_checklist()
    thumb_card()
    og_card()
