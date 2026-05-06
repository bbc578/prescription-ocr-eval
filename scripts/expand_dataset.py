#!/usr/bin/env python3
"""
Massive expansion of prescription OCR evaluation set.
Target: 300+ images across 4 categories, 3 difficulty levels.
"""
import os, json, random, hashlib
from PIL import Image, ImageDraw, ImageFont
import numpy as np

BASE = "/root/prescription-ocr-eval/images"
random.seed(42)

# ─── Expanded Templates ──────────────────────────────────────────────────────

# 中药处方 - 12个科室，每个3-5个药方模板
TCM_TEMPLATES = [
    # 中医内科
    {"header": "XX省中医院处方笺", "dept": "中医内科", "items": ["黄芪 15g", "当归 10g", "白术 12g", "茯苓 15g", "甘草 6g"], "usage": "水煎服，日一剂"},
    {"header": "XX市中医院处方", "dept": "中医内科", "items": ["党参 15g", "白术 12g", "茯苓 12g", "山药 20g", "薏苡仁 15g", "陈皮 6g"], "usage": "水煎服，早晚各一次"},
    {"header": "XX区中医医院处方笺", "dept": "中医内科", "items": ["柴胡 10g", "黄芩 10g", "半夏 9g", "生姜 3片", "大枣 3枚", "甘草 6g"], "usage": "水煎服，日一剂"},
    # 针灸推拿科
    {"header": "XX市中医院处方笺", "dept": "针灸推拿科", "items": ["川芎 10g", "丹参 15g", "红花 6g", "桃仁 10g", "赤芍 12g"], "usage": "水煎服，分两次温服"},
    {"header": "XX中医骨伤医院处方", "dept": "针灸推拿科", "items": ["独活 12g", "桑寄生 15g", "杜仲 12g", "牛膝 10g", "细辛 3g"], "usage": "水煎服，日一剂"},
    # 中医外科
    {"header": "XX区中医门诊处方", "dept": "中医外科", "items": ["金银花 15g", "连翘 12g", "蒲公英 20g", "紫花地丁 15g"], "usage": "水煎服，日一剂，忌辛辣"},
    {"header": "XX中医外科诊所处方", "dept": "中医外科", "items": ["黄柏 10g", "苍术 12g", "薏苡仁 20g", "牛膝 10g", "泽泻 10g"], "usage": "水煎服，外洗患处"},
    # 妇科
    {"header": "XX中医诊所处方", "dept": "妇科", "items": ["当归 12g", "白芍 10g", "熟地黄 15g", "川芎 8g"], "usage": "水煎服，经后服用"},
    {"header": "XX省中医院妇科处方", "dept": "妇科", "items": ["益母草 15g", "香附 10g", "当归 12g", "川芎 8g", "红花 6g"], "usage": "水煎服，经前一周开始"},
    # 儿科
    {"header": "XX儿童医院中医科处方", "dept": "儿科", "items": ["太子参 10g", "白术 8g", "茯苓 10g", "山药 12g", "鸡内金 6g"], "usage": "水煎服，日一剂，分三次"},
    {"header": "XX中医院儿科处方", "dept": "儿科", "items": ["金银花 8g", "连翘 8g", "桔梗 6g", "甘草 4g", "薄荷 3g"], "usage": "水煎服，日一剂"},
    # 皮肤科
    {"header": "XX中医皮肤科处方", "dept": "皮肤科", "items": ["地肤子 15g", "白鲜皮 12g", "苦参 10g", "蛇床子 10g"], "usage": "水煎外洗，日二次"},
    {"header": "XX中医院皮肤科处方", "dept": "皮肤科", "items": ["生地黄 15g", "牡丹皮 10g", "赤芍 10g", "紫草 10g", "白茅根 15g"], "usage": "水煎服，日一剂"},
    # 骨伤科
    {"header": "XX中医骨伤科处方", "dept": "骨伤科", "items": ["续断 12g", "骨碎补 10g", "自然铜 15g", "乳香 6g", "没药 6g"], "usage": "水煎服，日一剂"},
    {"header": "XX骨伤医院处方笺", "dept": "骨伤科", "items": ["当归 12g", "川芎 10g", "赤芍 10g", "桃仁 10g", "红花 6g", "土鳖虫 6g"], "usage": "水煎服，日一剂"},
    # 肛肠科
    {"header": "XX中医院肛肠科处方", "dept": "肛肠科", "items": ["地榆 15g", "槐花 12g", "黄芩 10g", "枳壳 10g", "大黄 6g"], "usage": "水煎服，日一剂"},
    # 耳鼻喉科
    {"header": "XX中医院耳鼻喉科处方", "dept": "耳鼻喉科", "items": ["辛夷 10g", "苍耳子 10g", "白芷 10g", "薄荷 6g", "细辛 3g"], "usage": "水煎服，日一剂"},
    # 眼科
    {"header": "XX中医院眼科处方", "dept": "眼科", "items": ["菊花 10g", "枸杞子 15g", "决明子 12g", "青葙子 10g", "车前子 10g"], "usage": "水煎服，日一剂"},
    # 肿瘤科
    {"header": "XX中医院肿瘤科处方", "dept": "肿瘤科", "items": ["白花蛇舌草 30g", "半枝莲 20g", "薏苡仁 30g", "莪术 10g", "三棱 10g"], "usage": "水煎服，日一剂"},
    # 全科/社区
    {"header": "社区卫生中心处方笺", "dept": "全科", "items": ["柴胡 10g", "黄芩 10g", "半夏 9g", "生姜 3片", "大枣 3枚"], "usage": "水煎服，日一剂"},
    {"header": "XX社区卫生服务站处方", "dept": "全科", "items": ["板蓝根 15g", "大青叶 12g", "连翘 10g", "甘草 6g"], "usage": "水煎服，日一剂"},
    # 肾病科
    {"header": "XX中医院肾病科处方", "dept": "肾病科", "items": ["熟地黄 15g", "山茱萸 12g", "山药 15g", "泽泻 10g", "茯苓 12g", "牡丹皮 10g"], "usage": "水煎服，日一剂"},
    # 脾胃科
    {"header": "XX中医院脾胃科处方", "dept": "脾胃科", "items": ["党参 15g", "白术 12g", "茯苓 12g", "甘草 6g", "陈皮 10g", "半夏 9g"], "usage": "水煎服，日一剂"},
    # 肺病科
    {"header": "XX中医院肺病科处方", "dept": "肺病科", "items": ["麻黄 6g", "杏仁 10g", "甘草 6g", "石膏 20g", "桔梗 10g"], "usage": "水煎服，日一剂"},
    # 心病科
    {"header": "XX中医院心病科处方", "dept": "心病科", "items": ["丹参 15g", "三七 6g", "川芎 10g", "红花 6g", "赤芍 10g"], "usage": "水煎服，日一剂"},
    # 肝病科
    {"header": "XX中医院肝病科处方", "dept": "肝病科", "items": ["茵陈 20g", "栀子 10g", "大黄 6g", "柴胡 10g", "白芍 12g"], "usage": "水煎服，日一剂"},
    # 脑病科
    {"header": "XX中医院脑病科处方", "dept": "脑病科", "items": ["天麻 10g", "钩藤 12g", "石决明 15g", "牛膝 10g", "杜仲 12g"], "usage": "水煎服，日一剂"},
    # 风湿科
    {"header": "XX中医院风湿科处方", "dept": "风湿科", "items": ["独活 12g", "羌活 10g", "防风 10g", "秦艽 10g", "威灵仙 12g"], "usage": "水煎服，日一剂"},
    # 内分泌科
    {"header": "XX中医院内分泌科处方", "dept": "内分泌科", "items": ["黄芪 20g", "生地黄 15g", "山药 15g", "天花粉 12g", "葛根 15g"], "usage": "水煎服，日一剂"},
]

