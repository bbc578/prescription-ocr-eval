#!/usr/bin/env python3
"""
Phase 3: expand to 1000+ images.
Add: 中成药、外用、多药处方、横版布局、印章效果、复写效果。
"""
import os, json, random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

BASE = "/root/prescription-ocr-eval/images"
random.seed(2026)

def get_font(size=20):
    for fp in ["/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
               "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"]:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    import subprocess
    try:
        r = subprocess.run(["fc-match", "-f", "%{file}", "lang:zh"], capture_output=True, text=True)
        if r.stdout.strip() and os.path.exists(r.stdout.strip()):
            return ImageFont.truetype(r.stdout.strip(), size)
    except: pass
    return ImageFont.load_default()

GENDERS = ["男", "女"]

NAMES = [
    "张伟", "王芳", "李娜", "刘洋", "陈杰", "杨丽", "赵强", "黄敏",
    "周涛", "吴静", "徐明", "孙磊", "马娟", "朱红", "胡军", "郭兰",
    "何平", "高超", "林芳", "罗刚", "梁辉", "宋杰", "郑丽", "谢勇",
    "韩冰", "唐亮", "董娟", "夏强", "吕婷", "曹峰", "邓芳", "萧亮",
    "田甜", "汪洋", "范刚", "石磊", "廖敏", "姚芳", "邹杰", "熊勇",
    "金亮", "陆芳", "郝强", "孔敏", "白洁", "崔峰", "程亮", "沈芳",
    "任杰", "姜勇", "钟芳", "卢强", "贾敏", "丁芳", "魏杰", "薛勇",
    "方超", "余芳", "潘杰", "杜勇", "叶芳", "苏杰", "卢勇", "蔡芳",
]

# ─── 中成药处方 ──────────────────────────────────────────────────────────────
PATENT_TCM = [
    {"header": "XX市中医院中成药处方", "dept": "中医内科", "items": ["六味地黄丸 200丸×1瓶", "补中益气丸 200丸×1瓶"], "usage": "六味地黄丸 8丸 tid po\n补中益气丸 8丸 tid po"},
    {"header": "XX区中医院处方", "dept": "心病科", "items": ["复方丹参滴丸 180丸×1盒", "麝香保心丸 42丸×1盒"], "usage": "丹参滴丸 10丸 tid po\n麝香保心丸 2丸 tid po"},
    {"header": "XX中医门诊处方", "dept": "脾胃科", "items": ["香砂养胃丸 200丸×1瓶", "保和丸 200丸×1瓶"], "usage": "香砂养胃丸 8丸 tid po\n保和丸 8丸 tid po"},
    {"header": "XX中医院处方笺", "dept": "肺病科", "items": ["急支糖浆 200ml×1瓶", "川贝枇杷膏 150ml×1瓶"], "usage": "急支糖浆 20ml tid po\n川贝枇杷膏 15ml tid po"},
    {"header": "XX社区卫生中心处方", "dept": "全科", "items": ["连花清瘟胶囊 48粒×1盒", "板蓝根颗粒 10袋×1盒"], "usage": "连花清瘟 4粒 tid po\n板蓝根 1袋 tid po"},
    {"header": "XX中医院骨伤科处方", "dept": "骨伤科", "items": ["仙灵骨葆胶囊 50粒×1盒", "骨疏康颗粒 10袋×1盒"], "usage": "仙灵骨葆 3粒 tid po\n骨疏康 1袋 tid po"},
    {"header": "XX中医院妇科处方", "dept": "妇科", "items": ["逍遥丸 200丸×1瓶", "乌鸡白凤丸 10丸×1盒"], "usage": "逍遥丸 8丸 tid po\n乌鸡白凤丸 1丸 bid po"},
    {"header": "XX中医院皮肤科处方", "dept": "皮肤科", "items": ["皮肤病血毒丸 200丸×1瓶", "湿毒清胶囊 60粒×1盒"], "usage": "血毒丸 20丸 bid po\n湿毒清 4粒 tid po"},
    {"header": "XX中医院脑病科处方", "dept": "脑病科", "items": ["天麻素片 100片×1瓶", "养血清脑颗粒 10袋×1盒"], "usage": "天麻素 2片 tid po\n养血清脑 1袋 tid po"},
    {"header": "XX中医院肾病科处方", "dept": "肾病科", "items": ["金水宝胶囊 63粒×1盒", "黄葵胶囊 30粒×1盒"], "usage": "金水宝 3粒 tid po\n黄葵 5粒 tid po"},
]

