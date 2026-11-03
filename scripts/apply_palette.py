#!/usr/bin/env python3
"""Apply category colors and refresh PNG assets and contact sheets."""

import csv
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
BASE = "#B9E2E4"
SWATCHES = {
    "C": BASE,
    "Y": "#F3DDAE",
    "G": "#CDE3CD",
    "P": "#F2D3DC",
    "O": "#F3D2C2",
    "V": "#DDD9ED",
    "N": "#DCE3DF",
}
COLORS = {
    "交通出行": BASE,
    "餐饮食品": "#F3DDAE",
    "生活服务与缴费": "#DDD9ED",
    "住房": "#F3D2C2",
    "服饰美容": "#F2D3DC",
    "日用家居": "#F3DDAE",
    "人情往来": "#F3D2C2",
    "休闲学习": "#DDD9ED",
    "其他支出": "#DCE3DF",
    "医疗健康": "#CDE3CD",
    "车辆支出": BASE,
    "子女支出": "#F2D3DC",
    "工作收入": "#CDE3CD",
    "礼金红包": "#F3D2C2",
    "补贴津贴": "#DDD9ED",
    "其他收入": "#DCE3DF",
}
SECONDARY_SPEC = {
    ("支出", "交通出行"): "公交车:Y 共享单车:G 打车:C 火车高铁:N 地铁:V 摩的:O 载客三轮:Y 飞机:C",
    ("支出", "餐饮食品"): """
        买菜食材:G 零食:Y 小吃快餐:O 水果:P 晚餐:O 奶茶:O 乳品烘焙:N 饮料:C
        火锅:O 午餐:Y 早餐:Y 烧烤:O 聚会:V 酒:P
    """,
    ("支出", "生活服务与缴费"): """
        水费:C 话费:V 电费:Y 燃气费:O 理发:P 家庭生活费:N 网费:V 快递:Y
        洗衣干洗:C 家政清洁:G
    """,
    ("支出", "住房"): """
        房租:O 房贷:O 装修贷:Y 装修工程:Y 房屋税费:N 房屋维修:G
        车位购买:V 物业费:O 车位租赁与管理:V 乔迁:O
    """,
    ("支出", "服饰美容"): """
        包包:P 内衣睡衣:O 鞋子:O 上衣:G 彩妆:P 首饰配饰:V 外套:V
        美容美甲:P 裤子:C 护肤:P 其他服装:Y 裙子:P
    """,
    ("支出", "日用家居"): """
        清洁用品与纸品:Y 数码设备与配件:N 卫浴用品:C 厨房用品:O 日用杂货:Y
        家具家饰:G 床品布艺:V 家用电器:N 个人护理:P
    """,
    ("支出", "人情往来"): "红包礼金:O 礼物:Y 鲜花:P 亲属支持:O",
    ("支出", "休闲学习"): """
        彩票:V 宠物:O 游戏:P 个人订阅:V 电影演出:Y 学习培训:G
        考证考试:Y 旅游:N 运动健身:O 游乐场:P
    """,
    ("支出", "其他支出"): """
        信用卡还款汇总:N 工作工具订阅:V 打印复印:N 零星杂项:N 工作杂费:G
        宗教信仰:Y 证件事务:V 手续费:N
    """,
    ("支出", "医疗健康"): """
        挂号就诊:G 牙科/眼科:Y 药品耗材:P 住院手术:C
        医疗保险:G 保健营养:Y 体检:G
    """,
    ("支出", "车辆支出"): """
        加油:O 停车:V 充电:G 汽车用品:N 车辆保险:G 购车费用:C 过路费:N
        车贷还款:Y 交通罚款:O 代驾:C 洗车美容:C 维修保养:G
    """,
    ("支出", "子女支出"): """
        育儿用品:P 奶粉:Y 其他:V 纸尿裤:N 床品寝具:V 洗护:P 玩具:V
        医保/保险:G 保健营养:Y 就诊与儿保:G 服饰:P 安全防护:G
        药品耗材:P 游玩活动:V 零食:Y 餐食:O 绘本图书:Y
        教育托育:G 生日庆祝:P
    """,
    ("收入", "工作收入"): "工资薪金:G 奖金:Y 劳务报酬:O",
    ("收入", "其他收入"): "个税退税:N 闲置出售:V 退款:G 利息收入:Y 理财:G 投资收益:Y",
    ("收入", "礼金红包"): "其他礼金:O 乔迁礼金:G 子女礼金:P 婚丧礼金:V",
    ("收入", "补贴津贴"): """
        产检补贴:P 住房补贴:G 生育津贴:O 育儿补贴:P 餐饮交通补贴:Y
    """,
}
PORTRAIT_CATEGORIES = {
    ("支出", "子女支出", ""),
    ("支出", "子女支出", "就诊与儿保"),
    ("支出", "子女支出", "医保/保险"),
    ("收入", "礼金红包", "子女礼金"),
    ("收入", "补贴津贴", "育儿补贴"),
}
SECONDARY = {
    category: dict(entry.rsplit(":", 1) for entry in spec.split())
    for category, spec in SECONDARY_SPEC.items()
}
PALETTE = re.compile(r'(\b(?:fill|stroke)=")(' + "|".join(sorted(set(SWATCHES.values()))) + r')(")')
FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"