# 西药处方 - 15个科室
WESTERN_TEMPLATES = [
    # 内科
    {"header": "XX市人民医院处方笺", "dept": "内科", "items": ["阿莫西林胶囊 0.5g×24粒", "布洛芬缓释胶囊 0.3g×12粒"], "usage": "阿莫西林 0.5g tid po\n布洛芬 0.3g prn po"},
    {"header": "XX医院门诊处方", "dept": "内科", "items": ["头孢呋辛酯片 0.25g×12片", "复方甘草片 100片"], "usage": "头孢 0.25g bid po\n甘草片 3片 tid po"},
    # 呼吸内科
    {"header": "XX区医院门诊处方", "dept": "呼吸内科", "items": ["头孢克洛胶囊 0.25g×12粒", "盐酸氨溴索片 30mg×20片"], "usage": "头孢 0.25g tid po\n氨溴索 30mg tid po"},
    {"header": "XX市第一人民医院处方", "dept": "呼吸内科", "items": ["阿奇霉素片 0.25g×6片", "孟鲁司特钠片 10mg×7片", "沙丁胺醇气雾剂 100μg×200揿"], "usage": "阿奇 0.25g qd po\n孟鲁司特 10mg qn po\n沙丁胺醇 2揿 prn"},
    # 消化内科
    {"header": "XX医院处方笺", "dept": "消化内科", "items": ["奥美拉唑胶囊 20mg×14粒", "多潘立酮片 10mg×30片"], "usage": "奥美拉唑 20mg qd po\n多潘立酮 10mg tid ac"},
    {"header": "XX大学附属医院处方", "dept": "消化内科", "items": ["泮托拉唑钠肠溶片 40mg×14片", "铝碳酸镁片 0.5g×30片", "枸橼酸莫沙必利片 5mg×20片"], "usage": "泮托拉唑 40mg qd po\n铝碳酸镁 1g tid po\n莫沙必利 5mg tid ac"},
    # 心内科
    {"header": "XX区医院处方笺", "dept": "心内科", "items": ["硝苯地平控释片 30mg×7片", "阿托伐他汀钙片 20mg×7片"], "usage": "硝苯地平 30mg qd\n阿托伐他汀 20mg qn"},
    {"header": "XX心血管病医院处方", "dept": "心内科", "items": ["氯吡格雷片 75mg×14片", "美托洛尔缓释片 47.5mg×14片", "培哚普利叔丁胺片 4mg×14片"], "usage": "氯吡格雷 75mg qd\n美托洛尔 47.5mg qd\n培哚普利 4mg qd"},
    # 神经内科
    {"header": "XX医院神经内科处方", "dept": "神经内科", "items": ["卡马西平片 0.2g×30片", "甲钴胺片 0.5mg×30片"], "usage": "卡马西平 0.2g bid po\n甲钴胺 0.5mg tid po"},
    # 皮肤科
    {"header": "XX大学附属医院处方", "dept": "皮肤科", "items": ["氯雷他定片 10mg×6片", "地奈德乳膏 15g×1支"], "usage": "氯雷他定 10mg qd po\n地奈德乳膏 外用 bid"},
    {"header": "XX皮肤病医院处方", "dept": "皮肤科", "items": ["依巴斯汀片 10mg×10片", "卤米松乳膏 15g×1支", "尿素维E乳膏 50g×1支"], "usage": "依巴斯汀 10mg qd po\n卤米松 外用 bid\n尿素维E 外用 tid"},
    # 骨科
    {"header": "XX骨科医院处方", "dept": "骨科", "items": ["塞来昔布胶囊 0.2g×10粒", "氨基葡萄糖硫酸盐胶囊 0.25g×60粒"], "usage": "塞来昔布 0.2g bid po\n氨糖 0.5g tid po"},
    # 妇产科
    {"header": "XX妇幼保健院处方", "dept": "妇产科", "items": ["甲硝唑片 0.2g×21片", "克霉唑阴道片 0.5g×3片"], "usage": "甲硝唑 0.2g tid po\n克霉唑 阴道用药 qn×3d"},
    # 泌尿外科
    {"header": "XX医院泌尿外科处方", "dept": "泌尿外科", "items": ["左氧氟沙星片 0.5g×6片", "坦索罗辛缓释胶囊 0.4mg×10粒"], "usage": "左氧 0.5g qd po\n坦索罗辛 0.4mg qn po"},
    # 眼科
    {"header": "XX眼科医院处方", "dept": "眼科", "items": ["左氧氟沙星滴眼液 5ml×1支", "玻璃酸钠滴眼液 10ml×1支"], "usage": "左氧氟沙星 1滴 qid\n玻璃酸钠 1滴 tid"},
    # 耳鼻喉科
    {"header": "XX医院耳鼻喉科处方", "dept": "耳鼻喉科", "items": ["桉柠蒎肠溶软胶囊 0.3g×12粒", "糠酸莫米松鼻喷雾剂 140揿×1支"], "usage": "桉柠蒎 0.3g tid po\n莫米松 2喷 qd 鼻用"},
    # 口腔科
    {"header": "XX口腔医院处方", "dept": "口腔科", "items": ["甲硝唑口颊片 3mg×20片", "复方氯己定含漱液 200ml×1瓶"], "usage": "甲硝唑 1片 tid 含服\n氯己定 15ml bid 含漱"},
    # 儿科
    {"header": "XX儿童医院处方", "dept": "儿科", "items": ["阿莫西林克拉维酸钾干混悬剂 0.2285g×12包", "小儿氨酚黄那敏颗粒 10袋"], "usage": "阿莫西林克拉维酸 1包 tid po\n氨酚黄那敏 1包 tid po"},
    # 急诊科
    {"header": "XX医院急诊处方", "dept": "急诊科", "items": ["0.9%氯化钠注射液 250ml×1瓶", "头孢曲松钠注射液 1g×2支", "地塞米松磷酸钠注射液 5mg×1支"], "usage": "NS 250ml+头孢曲松 2g ivgtt st\n地塞米松 5mg iv st"},
    # 全科
    {"header": "社区卫生服务中心处方", "dept": "全科", "items": ["硝苯地平缓释片 10mg×30片", "二甲双胍缓释片 0.5g×30片"], "usage": "硝苯地平 10mg bid po\n二甲双胍 0.5g bid po"},
]