# ─── 外用处方 ────────────────────────────────────────────────────────────────
TOPICAL_TEMPLATES = [
    {"header": "XX皮肤病医院外用处方", "dept": "皮肤科", "items": [
        "卤米松乳膏 15g×1支", "莫匹罗星软膏 5g×1支",
        "炉甘石洗剂 100ml×1瓶"
    ], "usage": "卤米松 外用 bid\n莫匹罗星 外用 bid\n炉甘石 外用 tid"},
    {"header": "XX骨科医院外用处方", "dept": "骨科", "items": [
        "双氯芬酸二乙胺乳胶剂 20g×1支", "云南白药膏 10贴×1盒"
    ], "usage": "双氯芬酸 外用 bid\n云南白药膏 贴患处 qd"},
    {"header": "XX中医外科外用处方", "dept": "中医外科", "items": [
        "金黄散 30g×1袋", "紫草油 50ml×1瓶"
    ], "usage": "金黄散 醋调外敷 bid\n紫草油 外涂 tid"},
    {"header": "XX眼科医院处方", "dept": "眼科", "items": [
        "左氧氟沙星滴眼液 5ml×1支", "玻璃酸钠滴眼液 10ml×1瓶",
        "妥布霉素地塞米松眼膏 3.5g×1支"
    ], "usage": "左氧氟沙星 1滴 qid\n玻璃酸钠 1滴 tid\n眼膏 睡前涂用"},
    {"header": "XX耳鼻喉科处方", "dept": "耳鼻喉科", "items": [
        "氧氟沙星滴耳液 5ml×1支", "糠酸莫米松鼻喷雾剂 140揿×1支"
    ], "usage": "氧氟沙星 滴耳 tid\n莫米松 2喷 qd 鼻用"},
    {"header": "XX口腔医院外用处方", "dept": "口腔科", "items": [
        "复方氯己定含漱液 200ml×1瓶", "口腔溃疡散 3g×1瓶",
        "丁硼乳膏 65g×1支"
    ], "usage": "氯己定 15ml bid 含漱\n溃疡散 涂患处 tid\n丁硼乳膏 刷牙用"},
]

# ─── 多药复杂处方（6-10种药）────────────────────────────────────────────────
COMPLEX_TEMPLATES = [
    {"header": "XX大学附属医院处方", "dept": "心内科", "items": [
        "阿司匹林肠溶片 100mg×30片", "氯吡格雷片 75mg×30片",
        "阿托伐他汀钙片 20mg×30片", "美托洛尔缓释片 47.5mg×30片",
        "培哚普利叔丁胺片 4mg×30片", "呋塞米片 20mg×30片",
        "螺内酯片 20mg×30片"
    ], "usage": "阿司匹林 100mg qd\n氯吡格雷 75mg qd\n阿托伐他汀 20mg qn\n美托洛尔 47.5mg qd\n培哚普利 4mg qd\n呋塞米 20mg qd\n螺内酯 20mg qd"},
    {"header": "XX医院内分泌科处方", "dept": "内分泌科", "items": [
        "二甲双胍缓释片 0.5g×60片", "格列美脲片 2mg×30片",
        "达格列净片 10mg×30片", "阿托伐他汀钙片 20mg×30片",
        "厄贝沙坦片 150mg×30片", "阿司匹林肠溶片 100mg×30片"
    ], "usage": "二甲双胍 0.5g bid\n格列美脲 2mg qd\n达格列净 10mg qd\n阿托伐他汀 20mg qn\n厄贝沙坦 150mg qd\n阿司匹林 100mg qd"},
    {"header": "XX肿瘤医院支持治疗处方", "dept": "肿瘤内科", "items": [
        "甲氧氯普胺片 10mg×30片", "地塞米松片 0.75mg×30片",
        "奥美拉唑胶囊 20mg×28粒", "阿普唑仑片 0.4mg×14片",
        "曲马多缓释片 100mg×10片", "乳果糖口服溶液 100ml×1瓶"
    ], "usage": "甲氧氯普胺 10mg tid ac\n地塞米松 0.75mg bid\n奥美拉唑 20mg qd\n阿普唑仑 0.4mg qn\n曲马多 100mg q12h prn\n乳果糖 15ml bid"},
    {"header": "XX风湿免疫科处方", "dept": "风湿免疫科", "items": [
        "甲氨蝶呤片 2.5mg×16片", "叶酸片 5mg×30片",
        "羟氯喹片 0.1g×60片", "塞来昔布胶囊 0.2g×20粒",
        "醋酸泼尼松片 5mg×100片", "碳酸钙D3片 600mg×30片"
    ], "usage": "甲氨蝶呤 10mg qw（4片）\n叶酸 5mg qw（次日）\n羟氯喹 0.2g bid\n塞来昔布 0.2g bid\n泼尼松 10mg qd\n碳酸钙D3 600mg qd"},
    {"header": "XX呼吸科处方", "dept": "呼吸内科", "items": [
        "沙美特罗替卡松粉吸入剂 50/250μg×1支", "噻托溴铵粉吸入剂 18μg×30粒",
        "氨溴索片 30mg×60片", "多索茶碱片 0.2g×20片",
        "甲泼尼龙片 4mg×30片"
    ], "usage": "沙美特罗替卡松 1吸 bid\n噻托溴铵 1吸 qd\n氨溴索 30mg tid\n多索茶碱 0.2g bid\n甲泼尼龙 8mg qd"},
]

