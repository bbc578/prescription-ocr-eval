#!/usr/bin/env python3
"""
Phase 4: mass expansion to 1500+ via template variations, layout variants, noise combos.
"""
import os, json, random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np

BASE = "/root/prescription-ocr-eval/images"
random.seed(2026)

def get_font(size=20):
    for fp in ["/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
               "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"]:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()

NAMES = ["张伟","王芳","李娜","刘洋","陈杰","杨丽","赵强","黄敏","周涛","吴静",
    "徐明","孙磊","马娟","朱红","胡军","郭兰","何平","高超","林芳","罗刚",
    "梁辉","宋杰","郑丽","谢勇","韩冰","唐亮","董娟","夏强","吕婷","曹峰",
    "邓芳","萧亮","田甜","汪洋","范刚","石磊","廖敏","姚芳","邹杰","熊勇",
    "金亮","陆芳","郝强","孔敏","白洁","崔峰","程亮","沈芳","任杰","姜勇",
    "钟芳","卢强","贾敏","丁芳","魏杰","薛勇","方超","余芳","潘杰","杜勇",
    "叶芳","苏杰","蔡芳","戴杰","姚勇","崔芳","丁杰","苏勇","彭芳","潘强"]
GENDERS = ["男", "女"]

# All templates combined
ALL_TEMPLATES = [
    # TCM
    {"cat":"tcm","header":"XX省中医院处方笺","dept":"中医内科","items":["黄芪 15g","当归 10g","白术 12g","茯苓 15g","甘草 6g"],"usage":"水煎服，日一剂"},
    {"cat":"tcm","header":"XX市中医院处方","dept":"中医内科","items":["党参 15g","白术 12g","茯苓 12g","山药 20g","薏苡仁 15g","陈皮 6g"],"usage":"水煎服，早晚各一次"},
    {"cat":"tcm","header":"XX区中医医院处方笺","dept":"中医内科","items":["柴胡 10g","黄芩 10g","半夏 9g","生姜 3片","大枣 3枚","甘草 6g"],"usage":"水煎服，日一剂"},
    {"cat":"tcm","header":"XX市中医院处方笺","dept":"针灸推拿科","items":["川芎 10g","丹参 15g","红花 6g","桃仁 10g","赤芍 12g"],"usage":"水煎服，分两次温服"},
    {"cat":"tcm","header":"XX中医骨伤医院处方","dept":"针灸推拿科","items":["独活 12g","桑寄生 15g","杜仲 12g","牛膝 10g","细辛 3g"],"usage":"水煎服，日一剂"},
    {"cat":"tcm","header":"XX区中医门诊处方","dept":"中医外科","items":["金银花 15g","连翘 12g","蒲公英 20g","紫花地丁 15g"],"usage":"水煎服，日一剂，忌辛辣"},
    {"cat":"tcm","header":"XX中医诊所处方","dept":"妇科","items":["当归 12g","白芍 10g","熟地黄 15g","川芎 8g"],"usage":"水煎服，经后服用"},
    {"cat":"tcm","header":"XX省中医院妇科处方","dept":"妇科","items":["益母草 15g","香附 10g","当归 12g","川芎 8g","红花 6g"],"usage":"水煎服，经前一周开始"},
    {"cat":"tcm","header":"XX儿童医院中医科处方","dept":"儿科","items":["太子参 10g","白术 8g","茯苓 10g","山药 12g","鸡内金 6g"],"usage":"水煎服，日一剂，分三次"},
    {"cat":"tcm","header":"XX中医皮肤科处方","dept":"皮肤科","items":["地肤子 15g","白鲜皮 12g","苦参 10g","蛇床子 10g"],"usage":"水煎外洗，日二次"},
    {"cat":"tcm","header":"XX中医骨伤科处方","dept":"骨伤科","items":["续断 12g","骨碎补 10g","自然铜 15g","乳香 6g","没药 6g"],"usage":"水煎服，日一剂"},
    {"cat":"tcm","header":"XX中医院肛肠科处方","dept":"肛肠科","items":["地榆 15g","槐花 12g","黄芩 10g","枳壳 10g","大黄 6g"],"usage":"水煎服，日一剂"},
    {"cat":"tcm","header":"XX中医院耳鼻喉科处方","dept":"耳鼻喉科","items":["辛夷 10g","苍耳子 10g","白芷 10g","薄荷 6g","细辛 3g"],"usage":"水煎服，日一剂"},
    {"cat":"tcm","header":"XX中医院眼科处方","dept":"眼科","items":["菊花 10g","枸杞子 15g","决明子 12g","青葙子 10g","车前子 10g"],"usage":"水煎服，日一剂"},
    {"cat":"tcm","header":"XX中医院肿瘤科处方","dept":"肿瘤科","items":["白花蛇舌草 30g","半枝莲 20g","薏苡仁 30g","莪术 10g","三棱 10g"],"usage":"水煎服，日一剂"},
    {"cat":"tcm","header":"社区卫生中心处方笺","dept":"全科","items":["柴胡 10g","黄芩 10g","半夏 9g","生姜 3片","大枣 3枚"],"usage":"水煎服，日一剂"},
    {"cat":"tcm","header":"XX中医院肾病科处方","dept":"肾病科","items":["熟地黄 15g","山茱萸 12g","山药 15g","泽泻 10g","茯苓 12g","牡丹皮 10g"],"usage":"水煎服，日一剂"},
    {"cat":"tcm","header":"XX中医院脾胃科处方","dept":"脾胃科","items":["党参 15g","白术 12g","茯苓 12g","甘草 6g","陈皮 10g","半夏 9g"],"usage":"水煎服，日一剂"},
    {"cat":"tcm","header":"XX中医院肺病科处方","dept":"肺病科","items":["麻黄 6g","杏仁 10g","甘草 6g","石膏 20g","桔梗 10g"],"usage":"水煎服，日一剂"},
    {"cat":"tcm","header":"XX中医院心病科处方","dept":"心病科","items":["丹参 15g","三七 6g","川芎 10g","红花 6g","赤芍 10g"],"usage":"水煎服，日一剂"},
    {"cat":"tcm","header":"XX中医院肝病科处方","dept":"肝病科","items":["茵陈 20g","栀子 10g","大黄 6g","柴胡 10g","白芍 12g"],"usage":"水煎服，日一剂"},
    {"cat":"tcm","header":"XX中医院脑病科处方","dept":"脑病科","items":["天麻 10g","钩藤 12g","石决明 15g","牛膝 10g","杜仲 12g"],"usage":"水煎服，日一剂"},
    {"cat":"tcm","header":"XX中医院风湿科处方","dept":"风湿科","items":["独活 12g","羌活 10g","防风 10g","秦艽 10g","威灵仙 12g"],"usage":"水煎服，日一剂"},
    {"cat":"tcm","header":"XX中医院内分泌科处方","dept":"内分泌科","items":["黄芪 20g","生地黄 15g","山药 15g","天花粉 12g","葛根 15g"],"usage":"水煎服，日一剂"},
    {"cat":"tcm","header":"XX中医院男科处方","dept":"男科","items":["枸杞子 15g","菟丝子 12g","覆盆子 10g","五味子 6g","车前子 10g"],"usage":"水煎服，日一剂"},
    {"cat":"tcm","header":"XX中医院治未病科","dept":"治未病科","items":["黄芪 20g","防风 10g","白术 15g","大枣 3枚"],"usage":"水煎服，日一剂，连服两周"},
    {"cat":"tcm","header":"XX中医院糖尿病科","dept":"糖尿病科","items":["黄芪 20g","山药 20g","天花粉 15g","葛根 15g","知母 10g"],"usage":"水煎服，日一剂"},
    {"cat":"tcm","header":"XX中医院甲状腺科","dept":"甲状腺科","items":["夏枯草 15g","浙贝母 10g","玄参 12g","牡蛎 20g","海藻 10g"],"usage":"水煎服，日一剂"},
    # Western
    {"cat":"western","header":"XX市人民医院处方笺","dept":"内科","items":["阿莫西林胶囊 0.5g×24粒","布洛芬缓释胶囊 0.3g×12粒"],"usage":"阿莫西林 0.5g tid po\n布洛芬 0.3g prn po"},
    {"cat":"western","header":"XX区医院门诊处方","dept":"呼吸内科","items":["头孢克洛胶囊 0.25g×12粒","盐酸氨溴索片 30mg×20片"],"usage":"头孢 0.25g tid po\n氨溴索 30mg tid po"},
    {"cat":"western","header":"XX医院处方笺","dept":"消化内科","items":["奥美拉唑胶囊 20mg×14粒","多潘立酮片 10mg×30片"],"usage":"奥美拉唑 20mg qd po\n多潘立酮 10mg tid ac"},
    {"cat":"western","header":"XX区医院处方笺","dept":"心内科","items":["硝苯地平控释片 30mg×7片","阿托伐他汀钙片 20mg×7片"],"usage":"硝苯地平 30mg qd\n阿托伐他汀 20mg qn"},
    {"cat":"western","header":"XX医院神经内科处方","dept":"神经内科","items":["卡马西平片 0.2g×30片","甲钴胺片 0.5mg×30片"],"usage":"卡马西平 0.2g bid po\n甲钴胺 0.5mg tid po"},
    {"cat":"western","header":"XX大学附属医院处方","dept":"皮肤科","items":["氯雷他定片 10mg×6片","地奈德乳膏 15g×1支"],"usage":"氯雷他定 10mg qd po\n地奈德乳膏 外用 bid"},
    {"cat":"western","header":"XX骨科医院处方","dept":"骨科","items":["塞来昔布胶囊 0.2g×10粒","氨基葡萄糖硫酸盐胶囊 0.25g×60粒"],"usage":"塞来昔布 0.2g bid po\n氨糖 0.5g tid po"},
    {"cat":"western","header":"XX妇幼保健院处方","dept":"妇产科","items":["甲硝唑片 0.2g×21片","克霉唑阴道片 0.5g×3片"],"usage":"甲硝唑 0.2g tid po\n克霉唑 阴道用药 qn×3d"},
    {"cat":"western","header":"XX医院泌尿外科处方","dept":"泌尿外科","items":["左氧氟沙星片 0.5g×6片","坦索罗辛缓释胶囊 0.4mg×10粒"],"usage":"左氧 0.5g qd po\n坦索罗辛 0.4mg qn po"},
    {"cat":"western","header":"XX眼科医院处方","dept":"眼科","items":["左氧氟沙星滴眼液 5ml×1支","玻璃酸钠滴眼液 10ml×1支"],"usage":"左氧氟沙星 1滴 qid\n玻璃酸钠 1滴 tid"},
    {"cat":"western","header":"XX医院耳鼻喉科处方","dept":"耳鼻喉科","items":["桉柠蒎肠溶软胶囊 0.3g×12粒","糠酸莫米松鼻喷雾剂 140揿×1支"],"usage":"桉柠蒎 0.3g tid po\n莫米松 2喷 qd 鼻用"},
    {"cat":"western","header":"XX儿童医院处方","dept":"儿科","items":["阿莫西林克拉维酸钾干混悬剂 0.2285g×12包","小儿氨酚黄那敏颗粒 10袋"],"usage":"阿莫西林克拉维酸 1包 tid po\n氨酚黄那敏 1包 tid po"},
    {"cat":"western","header":"社区卫生服务中心处方","dept":"全科","items":["硝苯地平缓释片 10mg×30片","二甲双胍缓释片 0.5g×30片"],"usage":"硝苯地平 10mg bid po\n二甲双胍 0.5g bid po"},
    {"cat":"western","header":"XX医院风湿免疫科处方","dept":"风湿免疫科","items":["甲氨蝶呤片 2.5mg×16片","叶酸片 5mg×30片","塞来昔布胶囊 0.2g×20粒"],"usage":"甲氨蝶呤 10mg qw\n叶酸 5mg qw\n塞来昔布 0.2g bid"},
    {"cat":"western","header":"XX医院内分泌科处方","dept":"内分泌科","items":["二甲双胍缓释片 0.5g×60片","格列美脲片 2mg×30片","达格列净片 10mg×30片"],"usage":"二甲双胍 0.5g bid\n格列美脲 2mg qd\n达格列净 10mg qd"},
    # Inpatient
    {"cat":"inpatient","header":"XX市人民医院住院处方","dept":"心内科","items":["0.9%氯化钠注射液 250ml","注射用头孢曲松钠 2g×2支","阿司匹林肠溶片 100mg×30片","氯吡格雷片 75mg×30片"],"usage":"NS 250ml+头孢曲松 4g ivgtt qd\n阿司匹林 100mg qd\n氯吡格雷 75mg qd","ward":"心内一区 12床"},
    {"cat":"inpatient","header":"XX大学附属医院住院医嘱","dept":"神经外科","items":["20%甘露醇注射液 250ml×3瓶","地塞米松磷酸钠注射液 5mg×3支","注射用头孢噻肟钠 1g×6支"],"usage":"甘露醇 250ml ivgtt q8h\n地塞米松 5mg iv q12h\n头孢噻肟 2g ivgtt q12h","ward":"神外ICU 3床"},
    {"cat":"inpatient","header":"XX区医院住院处方","dept":"骨科","items":["注射用帕瑞昔布钠 40mg×3支","低分子肝素钠注射液 4000IU×7支"],"usage":"帕瑞昔布 40mg iv q12h\n低分子肝素 4000IU ih qd","ward":"骨二区 8床"},
    # Emergency
    {"cat":"emergency","header":"XX市急救中心处方","dept":"急诊科","items":["0.9%氯化钠注射液 500ml×2瓶","注射用头孢曲松钠 2g×2支","破伤风抗毒素注射液 1500IU×1支"],"usage":"NS 500ml+头孢曲松 2g ivgtt st\nTAT 1500IU ih st"},
    {"cat":"emergency","header":"XX医院急诊处方","dept":"急诊外科","items":["注射用帕瑞昔布钠 40mg×1支","0.9%氯化钠注射液 250ml","注射用头孢呋辛钠 1.5g×2支"],"usage":"帕瑞昔布 40mg iv st\nNS 250ml+头孢呋辛 1.5g ivgtt st"},
    # Patent TCM
    {"cat":"patent_tcm","header":"XX市中医院中成药处方","dept":"中医内科","items":["六味地黄丸 200丸×1瓶","补中益气丸 200丸×1瓶"],"usage":"六味地黄丸 8丸 tid po\n补中益气丸 8丸 tid po"},
    {"cat":"patent_tcm","header":"XX区中医院处方","dept":"心病科","items":["复方丹参滴丸 180丸×1盒","麝香保心丸 42丸×1盒"],"usage":"丹参滴丸 10丸 tid po\n麝香保心丸 2丸 tid po"},
    {"cat":"patent_tcm","header":"XX社区卫生中心处方","dept":"全科","items":["连花清瘟胶囊 48粒×1盒","板蓝根颗粒 10袋×1盒"],"usage":"连花清瘟 4粒 tid po\n板蓝根 1袋 tid po"},
    # Special
    {"cat":"special","header":"XX精神卫生中心处方","dept":"精神科","items":["奥氮平片 10mg×28片","氯硝西泮片 2mg×14片"],"usage":"奥氮平 10mg qn po\n氯硝西泮 1mg qn po"},
    {"cat":"special","header":"XX康复医院处方","dept":"康复科","items":["甲钴胺片 0.5mg×60片","维生素B1片 10mg×60片","巴氯芬片 10mg×30片"],"usage":"甲钴胺 0.5mg tid\nVitB1 10mg tid\n巴氯芬 5mg tid"},
    {"cat":"special","header":"XX医院疼痛科处方","dept":"疼痛科","items":["普瑞巴林胶囊 75mg×28粒","塞来昔布胶囊 0.2g×20粒"],"usage":"普瑞巴林 75mg bid\n塞来昔布 0.2g bid"},
]

