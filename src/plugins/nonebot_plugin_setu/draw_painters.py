import re
import time
import httpx
import asyncio
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
from pathlib import Path


def draw_text(target, text: str, size: int, position: tuple, color: tuple):
    font = ImageFont.truetype("msyhbd.ttc", size)
    draw = ImageDraw.Draw(target)
    draw.text(position, text=text, font=font, fill=color)


def paste(target, fp, position: tuple, size: tuple, mask=None):
    img = fp if isinstance(fp, Image.Image) else Image.open(fp)
    img = img.resize(size, Image.ANTIALIAS)
    alpha = img.split()[3] if len(img.split()) > 3 else None
    target.paste(img, position, mask=alpha)


def circle_corner(img, radii):  # 把原图片变成圆角，这个函数是从网上找的，原址 https://www.pyget.cn/p/185266
    """
    圆角处理
    :param img: 源图象。
    :param radii: 半径，如：30。
    :return: 返回一个圆角处理后的图象。
    """

    # 画圆（用于分离4个角）
    circle = Image.new('L', (radii * 2, radii * 2), 0)  # 创建一个黑色背景的画布
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)  # 画白色圆形

    # 原图
    img = img.convert("RGBA")
    w, h = img.size

    # 画4个角（将整圆分离为4个部分）
    alpha = Image.new('L', img.size, 255)
    alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))  # 左上角
    alpha.paste(circle.crop((radii, 0, radii * 2, radii)),
                (w - radii, 0))  # 右上角
    alpha.paste(circle.crop((radii, radii, radii * 2, radii * 2)),
                (w - radii, h - radii))  # 右下角
    alpha.paste(circle.crop((0, radii, radii, radii * 2)),
                (0, h - radii))  # 左下角

    img.putalpha(alpha)  # 白色区域透明可见，黑色区域不可见
    return img


def draw(painters):
    plugin_path = Path("./src/plugins/nonebot_plugin_setu/image")
    background = Image.open(plugin_path.joinpath("background.png"))
    number_mask = Image.open(plugin_path.joinpath("number_mask.png"))

    interval = 170
    blue = (0, 150, 250)
    dark_gray = (110, 110, 110)
    count = len(painters) if len(painters) < 10 else 10

    for i in range(count):
        painter = painters[i]

        paste(background, number_mask, position=(
            22, interval * i + 130), size=(65, 51))
        avatar = Image.open(BytesIO(painter["avatar"]))
        paste(
            background,
            circle_corner(avatar, int(avatar.size[0] / 2)),
            position=(95, interval * i + 130),
            size=(112, 112))

        draw_text(
            background,
            text=str(i + 1),
            size=35,
            position=(30, interval * i + 133),
            color=dark_gray)

        draw_text(
            background,
            text=painter["painter"],
            size=30,
            position=(220, interval * i + 133),
            color=dark_gray)

        draw_text(
            background,
            text='插画投稿数: ' + painter["works"],
            size=30,
            position=(220, interval * i + 185),
            color=dark_gray)

    img = background.crop((0, 0, background.size[0], 180 + interval * count))
    draw_text(
        img,
        text='请回复编号查询对应画师',
        size=25,
        position=(200, img.size[1] - 80),
        color=dark_gray
    )

    draw_text(
        img,
        text='回复 "0" 则结束此次查询',
        size=25,
        position=(198, img.size[1] - 50),
        color=dark_gray
    )

    img_bytes = BytesIO()
    img.mode = "RGB"
    img.save(img_bytes, format="PNG")
    return img_bytes.getvalue()


async def get_painter(r, client: httpx.AsyncClient):
    avatar = r.group("avatar")

    return {
        "id": r.group("id"),
        "painter": r.group("painter"),
        "avatar": (await client.get(re.sub(r'piximg.net', 'pixiv.cat', avatar))).content,
        "works": r.group("works")
    }