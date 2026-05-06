#!/usr/bin/env python3
"""
Phase 2 expansion: add 300+ more images with new prescription types.
Target: 600+ total images.
"""
import os, json, random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageTransform
import numpy as np

BASE = "/root/prescription-ocr-eval/images"
random.seed(2026)

def get_font(size=20):
    font_paths = [
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    import subprocess
    try:
        r = subprocess.run(["fc-match", "-f", "%{file}", "lang:zh"], capture_output=True, text=True)
        if r.stdout.strip() and os.path.exists(r.stdout.strip()):
            return ImageFont.truetype(r.stdout.strip(), size)
    except:
        pass
    return ImageFont.load_default()

NAMES = [
    "张伟", "王芳", "李娜", "刘洋", "陈杰", "杨丽", "赵强", "黄敏",
    "周涛", "吴静", "徐明", "孙磊", "马娟", "朱红", "胡军", "郭兰",
    "何平", "高超", "林芳", "罗刚", "梁辉", "宋杰", "郑丽", "谢勇",
    "韩冰", "唐亮", "董娟", "夏强", "吕婷", "曹峰", "邓芳", "萧亮",
    "田甜", "汪洋", "范刚", "石磊", "廖敏", "姚芳", "邹杰", "熊勇",
    "金亮", "陆芳", "郝强", "孔敏", "白洁", "崔峰", "程亮", "沈芳",
    "任杰", "姜勇", "钟芳", "卢强", "贾敏", "丁芳", "魏杰", "薛勇",
]

GENDERS = ["男", "女"]

# ─── NEW: 住院处方模板 ──────────────────────────────────────────────────────
INPATIENT_TEMPLATES = [
    {"header": "XX市人民医院住院处方", "dept": "心内科", "items": [
        "0.9%氯化钠注射液 250ml", "注射用头孢曲松钠 2g×2支",
        "阿司匹林肠溶片 100mg×30片", "氯吡格雷片 75mg×30片"
    ], "usage": "NS 250ml+头孢曲松 4g ivgtt qd\n阿司匹林 100mg qd\n氯吡格雷 75mg qd", "ward": "心内一区 12床"},
    {"header": "XX大学附属医院住院医嘱", "dept": "神经外科", "items": [
        "20%甘露醇注射液 250ml×3瓶", "地塞米松磷酸钠注射液 5mg×3支",
        "注射用头孢噻肟钠 1g×6支", "奥美拉唑注射液 40mg×3支"
    ], "usage": "甘露醇 250ml ivgtt q8h\n地塞米松 5mg iv q12h\n头孢噻肟 2g ivgtt q12h\n奥美拉唑 40mg iv qd", "ward": "神外ICU 3床"},
    {"header": "XX区医院住院处方", "dept": "骨科", "items": [
        "注射用帕瑞昔布钠 40mg×3支", "低分子肝素钠注射液 4000IU×7支",
        "碳酸钙D3片 600mg×30片"
    ], "usage": "帕瑞昔布 40mg iv q12h\n低分子肝素 4000IU ih qd\n碳酸钙D3 600mg qd po", "ward": "骨二区 8床"},
    {"header": "XX医院住院处方笺", "dept": "呼吸内科", "items": [
        "0.9%氯化钠注射液 100ml", "注射用哌拉西林钠他唑巴坦钠 4.5g×3支",
        "盐酸氨溴索注射液 30mg×6支", "布地奈德混悬液 2mg×6支"
    ], "usage": "NS 100ml+哌拉西林他唑巴坦 4.5g ivgtt q8h\n氨溴索 30mg iv bid\n布地奈德 2mg 雾化 bid", "ward": "呼吸一区 15床"},
    {"header": "XX妇幼保健院住院处方", "dept": "产科", "items": [
        "缩宫素注射液 10IU×3支", "头孢呋辛钠注射液 1.5g×3支",
        "复方氨基酸注射液 250ml×3瓶"
    ], "usage": "缩宫素 10IU im st\n头孢呋辛 1.5g ivgtt q12h\n氨基酸 250ml ivgtt qd", "ward": "产二区 6床"},
    {"header": "XX儿童医院住院处方", "dept": "新生儿科", "items": [
        "注射用头孢噻肟钠 0.5g×3支", "维生素K1注射液 1mg×3支",
        "葡萄糖注射液 10% 100ml×3瓶"
    ], "usage": "头孢噻肟 0.25g ivgtt q12h\nVitK1 1mg iv qd\nGS 10% 30ml ivgtt qd", "ward": "新生儿病房 2床"},
]

# ─── NEW: 急诊处方模板 ──────────────────────────────────────────────────────
EMERGENCY_TEMPLATES = [
    {"header": "XX市急救中心处方", "dept": "急诊科", "items": [
        "0.9%氯化钠注射液 500ml×2瓶", "注射用头孢曲松钠 2g×2支",
        "破伤风抗毒素注射液 1500IU×1支", "利多卡因注射液 5ml×2支"
    ], "usage": "NS 500ml+头孢曲松 2g ivgtt st\nTAT 1500IU ih st（皮试后）\n利多卡因 局麻用"},
    {"header": "XX医院急诊处方", "dept": "急诊外科", "items": [
        "注射用帕瑞昔布钠 40mg×1支", "0.9%氯化钠注射液 250ml",
        "注射用头孢呋辛钠 1.5g×2支"
    ], "usage": "帕瑞昔布 40mg iv st\nNS 250ml+头孢呋辛 1.5g ivgtt st"},
    {"header": "XX中心医院急诊处方", "dept": "急诊内科", "items": [
        "硝酸甘油注射液 5mg×1支", "阿司匹林肠溶片 300mg×3片",
        "肝素钠注射液 12500IU×1支"
    ], "usage": "硝酸甘油 5mg+GS 250ml ivgtt st\n阿司匹林 300mg 嚼服 st\n肝素 5000IU iv st"},
    {"header": "XX医院急诊抢救处方", "dept": "急诊ICU", "items": [
        "肾上腺素注射液 1mg×3支", "阿托品注射液 0.5mg×3支",
        "多巴胺注射液 20mg×5支", "碳酸氢钠注射液 250ml×1瓶"
    ], "usage": "肾上腺素 1mg iv q3-5min\n阿托品 0.5mg iv q3-5min\n多巴胺 200mg+NS 250ml ivgtt\n碳酸氢钠 250ml ivgtt st"},
]

# ─── NEW: 中药配方颗粒处方 ──────────────────────────────────────────────────
GRANULE_TEMPLATES = [
    {"header": "XX中医院配方颗粒处方", "dept": "中医内科", "items": [
        "黄芪配方颗粒 10g×3袋", "当归配方颗粒 6g×3袋",
        "白术配方颗粒 6g×3袋", "茯苓配方颗粒 10g×3袋"
    ], "usage": "开水冲服，日一剂，分两次"},
    {"header": "XX中医药大学附属医院颗粒处方", "dept": "脾胃科", "items": [
        "党参配方颗粒 10g×3袋", "白术配方颗粒 10g×3袋",
        "茯苓配方颗粒 10g×3袋", "甘草配方颗粒 3g×3袋",
        "陈皮配方颗粒 6g×3袋"
    ], "usage": "开水冲服，日一剂，饭前服用"},
    {"header": "XX社区卫生中心中药颗粒", "dept": "全科", "items": [
        "板蓝根配方颗粒 10g×3袋", "连翘配方颗粒 6g×3袋",
        "薄荷配方颗粒 3g×3袋"
    ], "usage": "开水冲服，日一剂"},
    {"header": "XX中医诊所颗粒处方", "dept": "妇科", "items": [
        "当归配方颗粒 6g×3袋", "白芍配方颗粒 6g×3袋",
        "川芎配方颗粒 3g×3袋", "熟地黄配方颗粒 10g×3袋",
        "益母草配方颗粒 10g×3袋"
    ], "usage": "开水冲服，日一剂，经后服用"},
]

# ─── NEW: 特殊处方模板 ──────────────────────────────────────────────────────
SPECIAL_TEMPLATES = [
    # 精神科
    {"header": "XX精神卫生中心处方", "dept": "精神科", "items": [
        "奥氮平片 10mg×28片", "氯硝西泮片 2mg×14片"
    ], "usage": "奥氮平 10mg qn po\n氯硝西泮 1mg qn po", "note": "精神药品处方"},
    # 皮肤科（外用为主）
    {"header": "XX皮肤病防治院处方", "dept": "皮肤科", "items": [
        "复方氟米松软膏 10g×1支", "酮康唑洗剂 200ml×1瓶",
        "氯雷他定片 10mg×12片", "维A酸乳膏 15g×1支"
    ], "usage": "氟米松 外用 bid\n酮康唑 洗剂 每周2次\n氯雷他定 10mg qd po\n维A酸 外用 qn"},
    # 肿瘤科
    {"header": "XX肿瘤医院化疗处方", "dept": "肿瘤内科", "items": [
        "注射用奥沙利铂 100mg×2支", "亚叶酸钙注射液 200mg×2支",
        "氟尿嘧啶注射液 0.25g×8支", "昂丹司琼注射液 8mg×2支"
    ], "usage": "奥沙利铂 135mg/m² ivgtt d1\n亚叶酸钙 200mg ivgtt d1-5\n5-FU 500mg ivgtt d1-5\n昂丹司琼 8mg iv bid", "note": "化疗方案FOLFOX4"},
    # 麻醉科
    {"header": "XX医院麻醉处方", "dept": "麻醉科", "items": [
        "丙泊酚乳状注射液 200mg×2支", "枸橼酸芬太尼注射液 0.1mg×2支",
        "罗库溴铵注射液 50mg×1支", "注射用苯磺酸顺阿曲库铵 10mg×2支"
    ], "usage": "丙泊酚 150mg iv\n芬太尼 0.2mg iv\n罗库溴铵 50mg iv\n顺阿曲库铵 10mg iv", "note": "全麻诱导"},
    # 康复科
    {"header": "XX康复医院处方", "dept": "康复科", "items": [
        "甲钴胺片 0.5mg×60片", "维生素B1片 10mg×60片",
        "巴氯芬片 10mg×30片"
    ], "usage": "甲钴胺 0.5mg tid po\nVitB1 10mg tid po\n巴氯芬 5mg tid po"},
    # 营养科
    {"header": "XX医院营养处方", "dept": "营养科", "items": [
        "肠内营养乳剂(TP) 500ml×3瓶", "复方氨基酸注射液(18AA) 250ml×3瓶",
        "脂溶性维生素注射液 10ml×3支"
    ], "usage": "能全力 500ml 鼻饲 tid\n氨基酸 250ml ivgtt qd\n脂维 10ml ivgtt qd"},
    # 疼痛科
    {"header": "XX医院疼痛科处方", "dept": "疼痛科", "items": [
        "普瑞巴林胶囊 75mg×28粒", "塞来昔布胶囊 0.2g×20粒",
        "盐酸曲马多缓释片 100mg×10片"
    ], "usage": "普瑞巴林 75mg bid po\n塞来昔布 0.2g bid po\n曲马多 100mg q12h po（备用）"},
]

# ─── 新增科室的中药模板 ─────────────────────────────────────────────────────
TCM_EXTRA = [
    {"header": "XX中医院男科处方", "dept": "男科", "items": ["枸杞子 15g", "菟丝子 12g", "覆盆子 10g", "五味子 6g", "车前子 10g"], "usage": "水煎服，日一剂"},
    {"header": "XX中医院治未病科", "dept": "治未病科", "items": ["黄芪 20g", "防风 10g", "白术 15g", "大枣 3枚"], "usage": "水煎服，日一剂，连服两周"},
    {"header": "XX中医院推拿科处方", "dept": "推拿科", "items": ["桂枝 10g", "白芍 12g", "生姜 3片", "大枣 3枚", "甘草 6g"], "usage": "水煎服，日一剂"},
    {"header": "XX中医院糖尿病科", "dept": "糖尿病科", "items": ["黄芪 20g", "山药 20g", "天花粉 15g", "葛根 15g", "知母 10g"], "usage": "水煎服，日一剂"},
    {"header": "XX中医院甲状腺科", "dept": "甲状腺科", "items": ["夏枯草 15g", "浙贝母 10g", "玄参 12g", "牡蛎 20g", "海藻 10g"], "usage": "水煎服，日一剂"},
    {"header": "XX中医院乳腺科处方", "dept": "乳腺科", "items": ["柴胡 10g", "白芍 12g", "当归 10g", "川芎 8g", "香附 10g"], "usage": "水煎服，日一剂"},
    {"header": "XX中医院血液科处方", "dept": "血液科", "items": ["黄芪 20g", "当归 12g", "阿胶 10g", "熟地黄 15g", "白芍 12g"], "usage": "水煎服，日一剂"},
    {"header": "XX中医院泌尿科处方", "dept": "中医泌尿科", "items": ["车前草 15g", "滑石 12g", "瞿麦 10g", "萹蓄 10g", "甘草 6g"], "usage": "水煎服，日一剂"},
]

# ─── 新增科室的西药模板 ─────────────────────────────────────────────────────
WESTERN_EXTRA = [
    {"header": "XX医院风湿免疫科处方", "dept": "风湿免疫科", "items": ["甲氨蝶呤片 2.5mg×16片", "叶酸片 5mg×30片", "塞来昔布胶囊 0.2g×20粒"], "usage": "甲氨蝶呤 10mg qw po（每周一次）\n叶酸 5mg qw po（甲氨蝶呤后第2天）\n塞来昔布 0.2g bid po"},
    {"header": "XX医院血液科处方", "dept": "血液科", "items": ["利妥昔单抗注射液 100mg×4支", "地塞米松磷酸钠注射液 5mg×4支"], "usage": "利妥昔单抗 375mg/m² ivgtt\n地塞米松 20mg iv d1-4"},
    {"header": "XX医院内分泌科处方", "dept": "内分泌科", "items": ["二甲双胍缓释片 0.5g×60片", "格列美脲片 2mg×30片", "达格列净片 10mg×30片"], "usage": "二甲双胍 0.5g bid po\n格列美脲 2mg qd po\n达格列净 10mg qd po"},
    {"header": "XX医院肾内科处方", "dept": "肾内科", "items": ["醋酸泼尼松片 5mg×100片", "环磷酰胺片 50mg×30片", "碳酸钙D3片 600mg×30片"], "usage": "泼尼松 40mg qd po\n环磷酰胺 50mg bid po\n碳酸钙D3 600mg qd po"},
    {"header": "XX胸科医院处方", "dept": "胸外科", "items": ["注射用头孢哌酮钠舒巴坦钠 1.5g×6支", "氨溴索注射液 30mg×6支"], "usage": "头孢哌酮舒巴坦 1.5g ivgtt q12h\n氨溴索 30mg iv bid"},
    {"header": "XX医院感染科处方", "dept": "感染科", "items": ["恩替卡韦分散片 0.5mg×28片", "复方甘草酸苷片 100片"], "usage": "恩替卡韦 0.5mg qd po\n甘草酸苷 3片 tid po"},
    {"header": "XX医院变态反应科处方", "dept": "变态反应科", "items": ["孟鲁司特钠咀嚼片 5mg×14片", "丙酸氟替卡松鼻喷雾剂 120揿×1支", "西替利嗪片 10mg×14片"], "usage": "孟鲁司特 5mg qn po\n氟替卡松 2喷 qd 鼻用\n西替利嗪 10mg qd po"},
    {"header": "XX医院全科门诊处方", "dept": "全科门诊", "items": ["阿莫西林克拉维酸钾片 0.375g×18片", "复方甲氧那明胶囊 12粒×1盒"], "usage": "阿莫西林克拉维酸 0.375g tid po\n甲氧那明 1粒 tid po"},
]

# ─── Image Generation ────────────────────────────────────────────────────────

def generate_prescription_image(text_lines, width=800, height=600, difficulty="medium", noise_level=0, rotate=False):
    """Generate a prescription image with various effects."""
    if difficulty == "hard":
        bg = random.randint(235, 255)
        bg_color = (bg, bg - random.randint(0, 15), bg - random.randint(5, 25))
    elif difficulty == "medium":
        bg_color = (252, 252, 250)
    else:
        bg_color = (255, 255, 255)
    
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw border
    border_color = (0, 0, 0) if difficulty != "hard" else (random.randint(0, 60), random.randint(0, 60), random.randint(0, 60))
    draw.rectangle([8, 8, width-8, height-8], outline=border_color, width=2)
    
    # Header line
    draw.line([(8, 45), (width-8, 45)], fill=border_color, width=1)
    
    # Draw text
    font = get_font(18 if difficulty == "easy" else 16 if difficulty == "medium" else 15)
    y = 55
    for line in text_lines:
        if difficulty == "hard":
            x_off = random.randint(-4, 4)
            y_off = random.randint(-2, 2)
            alpha = random.randint(40, 100)
            color = (alpha, alpha, alpha)
        elif difficulty == "medium":
            x_off = random.randint(-1, 1)
            y_off = random.randint(-1, 1)
            color = (random.randint(0, 30), random.randint(0, 30), random.randint(0, 30))
        else:
            x_off = 0
            y_off = 0
            color = (0, 0, 0)
        
        draw.text((25 + x_off, y + y_off), line, fill=color, font=font)
        y += random.randint(24, 32) if difficulty == "hard" else 28
    
    # Add noise
    if noise_level > 0:
        np.random.seed(hash(str(text_lines)[:50]) % 2**32)
        noise = np.random.normal(0, noise_level, (height, width, 3))
        img_arr = np.array(img).astype(np.float32) + noise
        img_arr = np.clip(img_arr, 0, 255).astype(np.uint8)
        img = Image.fromarray(img_arr)
    
    # Blur for hard
    if difficulty == "hard" and random.random() < 0.3:
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.5)))
    
    # Slight rotation for some hard images
    if rotate and difficulty == "hard":
        angle = random.uniform(-3, 3)
        img = img.rotate(angle, fillcolor=bg_color, expand=False)
    
    return img