# ─── 儿科处方（剂量特点）─────────────────────────────────────────────────────
PEDIATRIC_TEMPLATES = [
    {"header": "XX儿童医院处方", "dept": "儿内科", "items": [
        "阿莫西林克拉维酸钾干混悬剂 0.2285g×12包",
        "布洛芬混悬液 100ml×1瓶", "小儿豉翘清热颗粒 6袋×1盒"
    ], "usage": "阿莫西林克拉维酸 1包 tid po\n布洛芬 4ml prn（>38.5℃）\n豉翘 1袋 tid po"},
    {"header": "XX妇幼保健院处方", "dept": "新生儿科", "items": [
        "双歧杆菌活菌散剂 1g×10袋", "维生素D滴剂 400IU×30粒"
    ], "usage": "双歧杆菌 1袋 bid po\nVitD 400IU qd po"},
    {"header": "XX儿童医院处方", "dept": "儿童呼吸科", "items": [
        "阿奇霉素干混悬剂 0.1g×6袋", "丙酸氟替卡松气雾剂 120揿×1支",
        "孟鲁司特钠咀嚼片 4mg×14片"
    ], "usage": "阿奇霉素 0.2g qd po（服3停4）\n氟替卡松 1喷 bid\n孟鲁司特 4mg qn po"},
    {"header": "XX儿童医院皮肤科处方", "dept": "儿童皮肤科", "items": [
        "地奈德乳膏 15g×1支", "氯雷他定糖浆 60ml×1瓶",
        "炉甘石洗剂 100ml×1瓶"
    ], "usage": "地奈德 外用 bid\n氯雷他定 5ml qd po\n炉甘石 外用 tid"},
    {"header": "XX儿童医院消化科处方", "dept": "儿童消化科", "items": [
        "蒙脱石散 3g×10袋", "双歧杆菌三联活菌散 1g×10袋",
        "口服补液盐III 5.125g×6袋"
    ], "usage": "蒙脱石 1袋 tid po\n双歧杆菌 1袋 tid po\nORS 1袋 冲服 prn"},
]

# ─── 横版处方 ────────────────────────────────────────────────────────────────
LANDSCAPE_TEMPLATES = [
    {"header": "XX省人民医院处方笺（横版）", "dept": "神经内科", "items": [
        "左乙拉西坦片 0.5g×60片", "丙戊酸钠缓释片 0.5g×30片"
    ], "usage": "左乙拉西坦 0.5g bid po\n丙戊酸钠 0.5g bid po"},
    {"header": "XX市第一医院处方（横版）", "dept": "消化内科", "items": [
        "艾司奥美拉唑镁肠溶片 20mg×14片", "铝碳酸镁咀嚼片 0.5g×30片",
        "复方消化酶胶囊 20粒×1盒"
    ], "usage": "艾司奥美拉唑 20mg qd\n铝碳酸镁 1g tid\n消化酶 2粒 tid ac"},
    {"header": "XX医院横版处方笺", "dept": "心内科", "items": [
        "沙库巴曲缬沙坦钠片 100mg×28片", "达格列净片 10mg×30片",
        "比索洛尔片 5mg×30片"
    ], "usage": "沙库巴曲缬沙坦 100mg bid\n达格列净 10mg qd\n比索洛尔 5mg qd"},
    {"header": "XX大学附属医院横版处方", "dept": "呼吸内科", "items": [
        "茚达特罗格隆溴铵吸入粉雾剂 110/50μg×30粒",
        "布地奈德福莫特罗粉吸入剂 160/4.5μg×1支"
    ], "usage": "茚达特罗格隆溴铵 1吸 qd\n布地奈德福莫特罗 1吸 bid"},
]

