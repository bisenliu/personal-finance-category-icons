#!/usr/bin/env python3
"""Build screenshot-sized page artwork from the existing category illustrations."""

import csv
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.dont_write_bytecode = True
from apply_palette import COLORS


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "素材/03-支出页面素材"
SCALE = 4

# Bounds are measured from the 544 x 858 reference screenshot.
AREAS = {
    "顶部横幅": (9, 0, 531, 178),
    "左侧插画": (9, 186, 261, 262),
    "餐饮食品": (278, 186, 126, 128),
    "交通出行": (413, 186, 126, 128),
    "车辆支出": (278, 321, 126, 128),
    "子女支出": (413, 321, 126, 128),
    "日用家居": (9, 456, 126, 128),
    "生活服务与缴费": (144, 456, 126, 128),
    "休闲学习": (278, 456, 126, 128),
    "服饰美容": (413, 456, 126, 128),
    "人情往来": (9, 591, 126, 128),
    "住房": (144, 591, 126, 128),
    "右下插画": (278, 591, 261, 262),
    "医疗健康": (9, 726, 126, 128),
    "其他支出": (144, 726, 126, 128),
}


def rgb(value):
    return tuple(int(value[index:index + 2], 16) for index in (1, 3, 5))


def blend(first, second, weight):
    a, b = rgb(first), rgb(second)
    return tuple(round(a[index] * (1 - weight) + b[index] * weight) for index in range(3))


def icons():
    with (ROOT / "分类清单.csv").open(encoding="utf-8-sig", newline="") as source:
        return {
            row["一级分类"]: ROOT / row["PNG"]
            for row in csv.DictReader(source)
            if row["收支"] == "支出" and not row["二级分类"]
        }


def picture(width, height, color):
    return Image.new("RGBA", (width * SCALE, height * SCALE), color)


def ellipse(draw, bounds, color):
    draw.ellipse(tuple(round(point * SCALE) for point in bounds), fill=color)


def polygon(draw, points, color):
    draw.polygon([(round(x * SCALE), round(y * SCALE)) for x, y in points], fill=color)


def paste_icon(target, source, x, y, size):
    with Image.open(source) as opened:
        icon = opened.convert("RGBA").resize((round(size * SCALE),) * 2, Image.Resampling.LANCZOS)
    target.alpha_composite(icon, (round(x * SCALE), round(y * SCALE)))


def category_image(name, paths):
    width, height = AREAS[name][2:]
    color = COLORS[name]
    result = picture(width, height, blend(color, "#FFFFFF", 0.61))
    draw = ImageDraw.Draw(result)
    ellipse(draw, (-38, 83, 166, 166), blend(color, "#FFFFFF", 0.28))
    polygon(draw, [(0, 110), (42, 104), (86, 116), (126, 105), (126, 128), (0, 128)],
            blend(color, "#FFFFFF", 0.45))
    paste_icon(result, paths[name], 25, 20, 76)
    draw.rectangle((0, 84 * SCALE, width * SCALE, height * SCALE),
                   fill=blend(color, "#FFFFFF", 0.82))
    return result


def banner(paths):
    result = picture(531, 178, "#E8F3EC")
    draw = ImageDraw.Draw(result)
    ellipse(draw, (-100, 117, 590, 275), "#CDE3CD")
    ellipse(draw, (210, 117, 610, 222), "#F9FCF7")
    polygon(draw, [(0, 157), (190, 148), (358, 165), (531, 144), (531, 178), (0, 178)], "#B9E2E4")
    paste_icon(result, paths["餐饮食品"], 267, 75, 94)
    paste_icon(result, paths["住房"], 333, 40, 130)
    paste_icon(result, paths["交通出行"], 433, 73, 97)
    return result


def left_illustration(paths):
    result = picture(261, 262, "#E8F3EC")
    draw = ImageDraw.Draw(result)
    ellipse(draw, (-78, 191, 339, 342), "#CDE3CD")
    ellipse(draw, (126, -105, 353, 111), "#FFF2D5")
    paste_icon(result, paths["子女支出"], 20, 27, 215)
    paste_icon(result, ROOT / "素材/01-支出/二级分类/人情往来/鲜花.png", 171, 5, 72)
    return result


def right_illustration(paths):
    result = picture(261, 262, "#F9F0EA")
    draw = ImageDraw.Draw(result)
    ellipse(draw, (-68, 176, 330, 348), "#CDE3CD")
    ellipse(draw, (151, -95, 366, 123), "#F2D3DC")
    paste_icon(result, paths["住房"], 51, 74, 166)
    paste_icon(result, paths["餐饮食品"], -7, 143, 115)
    paste_icon(result, ROOT / "素材/01-支出/二级分类/人情往来/鲜花.png", 161, 5, 104)
    return result


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    paths = icons()
    preview = Image.new("RGBA", (544, 858), "#FFFFFF")
    for name, (x, y, width, height) in AREAS.items():
        if name == "顶部横幅":
            artwork = banner(paths)
        elif name == "左侧插画":
            artwork = left_illustration(paths)
        elif name == "右下插画":
            artwork = right_illustration(paths)
        else:
            artwork = category_image(name, paths)
        filename = f"{name}(女).png" if name in {"子女支出", "左侧插画"} else f"{name}.png"
        artwork.save(OUTPUT / filename)
        preview.alpha_composite(artwork.resize((width, height), Image.Resampling.LANCZOS), (x, y))
    preview.save(OUTPUT / "页面预览.png")
    male_paths = paths.copy()
    male_paths["子女支出"] = ROOT / "素材/01-支出/一级分类/子女支出(男).png"
    category_image("子女支出", male_paths).save(OUTPUT / "子女支出(男).png")
    left_illustration(male_paths).save(OUTPUT / "左侧插画(男).png")


if __name__ == "__main__":
    main()