def gen_patient(seed):
    random.seed(seed)
    return random.choice(NAMES), random.choice(GENDERS), random.randint(1, 90), random.randint(1, 12), random.randint(1, 28)

def make_text(t, n, g, a, m, d):
    lines = [t["header"]]
    lines.append(f"姓名：{n}　性别：{g}　年龄：{a}岁　日期：2025年{m}月{d}日")
    lines.append(f"科室：{t['dept']}")
    if t.get("ward"):
        lines.append(f"床号：{t['ward']}")
    lines.append("Rp:")
    for j, item in enumerate(t["items"]):
        lines.append(f"  {j+1}. {item}")
    lines.append(f"用法：{t['usage']}")
    return lines

def gen_img(lines, w, h, diff, noise, rotate=False, stamp=False, lowres=False, yellow=False, blur=False):
    if yellow:
        bg = random.randint(240, 255)
        bgc = (bg, bg-random.randint(5,20), bg-random.randint(15,40))
    elif diff == "hard":
        bg = random.randint(230, 255)
        bgc = (bg, bg-random.randint(0,15), bg-random.randint(5,25))
    elif diff == "medium":
        bgc = (252, 252, 250)
    else:
        bgc = (255, 255, 255)
    
    img = Image.new("RGB", (w, h), bgc)
    draw = ImageDraw.Draw(img)
    bc = (0,0,0) if diff != "hard" else (random.randint(0,60), random.randint(0,60), random.randint(0,60))
    draw.rectangle([8, 8, w-8, h-8], outline=bc, width=2)
    draw.line([(8, 45), (w-8, 45)], fill=bc, width=1)
    
    font = get_font(18 if diff=="easy" else 16 if diff=="medium" else 15)
    y = 55
    for line in lines:
        if diff == "hard":
            xo, yo = random.randint(-4,4), random.randint(-2,2)
            a = random.randint(40, 100)
            c = (a, a, a)
        elif diff == "medium":
            xo, yo = random.randint(-1,1), random.randint(-1,1)
            c = (random.randint(0,30), random.randint(0,30), random.randint(0,30))
        else:
            xo, yo = 0, 0
            c = (0, 0, 0)
        draw.text((25+xo, y+yo), line, fill=c, font=font)
        y += random.randint(24, 32) if diff == "hard" else 28
    
    if noise > 0:
        np.random.seed(hash(str(lines)[:50]) % 2**32)
        n = np.random.normal(0, noise, (h, w, 3))
        arr = np.clip(np.array(img).astype(np.float32) + n, 0, 255).astype(np.uint8)
        img = Image.fromarray(arr)
    
    if blur or (diff == "hard" and random.random() < 0.3):
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.5)))
    if rotate:
        img = img.rotate(random.uniform(-3, 3), fillcolor=bgc, expand=False)
    if stamp:
        draw2 = ImageDraw.Draw(img)
        sx, sy = random.randint(w-150, w-80), random.randint(h-100, h-50)
        sf = get_font(14)
        draw2.ellipse([sx, sy, sx+60, sy+60], outline=(200, 0, 0), width=2)
        draw2.text((sx+8, sy+18), "处方", fill=(200, 0, 0), font=sf)
    if lowres:
        img = img.resize((w//2, h//2), Image.BILINEAR)
        img = img.resize((w, h), Image.NEAREST)
    
    return img

def main():
    with open(os.path.join(BASE, "annotations.json"), "r", encoding="utf-8") as f:
        ann = json.load(f)
    
    os.makedirs(os.path.join(BASE, "variants"), exist_ok=True)
    idx = 3000
    count = 0
    
    # Generate 500 more images with various combinations
    print("Generating 500 variants...")
    
    variants = [
        # (diff, noise, rotate, stamp, lowres, yellow, blur, w, h)
        ("easy", 0, False, False, False, False, False, 800, 550),
        ("easy", 0, False, True, False, False, False, 800, 550),
        ("easy", 5, False, False, False, False, False, 800, 550),
        ("medium", 8, False, False, False, False, False, 800, 600),
        ("medium", 12, True, False, False, False, False, 800, 600),
        ("medium", 10, False, True, False, False, False, 800, 600),
        ("medium", 15, True, True, False, False, False, 800, 600),
        ("hard", 25, True, False, False, False, False, 800, 600),
        ("hard", 30, True, True, False, False, False, 800, 600),
        ("hard", 35, True, False, False, False, True, 800, 600),
        ("hard", 20, False, True, True, False, False, 800, 600),
        ("hard", 25, True, False, False, True, False, 800, 600),
        ("hard", 30, True, True, False, True, True, 800, 600),
        ("medium", 10, False, False, True, False, False, 800, 600),
        ("easy", 0, False, False, False, False, False, 900, 500),  # landscape
        ("medium", 12, True, True, False, False, False, 900, 500),
        ("hard", 28, True, True, False, True, True, 900, 500),
        ("hard", 40, True, True, False, False, True, 800, 600),  # very noisy
        ("easy", 0, False, True, False, False, False, 850, 550),  # stamp only
        ("medium", 8, False, False, False, False, False, 850, 550),
    ]
    
    for i in range(500):
        tmpl = ALL_TEMPLATES[i % len(ALL_TEMPLATES)]
        n, g, a, m, d = gen_patient(idx + i)
        
        # Special age for pediatric
        if tmpl.get("cat") == "pediatric" or "儿童" in tmpl.get("dept", ""):
            a = random.randint(1, 12)
        
        v = variants[i % len(variants)]
        diff, noise, rot, stamp, lowres, yellow, blur, w, h = v
        
        lines = make_text(tmpl, n, g, a, m, d)
        fname = f"variants/vr_{i:04d}.png"
        
        img = gen_img(lines, w, h, diff, noise, rot, stamp, lowres, yellow, blur)
        img.save(os.path.join(BASE, fname))
        
        fields = {
            "hospital": tmpl["header"], "department": tmpl["dept"],
            "patient_name": n, "gender": g, "age": str(a),
            "date": f"2025年{m}月{d}日",
            "prescription_items": tmpl["items"], "usage": tmpl["usage"],
        }
        
        note_parts = []
        if lowres: note_parts.append("low resolution")
        if yellow: note_parts.append("yellowed paper")
        if blur: note_parts.append("motion blur")
        
        ann[fname] = {
            "category": tmpl.get("cat", "mixed"),
            "source": "synthetic_variant",
            "text_full": "\n".join(lines),
            "fields": fields,
            "difficulty": diff,
        }
        if note_parts:
            ann[fname]["note"] = "; ".join(note_parts)
        
        count += 1
        idx += 1
    
    # Re-save (move save before the directory creation above)
    # Actually let me restructure - save images first
    
    with open(os.path.join(BASE, "annotations.json"), "w", encoding="utf-8") as f:
        json.dump(ann, f, indent=2, ensure_ascii=False)
    
    total = len(ann)
    complete = len([v for v in ann.values() if v.get("text_full") and "待人工" not in v.get("text_full", "")])
    print(f"\n=== Phase 4 Complete ===")
    print(f"Total: {total}")
    print(f"Complete: {complete}")
    
    cats = {}
    for v in ann.values():
        cats[v["category"]] = cats.get(v["category"], 0) + 1
    print(f"Categories: {cats}")

if __name__ == "__main__":
    main()
