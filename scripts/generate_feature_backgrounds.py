#!/usr/bin/env python3
"""Generate text-free backgrounds for the savings, assets, and profile pages."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "素材/04-功能页面背景"
SCALE = 2


def canvas(width, height, color):
    return Image.new("RGBA", (width * SCALE, height * SCALE), color)


def box(values):
    return tuple(round(value * SCALE) for value in values)


def ellipse(draw, bounds, fill, outline=None, width=1):
    draw.ellipse(box(bounds), fill=fill, outline=outline, width=width * SCALE)


def line(draw, points, fill, width):
    draw.line([(round(x * SCALE), round(y * SCALE)) for x, y in points],
              fill=fill, width=width * SCALE, joint="curve")


def polygon(draw, points, fill):
    draw.polygon([(round(x * SCALE), round(y * SCALE)) for x, y in points], fill=fill)


def icon(image, path, x, y, size):
    with Image.open(ROOT / path) as source:
        resized = source.convert("RGBA").resize((size * SCALE, size * SCALE), Image.Resampling.LANCZOS)
    image.alpha_composite(resized, (x * SCALE, y * SCALE))


def flower(draw, x, y, scale=1):
    for dx, dy in ((0, -13), (13, 0), (0, 13), (-13, 0)):
        radius = 8 * scale
        ellipse(draw, (x + dx * scale - radius, y + dy * scale - radius,
                       x + dx * scale + radius, y + dy * scale + radius),
                "#F2D3DC", "#354754", 1)
    ellipse(draw, (x - 5 * scale, y - 5 * scale, x + 5 * scale, y + 5 * scale), "#FFF2D5")


def savings():
    image = canvas(750, 250, "#547867")
    draw = ImageDraw.Draw(image)
    ellipse(draw, (421, -121, 883, 316), "#E8F3EC")
    ellipse(draw, (516, -132, 858, 168), "#FFF2D5")
    ellipse(draw, (-193, 214, 391, 391), "#638C74")
    ellipse(draw, (295, 197, 875, 395), "#CDE3CD")
    ellipse(draw, (456, 218, 885, 371), "#A9D3A5")
    line(draw, [(0, 225), (98, 215), (195, 225), (283, 218)], "#86AA8D", 3)
    for x, y, radius in ((355, 48, 3), (386, 80, 2), (326, 116, 2), (410, 153, 3)):
        ellipse(draw, (x-radius, y-radius, x+radius, y+radius), "#FFF2D5")
    icon(image, "素材/02-收入/二级分类/其他收入/理财.png", 455, 3, 235)
    icon(image, "素材/01-支出/二级分类/人情往来/鲜花.png", 645, 128, 100)
    return image


def assets():
    image = canvas(750, 250, "#E8F3EC")
    draw = ImageDraw.Draw(image)
    ellipse(draw, (438, -128, 811, 247), "#FFF2D5")
    ellipse(draw, (-164, 211, 424, 395), "#CDE3CD")
    ellipse(draw, (270, 195, 887, 381), "#CDE3CD")
    polygon(draw, [(0, 236), (151, 224), (312, 234), (480, 214), (750, 231), (750, 250), (0, 250)],
            "#B9E2E4")
    icon(image, "素材/02-收入/二级分类/其他收入/理财.png", 366, 93, 143)
    icon(image, "素材/01-支出/一级分类/住房.png", 480, 8, 225)
    icon(image, "素材/01-支出/二级分类/人情往来/鲜花.png", 653, 93, 95)
    return image


def profile():
    image = canvas(1120, 634, "#405F68")
    draw = ImageDraw.Draw(image)
    ellipse(draw, (913, 69, 1041, 197), "#FFF2D5")
    ellipse(draw, (943, 55, 1070, 184), "#405F68")
    for x, y, radius in ((115, 117, 3), (280, 77, 2), (479, 133, 3), (712, 77, 2),
                         (819, 184, 2), (1057, 271, 3), (97, 276, 2), (567, 229, 2)):
        ellipse(draw, (x-radius, y-radius, x+radius, y+radius), "#FFF2D5")
    ellipse(draw, (-290, 365, 865, 965), "#608874")
    ellipse(draw, (320, 322, 1385, 943), "#608874")
    ellipse(draw, (-340, 491, 495, 890), "#85A981")
    ellipse(draw, (215, 439, 1120, 946), "#85A981")
    ellipse(draw, (790, 425, 1434, 857), "#85A981")
    ellipse(draw, (-142, 467, 641, 832), "#94B58D")
    ellipse(draw, (537, 491, 1376, 816), "#A9D3A5")
    icon(image, "素材/01-支出/一级分类/住房.png", 832, 268, 238)
    icon(image, "素材/01-支出/二级分类/人情往来/鲜花.png", 1043, 431, 96)
    for x, y, scale in ((108, 564, 0.55), (287, 533, 0.5), (553, 575, 0.45), (762, 558, 0.5)):
        flower(draw, x, y, scale)
    return image


def main():
    OUTPUT.mkdir(exist_ok=True)
    for name, image in (("存钱计划", savings()), ("资产", assets()), ("个人主页", profile())):
        image.save(OUTPUT / f"{name}.png")


if __name__ == "__main__":
    main()
