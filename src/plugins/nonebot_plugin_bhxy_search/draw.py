from PIL import Image, ImageFont, ImageDraw
from pathlib import Path
from io import BytesIO


def draw_text(self, text, size, position, color):

    position = tuple([position[0], position[1] - 6])
    font = ImageFont.truetype('msyhbd.ttc', size)
    draw = ImageDraw.Draw(self)
    draw.text(position, text=text, font=font, fill=color)

def draw_image(equips, equips_num):

    orange = (255, 151, 1)
    blue = (105, 179, 231)
    black = (115, 115, 115)
    red = (194, 67, 64)
    green = (114, 190, 121)
    violet = (198, 107, 170)
    triangle = "▲"
    square = "■"
    round = "●"

    plugin_path = Path("./src/plugins/nonebot_plugin_bhxy_search/image")
    template = Image.open(plugin_path.joinpath("background.png"))

    draw_text(template, '共查询到 ' + str(equips_num) + ' 件装备', 50, (20, 50), orange)

    for equip in equips:
        e = equip[0]

        if e["type"] == "arms":
            e["typeName"] = triangle

        elif e["type"] == "clothes":
            e["typeName"] = square

        else:
            e["typeName"] = round

    for i, equip in enumerate(equips):

        rarity1 = equip[0]['rarity']
        rarity2 = '/' + equip[1]["rarity"] if len(equip) > 1 else ''
        type_name = equip[0]['typeName']
        size = 40
        y = 150 + i * 60
        
        draw_text(template, f'{i + 1}、', size, (70, y), blue)
        draw_text(template, '[', size, (145, y), orange)
        draw_text(template, rarity1 + rarity2, size, (163, y + 3), orange)
        # if len(equip) > 1:
        #     draw_text(template, rarity1 + rarity2, size, (163, y + 3), orange)
        # else:
        #     draw_text(template, rarity1, size, (190, y + 3), orange)
        draw_text(template, '★]', size, (235, y), orange)
        draw_text(template, equip[0]['title'], size, (310, y), blue)

        if type_name == triangle:
            draw_text(template, type_name, 29, (280, y + 2), orange)

        elif type_name == square:
            draw_text(template, type_name, 38, (282, y - 10), orange)

        elif type_name == round:
            draw_text(template, type_name, 40, (280, y - 8), orange)

    template = template.crop((0, 0, template.width, template.height - ((44 - len(equips)) * 60)))

    draw_text(template, '请回复编号查询对应装备', 40, (170, template.height - 110), black)
    draw_text(template, '回复"0"则结束此次查询', 40, (175, template.height - 60), black)

    # if equips_num > 40:
    #     draw_text(template, '# 查询结果超出显示上限，请缩小查询范围', 30, (100, template.height - 170), (156, 156, 156))

    image_bytes = BytesIO()
    template.mode = "RGB"
    template.save(image_bytes, format="PNG")
    return image_bytes.getvalue()