def gen_patient(seed):
    random.seed(seed)
    return random.choice(NAMES), random.choice(GENDERS), random.randint(1, 90), random.randint(1, 12), random.randint(1, 28)

def make_text(tmpl, name, gender, age, month, day):
    lines = [tmpl["header"]]
    lines.append(f"姓名：{name}　性别：{gender}　年龄：{age}岁　日期：2025年{month}月{day}日")
    lines.append(f"科室：{tmpl['dept']}")
    if tmpl.get("ward"):
        lines.append(f"床号：{tmpl['ward']}")
    lines.append("Rp:")
    for j, item in enumerate(tmpl["items"]):
        lines.append(f"  {j+1}. {item}")
    lines.append(f"用法：{tmpl['usage']}")
    if tmpl.get("note"):
        lines.append(f"备注：{tmpl['note']}")
    return lines

def gen_image(text_lines, w, h, diff, noise, rotate=False, stamp=False):
    if diff == "hard":
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
    for line in text_lines:
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
        np.random.seed(hash(str(text_lines)[:50]) % 2**32)
        n = np.random.normal(0, noise, (h, w, 3))
        arr = np.clip(np.array(img).astype(np.float32) + n, 0, 255).astype(np.uint8)
        img = Image.fromarray(arr)
    
    if diff == "hard" and random.random() < 0.3:
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.5)))
    if rotate and diff == "hard":
        img = img.rotate(random.uniform(-3, 3), fillcolor=bgc, expand=False)
    
    # Add stamp effect for some images
    if stamp:
        draw2 = ImageDraw.Draw(img)
        sx, sy = random.randint(w-150, w-80), random.randint(h-100, h-50)
        stamp_font = get_font(14)
        draw2.ellipse([sx, sy, sx+60, sy+60], outline=(200, 0, 0), width=2)
        draw2.text((sx+8, sy+18), "处方", fill=(200, 0, 0), font=stamp_font)
    
    return img

def save(img, fname, cat, src, lines, fields, diff, note=None):
    img.save(os.path.join(BASE, fname))
    ann = {"category": cat, "source": src, "text_full": "\n".join(lines), "fields": fields, "difficulty": diff}
    if note:
        ann["note"] = note
    return fname, ann

