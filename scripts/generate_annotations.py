#!/usr/bin/env python3
"""Generate ground-truth annotations for the prescription OCR evaluation set."""
import os, json, random

BASE = "/root/prescription-ocr-eval/images"

# TCM prescription templates (matching the generation script)
tcm_templates = [
    {"header": "XX中医院处方笺", "dept": "中医内科", "name": "黄芪 15g", "items": ["黄芪 15g", "当归 10g", "白术 12g", "茯苓 15g", "甘草 6g"], "usage": "水煎服，日一剂"},
    {"header": "XX市中医院处方笺", "dept": "针灸推拿科", "items": ["川芎 10g", "丹参 15g", "红花 6g", "桃仁 10g", "赤芍 12g"], "usage": "水煎服，分两次温服"},
    {"header": "XX区中医门诊处方", "dept": "中医外科", "items": ["金银花 15g", "连翘 12g", "蒲公英 20g", "紫花地丁 15g"], "usage": "水煎服，日一剂，忌辛辣"},
    {"header": "传统中药处方", "dept": "内科", "items": ["人参 10g", "白术 15g", "茯苓 12g", "山药 20g", "薏苡仁 15g"], "usage": "水煎服，早晚各一次"},
    {"header": "XX中医诊所处方", "dept": "妇科", "items": ["当归 12g", "白芍 10g", "熟地黄 15g", "川芎 8g"], "usage": "水煎服，经后服用"},
    {"header": "社区卫生中心处方笺", "dept": "全科", "items": ["柴胡 10g", "黄芩 10g", "半夏 9g", "生姜 3片", "大枣 3枚"], "usage": "水煎服，日一剂"},
]

western_templates = [
    {"header": "XX市人民医院处方笺", "dept": "内科", "items": ["阿莫西林胶囊 0.5g×24粒", "布洛芬缓释胶囊 0.3g×12粒"], "usage": "阿莫西林 0.5g tid po\n布洛芬 0.3g prn po"},
    {"header": "XX区医院门诊处方", "dept": "呼吸内科", "items": ["头孢克洛胶囊 0.25g×12粒", "盐酸氨溴索片 30mg×20片"], "usage": "头孢 0.25g tid po\n氨溴索 30mg tid po"},
    {"header": "XX医院处方笺", "dept": "消化内科", "items": ["奥美拉唑胶囊 20mg×14粒", "多潘立酮片 10mg×30片"], "usage": "奥美拉唑 20mg qd po\n多潘立酮 10mg tid ac"},
    {"header": "社区卫生服务中心处方", "dept": "全科", "items": ["硝苯地平控释片 30mg×7片", "阿托伐他汀钙片 20mg×7片"], "usage": "硝苯地平 30mg qd\n阿托伐他汀 20mg qn"},
    {"header": "XX大学附属医院处方", "dept": "皮肤科", "items": ["氯雷他定片 10mg×6片", "地奈德乳膏 15g×1支"], "usage": "氯雷他定 10mg qd po\n地奈德乳膏 外用 bid"},
]

names = ["张三", "李四", "王五", "赵六", "陈七", "刘八"]
genders = ["男", "女"]

annotations = {}

# Annotate synthetic TCM images
tcm_dir = os.path.join(BASE, "tcm")
if os.path.exists(tcm_dir):
    for fname in sorted(os.listdir(tcm_dir)):
        if not fname.endswith((".png", ".jpg", ".jpeg")):
            continue
        if "synth" in fname:
            idx = int(fname.split("_")[-1].split(".")[0])
            tmpl = tcm_templates[idx % len(tcm_templates)]
            random.seed(idx)
            name = random.choice(names)
            gender = random.choice(genders)
            age = random.randint(25, 75)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            
            text_lines = [
                tmpl["header"],
                f"姓名：{name}　性别：{gender}　年龄：{age}岁　日期：2025年{month}月{day}日",
                f"科室：{tmpl['dept']}",
                "Rp:",
            ]
            for j, item in enumerate(tmpl["items"]):
                text_lines.append(f"{j+1}. {item}")
            text_lines.append(f"用法：{tmpl['usage']}")
            
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
                "difficulty": "medium",
            }
        else:
            # Web-downloaded image - manual annotation needed
            annotations[fname] = {
                "category": "tcm",
                "source": "web",
                "text_full": "[待人工标注]",
                "fields": {},
                "difficulty": "hard",
                "note": "Real-world image, requires manual annotation",
            }

# Annotate synthetic Western medicine images
western_dir = os.path.join(BASE, "western")
if os.path.exists(western_dir):
    for fname in sorted(os.listdir(western_dir)):
        if not fname.endswith((".png", ".jpg", ".jpeg")):
            continue
        if "synth" in fname:
            idx = int(fname.split("_")[-1].split(".")[0])
            tmpl = western_templates[idx % len(western_templates)]
            random.seed(idx + 100)
            name = random.choice(names)
            gender = random.choice(genders)
            age = random.randint(25, 75)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            
            text_lines = [
                tmpl["header"],
                f"姓名：{name}　性别：{gender}　年龄：{age}岁　日期：2025年{month}月{day}日",
                f"科室：{tmpl['dept']}",
                "Rp:",
            ]
            for j, item in enumerate(tmpl["items"]):
                text_lines.append(f"{j+1}. {item}")
            text_lines.append(f"用法：{tmpl['usage']}")
            
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
                "difficulty": "medium",
            }
        else:
            annotations[fname] = {
                "category": "western",
                "source": "web",
                "text_full": "[待人工标注]",
                "fields": {},
                "difficulty": "hard",
                "note": "Real-world image, requires manual annotation",
            }

# Annotate handwritten images
hw_dir = os.path.join(BASE, "handwritten")
if os.path.exists(hw_dir):
    for fname in sorted(os.listdir(hw_dir)):
        if not fname.endswith((".png", ".jpg", ".jpeg")):
            continue
        annotations[fname] = {
            "category": "handwritten",
            "source": "web",
            "text_full": "[待人工标注]",
            "fields": {},
            "difficulty": "hard",
            "note": "Real-world handwritten prescription, requires manual annotation",
        }

# Save annotations
output_path = os.path.join(BASE, "annotations.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(annotations, f, indent=2, ensure_ascii=False)

# Statistics
total = len(annotations)
synthetic = sum(1 for v in annotations.values() if v["source"] == "synthetic")
web = sum(1 for v in annotations.values() if v["source"] == "web")
annotated = sum(1 for v in annotations.values() if v["text_full"] != "[待人工标注]")

print(f"Total images: {total}")
print(f"  Synthetic (auto-annotated): {synthetic}")
print(f"  Web (needs manual annotation): {web}")
print(f"  Fully annotated: {annotated}")
print(f"Saved to: {output_path}")