# 真实姓名库
NAMES = [
    "张三", "李四", "王五", "赵六", "陈七", "刘八", "孙九", "周十",
    "吴明", "郑强", "冯刚", "陈静", "褚卫", "蒋华", "沈伟", "韩磊",
    "杨丽", "朱红", "秦军", "许芳", "何平", "吕超", "施亮", "张敏",
    "孔杰", "曹娟", "严峰", "魏兰", "陶勇", "姜涛", "戚宁", "谢婷",
]

GENDERS = ["男", "女"]

# ─── Image Generation ────────────────────────────────────────────────────────

def get_font(size=20):
    """Try to find a Chinese font, fallback to default."""
    font_paths = [
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    # Try system fc-match
    import subprocess
    try:
        result = subprocess.run(["fc-match", "-f", "%{file}", "lang:zh"], capture_output=True, text=True)
        if result.stdout.strip() and os.path.exists(result.stdout.strip()):
            return ImageFont.truetype(result.stdout.strip(), size)
    except:
        pass
    return ImageFont.load_default()

def generate_prescription_image(text_lines, width=800, height=600, difficulty="medium", noise_level=0):
    """Generate a prescription image with text."""
    # Create image
    if difficulty == "hard":
        # Simulate real-world conditions
        bg_color = (random.randint(240, 255), random.randint(235, 250), random.randint(220, 240))
    else:
        bg_color = (255, 255, 255)
    
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Add noise for hard difficulty
    if difficulty == "hard" or noise_level > 0:
        np.random.seed(hash(str(text_lines)) % 2**32)
        noise = np.random.normal(0, noise_level if noise_level > 0 else 15, (height, width, 3))
        img_array = np.array(img).astype(np.float32) + noise
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        img = Image.fromarray(img_array)
        draw = ImageDraw.Draw(img)
    
    # Draw border
    draw.rectangle([10, 10, width-10, height-10], outline=(0, 0, 0), width=2)
    
    # Draw header line
    draw.line([(10, 50), (width-10, 50)], fill=(0, 0, 0), width=1)
    
    # Draw text
    font = get_font(18 if difficulty != "hard" else 16)
    y = 60
    for line in text_lines:
        if difficulty == "hard":
            # Simulate handwriting-like variation
            x_offset = random.randint(-3, 3)
            y_offset = random.randint(-2, 2)
            color = (random.randint(0, 80), random.randint(0, 80), random.randint(0, 80))
        else:
            x_offset = 0
            y_offset = 0
            color = (0, 0, 0)
        
        draw.text((30 + x_offset, y + y_offset), line, fill=color, font=font)
        y += 30 if difficulty != "hard" else random.randint(25, 35)
    
    return img

# ─── Main Generation ─────────────────────────────────────────────────────────

def main():
    os.makedirs(os.path.join(BASE, "tcm"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "western"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "handwritten"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "mixed"), exist_ok=True)
    
    annotations = {}
    idx = 0
    
    # 1. Generate TCM prescriptions (100 images)
    print("Generating TCM prescriptions...")
    for i in range(100):
        tmpl = TCM_TEMPLATES[i % len(TCM_TEMPLATES)]
        random.seed(i * 7 + 13)
        name = random.choice(NAMES)
        gender = random.choice(GENDERS)
        age = random.randint(18, 85)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        
        # Vary difficulty
        if i < 40:
            difficulty = "easy"
            noise = 0
        elif i < 75:
            difficulty = "medium"
            noise = 10
        else:
            difficulty = "hard"
            noise = 25
        
        text_lines = [
            tmpl["header"],
            f"姓名：{name}　性别：{gender}　年龄：{age}岁　日期：2025年{month}月{day}日",
            f"科室：{tmpl['dept']}",
            "Rp:",
        ]
        for j, item in enumerate(tmpl["items"]):
            text_lines.append(f"  {j+1}. {item}")
        text_lines.append(f"用法：{tmpl['usage']}")
        
        fname = f"tcm/tc_{i:04d}.png"
        img = generate_prescription_image(text_lines, difficulty=difficulty, noise_level=noise)
        img.save(os.path.join(BASE, fname))
        
        annotations[fname] = {
            "category": "tcm",
            "source": "synthetic",
            "text_full": "\n".join(text_lines),
            "fields": {
                "hospital": tmpl["header"],
                "department": tmpl["dept"],
                "patient_name": name,
                "gender": gender,
                "age": str(age),
                "date": f"2025年{month}月{day}日",
                "prescription_items": tmpl["items"],
                "usage": tmpl["usage"],
            },
            "difficulty": difficulty,
        }
        idx += 1
    
    # 2. Generate Western prescriptions (100 images)
    print("Generating Western prescriptions...")
    for i in range(100):
        tmpl = WESTERN_TEMPLATES[i % len(WESTERN_TEMPLATES)]
        random.seed(i * 11 + 37)
        name = random.choice(NAMES)
        gender = random.choice(GENDERS)
        age = random.randint(18, 85)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        
        if i < 40:
            difficulty = "easy"
            noise = 0
        elif i < 75:
            difficulty = "medium"
            noise = 10
        else:
            difficulty = "hard"
            noise = 25
        
        text_lines = [
            tmpl["header"],
            f"姓名：{name}　性别：{gender}　年龄：{age}岁　日期：2025年{month}月{day}日",
            f"科室：{tmpl['dept']}",
            "Rp:",
        ]
        for j, item in enumerate(tmpl["items"]):
            text_lines.append(f"  {j+1}. {item}")
        text_lines.append(f"用法：{tmpl['usage']}")
        
        fname = f"western/wm_{i:04d}.png"
        img = generate_prescription_image(text_lines, difficulty=difficulty, noise_level=noise)
        img.save(os.path.join(BASE, fname))
        
        annotations[fname] = {
            "category": "western",
            "source": "synthetic",
            "text_full": "\n".join(text_lines),
            "fields": {
                "hospital": tmpl["header"],
                "department": tmpl["dept"],
                "patient_name": name,
                "gender": gender,
                "age": str(age),
                "date": f"2025年{month}月{day}日",
                "prescription_items": tmpl["items"],
                "usage": tmpl["usage"],
            },
            "difficulty": difficulty,
        }
        idx += 1
    
    # 3. Generate "handwritten" style prescriptions (50 images)
    print("Generating handwritten-style prescriptions...")
    for i in range(50):
        tmpl = random.choice(TCM_TEMPLATES + WESTERN_TEMPLATES)
        random.seed(i * 23 + 71)
        name = random.choice(NAMES)
        gender = random.choice(GENDERS)
        age = random.randint(18, 85)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        
        text_lines = [
            tmpl["header"],
            f"姓名：{name}　性别：{gender}　年龄：{age}岁　日期：2025年{month}月{day}日",
            f"科室：{tmpl['dept']}",
            "Rp:",
        ]
        for j, item in enumerate(tmpl["items"]):
            text_lines.append(f"  {j+1}. {item}")
        text_lines.append(f"用法：{tmpl['usage']}")
        
        fname = f"handwritten/hw_{i:04d}.png"
        img = generate_prescription_image(text_lines, difficulty="hard", noise_level=35)
        img.save(os.path.join(BASE, fname))
        
        category = "tcm" if tmpl in TCM_TEMPLATES else "western"
        annotations[fname] = {
            "category": f"{category}_handwritten",
            "source": "synthetic_handwritten",
            "text_full": "\n".join(text_lines),
            "fields": {
                "hospital": tmpl["header"],
                "department": tmpl["dept"],
                "patient_name": name,
                "gender": gender,
                "age": str(age),
                "date": f"2025年{month}月{day}日",
                "prescription_items": tmpl["items"],
                "usage": tmpl["usage"],
            },
            "difficulty": "hard",
            "note": "Simulated handwritten style with noise and irregular spacing",
        }
        idx += 1
    
    # 4. Generate mixed-language prescriptions (50 images - TCM + Western combined)
    print("Generating mixed prescriptions...")
    for i in range(50):
        random.seed(i * 31 + 97)
        tcm_tmpl = random.choice(TCM_TEMPLATES)
        wm_tmpl = random.choice(WESTERN_TEMPLATES)
        name = random.choice(NAMES)
        gender = random.choice(GENDERS)
        age = random.randint(18, 85)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        
        if i < 20:
            difficulty = "easy"
            noise = 0
        elif i < 40:
            difficulty = "medium"
            noise = 10
        else:
            difficulty = "hard"
            noise = 20
        
        all_items = tcm_tmpl["items"][:3] + wm_tmpl["items"][:2]
        text_lines = [
            f"XX中西医结合医院处方笺",
            f"姓名：{name}　性别：{gender}　年龄：{age}岁　日期：2025年{month}月{day}日",
            f"科室：中西医结合科",
            "Rp:",
        ]
        for j, item in enumerate(all_items):
            text_lines.append(f"  {j+1}. {item}")
        text_lines.append(f"用法：{tcm_tmpl['usage']}；{wm_tmpl['usage'].split(chr(10))[0]}")
        
        fname = f"mixed/mx_{i:04d}.png"
        img = generate_prescription_image(text_lines, difficulty=difficulty, noise_level=noise)
        img.save(os.path.join(BASE, fname))
        
        annotations[fname] = {
            "category": "mixed",
            "source": "synthetic",
            "text_full": "\n".join(text_lines),
            "fields": {
                "hospital": "XX中西医结合医院处方笺",
                "department": "中西医结合科",
                "patient_name": name,
                "gender": gender,
                "age": str(age),
                "date": f"2025年{month}月{day}日",
                "prescription_items": all_items,
                "usage": f"{tcm_tmpl['usage']}；{wm_tmpl['usage'].split(chr(10))[0]}",
            },
            "difficulty": difficulty,
        }
        idx += 1
    
    # Save annotations
    output_path = os.path.join(BASE, "annotations.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(annotations, f, indent=2, ensure_ascii=False)
    
    # Statistics
    cats = {}
    diffs = {}
    for v in annotations.values():
        cats[v["category"]] = cats.get(v["category"], 0) + 1
        diffs[v["difficulty"]] = diffs.get(v["difficulty"], 0) + 1
    
    print(f"\n=== Generation Complete ===")
    print(f"Total images: {len(annotations)}")
    print(f"By category: {cats}")
    print(f"By difficulty: {diffs}")
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    main()