def main():
    with open(os.path.join(BASE, "annotations.json"), "r", encoding="utf-8") as f:
        ann = json.load(f)
    
    os.makedirs(os.path.join(BASE, "patent_tcm"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "topical"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "complex"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "pediatric"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "landscape"), exist_ok=True)
    
    idx = 2000
    
    # 1. 中成药处方 (60)
    print("Patent TCM...")
    for i in range(60):
        t = PATENT_TCM[i % len(PATENT_TCM)]
        n, g, a, m, d = gen_patient(idx+i)
        diff = ["easy","medium","hard"][i%3]
        noise = [0, 10, 25][i%3]
        lines = make_text(t, n, g, a, m, d)
        fname = f"patent_tcm/pt_{i:04d}.png"
        img = gen_image(lines, 800, 500, diff, noise, rotate=(i%5==0), stamp=(i%3==0))
        fields = {"hospital":t["header"],"department":t["dept"],"patient_name":n,"gender":g,"age":str(a),"date":f"2025年{m}月{d}日","prescription_items":t["items"],"usage":t["usage"]}
        k, v = save(img, fname, "patent_tcm", "synthetic", lines, fields, diff)
        ann[k] = v
        idx += 1
    
    # 2. 外用处方 (50)
    print("Topical...")
    for i in range(50):
        t = TOPICAL_TEMPLATES[i % len(TOPICAL_TEMPLATES)]
        n, g, a, m, d = gen_patient(idx+i)
        diff = ["easy","medium","hard"][i%3]
        noise = [0, 10, 25][i%3]
        lines = make_text(t, n, g, a, m, d)
        fname = f"topical/to_{i:04d}.png"
        img = gen_image(lines, 800, 550, diff, noise, stamp=(i%4==0))
        fields = {"hospital":t["header"],"department":t["dept"],"patient_name":n,"gender":g,"age":str(a),"date":f"2025年{m}月{d}日","prescription_items":t["items"],"usage":t["usage"]}
        k, v = save(img, fname, "topical", "synthetic", lines, fields, diff)
        ann[k] = v
        idx += 1
    
    # 3. 复杂多药处方 (60)
    print("Complex...")
    for i in range(60):
        t = COMPLEX_TEMPLATES[i % len(COMPLEX_TEMPLATES)]
        n, g, a, m, d = gen_patient(idx+i)
        diff = ["medium","hard","hard"][i%3]
        noise = [10, 22, 32][i%3]
        lines = make_text(t, n, g, a, m, d)
        fname = f"complex/cx_{i:04d}.png"
        img = gen_image(lines, 900, 700, diff, noise, rotate=(i%4==0), stamp=(i%2==0))
        fields = {"hospital":t["header"],"department":t["dept"],"patient_name":n,"gender":g,"age":str(a),"date":f"2025年{m}月{d}日","prescription_items":t["items"],"usage":t["usage"]}
        k, v = save(img, fname, "complex", "synthetic", lines, fields, diff)
        ann[k] = v
        idx += 1
    
    # 4. 儿科处方 (50)
    print("Pediatric...")
    for i in range(50):
        t = PEDIATRIC_TEMPLATES[i % len(PEDIATRIC_TEMPLATES)]
        n, g, a, m, d = gen_patient(idx+i)
        a = random.randint(1, 12)  # Children age
        diff = ["easy","medium","medium"][i%3]
        noise = [0, 8, 15][i%3]
        lines = make_text(t, n, g, a, m, d)
        fname = f"pediatric/pd_{i:04d}.png"
        img = gen_image(lines, 800, 550, diff, noise)
        fields = {"hospital":t["header"],"department":t["dept"],"patient_name":n,"gender":g,"age":str(a),"date":f"2025年{m}月{d}日","prescription_items":t["items"],"usage":t["usage"]}
        k, v = save(img, fname, "pediatric", "synthetic", lines, fields, diff)
        ann[k] = v
        idx += 1
    
    # 5. 横版处方 (50)
    print("Landscape...")
    for i in range(50):
        t = LANDSCAPE_TEMPLATES[i % len(LANDSCAPE_TEMPLATES)]
        n, g, a, m, d = gen_patient(idx+i)
        diff = ["easy","medium","hard"][i%3]
        noise = [0, 10, 25][i%3]
        lines = make_text(t, n, g, a, m, d)
        fname = f"landscape/ls_{i:04d}.png"
        img = gen_image(lines, 1000, 500, diff, noise, rotate=(i%4==0), stamp=(i%3==0))
        fields = {"hospital":t["header"],"department":t["dept"],"patient_name":n,"gender":g,"age":str(a),"date":f"2025年{m}月{d}日","prescription_items":t["items"],"usage":t["usage"]}
        k, v = save(img, fname, "landscape", "synthetic", lines, fields, diff)
        ann[k] = v
        idx += 1
    
    # 6. 更多手写风格 (60)
    print("More handwritten...")
    all_tmpls = PATENT_TCM + TOPICAL_TEMPLATES + PEDIATRIC_TEMPLATES
    for i in range(60):
        t = all_tmpls[i % len(all_tmpls)]
        n, g, a, m, d = gen_patient(idx+i)
        lines = make_text(t, n, g, a, m, d)
        fname = f"handwritten/hw_e{i:04d}.png"
        img = gen_image(lines, 800, 600, "hard", 40, rotate=True)
        cat = "tcm_handwritten" if t in (PATENT_TCM + PEDIATRIC_TEMPLATES) else "western_handwritten"
        fields = {"hospital":t["header"],"department":t["dept"],"patient_name":n,"gender":g,"age":str(a),"date":f"2025年{m}月{d}日","prescription_items":t["items"],"usage":t["usage"]}
        k, v = save(img, fname, cat, "synthetic_handwritten", lines, fields, "hard", "Simulated handwritten style")
        ann[k] = v
        idx += 1
    
    # Save
    with open(os.path.join(BASE, "annotations.json"), "w", encoding="utf-8") as f:
        json.dump(ann, f, indent=2, ensure_ascii=False)
    
    cats = {}; diffs = {}; depts = set()
    for v in ann.values():
        cats[v["category"]] = cats.get(v["category"], 0) + 1
        diffs[v["difficulty"]] = diffs.get(v["difficulty"], 0) + 1
        dept = v.get("fields", {}).get("department", "")
        if dept: depts.add(dept)
    
    print(f"\n=== Phase 3 Complete ===")
    print(f"Total: {len(ann)}")
    print(f"Categories: {cats}")
    print(f"Difficulty: {diffs}")
    print(f"Departments: {len(depts)}")

if __name__ == "__main__":
    main()