def rows():
    with (ROOT / "分类清单.csv").open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def portrait_variants(items):
    result = []
    for item in items:
        key = item["收支"], item["一级分类"], item["二级分类"]
        if key in PORTRAIT_CATEGORIES:
            assert item["SVG"].endswith("(女).svg")
            male = item.copy()
            for field in ("SVG", "PNG"):
                male[field] = item[field].replace("(女).", "(男).")
            result.extend((item, male))
    assert len(result) == 10
    return result


def recolor(items):
    updated = 0
    rendered = 0
    for item in items:
        path = ROOT / item["SVG"]
        png = ROOT / item["PNG"]
        original = path.read_text(encoding="utf-8")
        ET.fromstring(original)
        color = (SWATCHES[SECONDARY[item["收支"], item["一级分类"]][item["二级分类"]]]
                 if item["二级分类"] else COLORS[item["一级分类"]])
        replacement = PALETTE.sub(lambda match: match[1] + color + match[3], original)
        if replacement != original:
            ET.fromstring(replacement)
            path.write_text(replacement, encoding="utf-8")
            updated += 1
        if replacement != original or not png.exists() or path.stat().st_mtime_ns > png.stat().st_mtime_ns:
            subprocess.run(["rsvg-convert", "-w", "512", "-h", "512", "-o", str(png), str(path)], check=True)
            rendered += 1
    return updated, rendered


def contact_sheet(title, items, output, columns, variant_labels=False):
    rows_count = (len(items) + columns - 1) // columns
    cell_width = 172 if columns == 8 else 190
    sheet = Image.new("RGB", (columns * cell_width, 77 + rows_count * 190), "white")
    draw = ImageDraw.Draw(sheet)
    draw.text((24, 16), title, font=ImageFont.truetype(FONT, 27), fill="#354754")
    for index, item in enumerate(items):
        col, row = index % columns, index // columns
        icon = Image.open(ROOT / item["PNG"]).convert("RGBA")
        icon.thumbnail((120, 120), Image.Resampling.LANCZOS)
        sheet.paste(icon, (col * cell_width + (cell_width - icon.width) // 2, 75 + row * 190), icon)
        label = item["二级分类"] or item["一级分类"]
        if variant_labels:
            label += Path(item["SVG"]).stem[-3:]
        size = 20
        while size > 12:
            font = ImageFont.truetype(FONT, size)
            if draw.textbbox((0, 0), label, font=font)[2] <= cell_width - 8:
                break
            size -= 1
        width = draw.textbbox((0, 0), label, font=font)[2]
        draw.text((col * cell_width + (cell_width - width) // 2, 209 + row * 190), label, font=font, fill="#354754")
    sheet.save(ROOT / output)


def main():
    items = rows()
    assert len(items) == 157
    assert {(item["收支"], item["一级分类"], item["二级分类"])
            for item in items if item["二级分类"]} == {
                (flow, category, name)
                for (flow, category), names in SECONDARY.items() for name in names
            }
    variants = portrait_variants(items)
    updated, rendered = recolor(items + variants[1::2])
    for flow in ("支出", "收入"):
        selected = [item for item in items if item["收支"] == flow]
        contact_sheet(f"{flow}分类图标  ·  {len(selected)} 个", selected, f"预览-{flow}.png", 8)
    indexed = {item["SVG"]: item for item in items}
    paths = (ROOT / "scripts/adjusted_icon_paths.txt").read_text(encoding="utf-8").splitlines()
    adjusted = [indexed[path] for path in paths]
    assert len(adjusted) == 49
    contact_sheet("调整图标  ·  49 个", adjusted, "调整预览.png", 6)
    contact_sheet("子女图标  ·  女生 / 男生", variants, "预览-子女变体.png", 5,
                  variant_labels=True)
    print(f"Updated {updated} SVGs, rendered {rendered} PNGs and 4 previews")


if __name__ == "__main__":
    main()