def gen_patient_info(seed):
    random.seed(seed)
    name = random.choice(NAMES)
    gender = random.choice(GENDERS)
    age = random.randint(1, 90)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return name, gender, age, month, day

def make_text_lines(tmpl, name, gender, age, month, day, ptype="western"):
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

def save_image_and_annotate(img, fname, category, source, text_lines, fields, difficulty):
    img.save(os.path.join(BASE, fname))
    return fname, {
        "category": category,
        "source": source,
        "text_full": "\n".join(text_lines),
        "fields": fields,
        "difficulty": difficulty,
    }

# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    # Load existing annotations
    with open(os.path.join(BASE, "annotations.json"), "r", encoding="utf-8") as f:
        annotations = json.load(f)
    
    os.makedirs(os.path.join(BASE, "inpatient"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "emergency"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "granule"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "special"), exist_ok=True)
    
    idx = 1000  # Start from 1000 to avoid name collision
    
    # 1. Inpatient prescriptions (60 images)
    print("Generating inpatient prescriptions...")
    for i in range(60):
        tmpl = INPATIENT_TEMPLATES[i % len(INPATIENT_TEMPLATES)]
        name, gender, age, month, day = gen_patient_info(idx + i)
        diff = ["easy", "medium", "hard"][i % 3]
        noise = [0, 12, 28][i % 3]
        rotate = (i % 5 == 0)
        
        text_lines = make_text_lines(tmpl, name, gender, age, month, day)
        fname = f"inpatient/ip_{i:04d}.png"
        img = generate_prescription_image(text_lines, width=850, height=650, difficulty=diff, noise_level=noise, rotate=rotate)
        
        fields = {
            "hospital": tmpl["header"], "department": tmpl["dept"],
            "patient_name": name, "gender": gender, "age": str(age),
            "date": f"2025年{month}月{day}日",
            "ward": tmpl.get("ward", ""),
            "prescription_items": tmpl["items"], "usage": tmpl["usage"],
        }
        fname_key, ann = save_image_and_annotate(img, fname, "inpatient", "synthetic", text_lines, fields, diff)
        annotations[fname_key] = ann
        idx += 1
    
    # 2. Emergency prescriptions (40 images)
    print("Generating emergency prescriptions...")
    for i in range(40):
        tmpl = EMERGENCY_TEMPLATES[i % len(EMERGENCY_TEMPLATES)]
        name, gender, age, month, day = gen_patient_info(idx + i)
        diff = ["medium", "hard", "hard"][i % 3]
        noise = [10, 25, 35][i % 3]
        
        text_lines = make_text_lines(tmpl, name, gender, age, month, day)
        fname = f"emergency/em_{i:04d}.png"
        img = generate_prescription_image(text_lines, width=850, height=600, difficulty=diff, noise_level=noise, rotate=(i%4==0))
        
        fields = {
            "hospital": tmpl["header"], "department": tmpl["dept"],
            "patient_name": name, "gender": gender, "age": str(age),
            "date": f"2025年{month}月{day}日",
            "prescription_items": tmpl["items"], "usage": tmpl["usage"],
        }
        fname_key, ann = save_image_and_annotate(img, fname, "emergency", "synthetic", text_lines, fields, diff)
        annotations[fname_key] = ann
        idx += 1
    
    # 3. Granule prescriptions (40 images)
    print("Generating granule prescriptions...")
    for i in range(40):
        tmpl = GRANULE_TEMPLATES[i % len(GRANULE_TEMPLATES)]
        name, gender, age, month, day = gen_patient_info(idx + i)
        diff = ["easy", "medium", "medium"][i % 3]
        noise = [0, 8, 15][i % 3]
        
        text_lines = make_text_lines(tmpl, name, gender, age, month, day)
        fname = f"granule/gr_{i:04d}.png"
        img = generate_prescription_image(text_lines, width=800, height=550, difficulty=diff, noise_level=noise)
        
        fields = {
            "hospital": tmpl["header"], "department": tmpl["dept"],
            "patient_name": name, "gender": gender, "age": str(age),
            "date": f"2025年{month}月{day}日",
            "prescription_items": tmpl["items"], "usage": tmpl["usage"],
        }
        fname_key, ann = save_image_and_annotate(img, fname, "granule", "synthetic", text_lines, fields, diff)
        annotations[fname_key] = ann
        idx += 1
    
    # 4. Special prescriptions (70 images)
    print("Generating special prescriptions...")
    for i in range(70):
        tmpl = SPECIAL_TEMPLATES[i % len(SPECIAL_TEMPLATES)]
        name, gender, age, month, day = gen_patient_info(idx + i)
        diff = ["medium", "hard", "hard"][i % 3]
        noise = [10, 22, 32][i % 3]
        rotate = (i % 3 == 0)
        
        text_lines = make_text_lines(tmpl, name, gender, age, month, day)
        fname = f"special/sp_{i:04d}.png"
        img = generate_prescription_image(text_lines, width=850, height=600, difficulty=diff, noise_level=noise, rotate=rotate)
        
        fields = {
            "hospital": tmpl["header"], "department": tmpl["dept"],
            "patient_name": name, "gender": gender, "age": str(age),
            "date": f"2025年{month}月{day}日",
            "prescription_items": tmpl["items"], "usage": tmpl["usage"],
        }
        if tmpl.get("note"):
            fields["note"] = tmpl["note"]
        fname_key, ann = save_image_and_annotate(img, fname, "special", "synthetic", text_lines, fields, diff)
        annotations[fname_key] = ann
        idx += 1
    
    # 5. Extra TCM (50 images)
    print("Generating extra TCM prescriptions...")
    for i in range(50):
        tmpl = TCM_EXTRA[i % len(TCM_EXTRA)]
        name, gender, age, month, day = gen_patient_info(idx + i)
        diff = ["easy", "medium", "hard"][i % 3]
        noise = [0, 10, 25][i % 3]
        
        text_lines = make_text_lines(tmpl, name, gender, age, month, day, "tcm")
        fname = f"tcm/tc_e{i:04d}.png"
        img = generate_prescription_image(text_lines, difficulty=diff, noise_level=noise, rotate=(i%5==0))
        
        fields = {
            "hospital": tmpl["header"], "department": tmpl["dept"],
            "patient_name": name, "gender": gender, "age": str(age),
            "date": f"2025年{month}月{day}日",
            "prescription_items": tmpl["items"], "usage": tmpl["usage"],
        }
        fname_key, ann = save_image_and_annotate(img, fname, "tcm", "synthetic", text_lines, fields, diff)
        annotations[fname_key] = ann
        idx += 1
    
    # 6. Extra Western (50 images)
    print("Generating extra Western prescriptions...")
    for i in range(50):
        tmpl = WESTERN_EXTRA[i % len(WESTERN_EXTRA)]
        name, gender, age, month, day = gen_patient_info(idx + i)
        diff = ["easy", "medium", "hard"][i % 3]
        noise = [0, 10, 25][i % 3]
        
        text_lines = make_text_lines(tmpl, name, gender, age, month, day)
        fname = f"western/wm_e{i:04d}.png"
        img = generate_prescription_image(text_lines, difficulty=diff, noise_level=noise, rotate=(i%4==0))
        
        fields = {
            "hospital": tmpl["header"], "department": tmpl["dept"],
            "patient_name": name, "gender": gender, "age": str(age),
            "date": f"2025年{month}月{day}日",
            "prescription_items": tmpl["items"], "usage": tmpl["usage"],
        }
        fname_key, ann = save_image_and_annotate(img, fname, "western", "synthetic", text_lines, fields, diff)
        annotations[fname_key] = ann
        idx += 1
    
    # Save
    with open(os.path.join(BASE, "annotations.json"), "w", encoding="utf-8") as f:
        json.dump(annotations, f, indent=2, ensure_ascii=False)
    
    # Stats
    cats = {}
    diffs = {}
    depts = set()
    for v in annotations.values():
        cats[v["category"]] = cats.get(v["category"], 0) + 1
        diffs[v["difficulty"]] = diffs.get(v["difficulty"], 0) + 1
        dept = v.get("fields", {}).get("department", "")
        if dept:
            depts.add(dept)
    
    print(f"\n=== Phase 2 Complete ===")
    print(f"Total images: {len(annotations)}")
    print(f"By category: {cats}")
    print(f"By difficulty: {diffs}")
    print(f"Unique departments: {len(depts)}")

if __name__ == "__main__":
    main()
