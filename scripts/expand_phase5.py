#!/usr/bin/env python3
"""
Phase 5: push to 2000+ images.
New: 电子处方风格, 医保处方, 带化验单, 涂改处方, 更多药物组合变体.
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
    "叶芳","苏杰","蔡芳","戴杰","姚勇","崔芳","丁杰","苏勇","彭芳","潘强",
    "于洋","蒋芳","余杰","叶勇","夏芳","田杰","杜勇","廖芳","熊杰","范勇"]
GENDERS = ["男", "女"]

# 电子处方风格模板
E_PRESCRIPTION = [
    {"cat":"e_prescription","header":"[电子处方] XX市互联网医院","dept":"内科","items":["阿莫西林胶囊 0.5g×24粒","布洛芬缓释胶囊 0.3g×12粒"],"usage":"阿莫西林 0.5g tid po\n布洛芬 0.3g prn po","doctor":"王建国 主治医师","rx_no":"RX20250315001"},
    {"cat":"e_prescription","header":"[电子处方] XX省人民医院远程医疗","dept":"心内科","items":["硝苯地平控释片 30mg×7片","阿托伐他汀钙片 20mg×7片"],"usage":"硝苯地平 30mg qd\n阿托伐他汀 20mg qn","doctor":"李明远 副主任医师","rx_no":"RX20250412003"},
    {"cat":"e_prescription","header":"[电子处方] XX互联网医疗平台","dept":"皮肤科","items":["氯雷他定片 10mg×6片","地奈德乳膏 15g×1支"],"usage":"氯雷他定 10mg qd po\n地奈德乳膏 外用 bid","doctor":"张秀英 主治医师","rx_no":"RX20250520007"},
    {"cat":"e_prescription","header":"[电子处方] XX市第一医院在线问诊","dept":"消化内科","items":["奥美拉唑胶囊 20mg×14粒","多潘立酮片 10mg×30片"],"usage":"奥美拉唑 20mg qd po\n多潘立酮 10mg tid ac","doctor":"陈志强 副主任医师","rx_no":"RX20250601012"},
    {"cat":"e_prescription","header":"[电子处方] XX中医互联网医院","dept":"中医内科","items":["黄芪 15g","当归 10g","白术 12g","茯苓 15g","甘草 6g"],"usage":"水煎服，日一剂","doctor":"刘桂芳 主任中医师","rx_no":"RX20250708005"},
]

# 医保处方模板（带医保标识）
MEDICAL_INSURANCE = [
    {"cat":"insurance","header":"XX市医保定点医院处方","dept":"内科","items":["二甲双胍缓释片 0.5g×60片","格列美脲片 2mg×30片","阿托伐他汀钙片 20mg×30片"],"usage":"二甲双胍 0.5g bid\n格列美脲 2mg qd\n阿托伐他汀 20mg qn","insurance":"医保甲类","card":"YB202500123456"},
    {"cat":"insurance","header":"XX区医保处方笺","dept":"心内科","items":["氯吡格雷片 75mg×30片","美托洛尔缓释片 47.5mg×30片"],"usage":"氯吡格雷 75mg qd\n美托洛尔 47.5mg qd","insurance":"医保乙类","card":"YB202500234567"},
    {"cat":"insurance","header":"XX省医保定点社区卫生中心","dept":"全科","items":["硝苯地平缓释片 10mg×30片","二甲双胍缓释片 0.5g×30片"],"usage":"硝苯地平 10mg bid\n二甲双胍 0.5g bid","insurance":"医保甲类","card":"YB202500345678"},
    {"cat":"insurance","header":"XX市职工医保处方","dept":"呼吸内科","items":["阿莫西林克拉维酸钾片 0.375g×18片","氨溴索片 30mg×20片"],"usage":"阿莫西林克拉维酸 0.375g tid\n氨溴索 30mg tid","insurance":"医保甲类","card":"YB202500456789"},
    {"cat":"insurance","header":"XX医保门诊处方","dept":"神经内科","items":["左乙拉西坦片 0.5g×60片","丙戊酸钠缓释片 0.5g×30片"],"usage":"左乙拉西坦 0.5g bid\n丙戊酸钠 0.5g bid","insurance":"医保乙类","card":"YB202500567890"},
]

# 涂改处方（有划线修正）
CORRECTION_TEMPLATES = [
    {"cat":"correction","header":"XX医院处方笺","dept":"内科","items":["阿莫西林胶囊 0.5g×24粒","~~头孢克洛胶囊~~ 阿奇霉素片 0.25g×6片"],"usage":"阿莫西林 0.5g tid po\n阿奇霉素 0.25g qd po（3天）","note":"患者头孢过敏，改为阿奇霉素"},
    {"cat":"correction","header":"XX区医院处方","dept":"心内科","items":["~~硝苯地平片 10mg~~ 氨氯地平片 5mg×14片","阿托伐他汀钙片 20mg×7片"],"usage":"氨氯地平 5mg qd\n阿托伐他汀 20mg qn","note":"硝苯地平改为氨氯地平"},
    {"cat":"correction","header":"XX社区卫生中心处方","dept":"全科","items":["二甲双胍缓释片 0.5g×30片","~~格列本脲片 2.5mg~~ 格列美脲片 2mg×30片"],"usage":"二甲双胍 0.5g bid\n格列美脲 2mg qd","note":"低血糖风险，更换磺脲类药物"},
]

# 带检验报告的处方
LAB_TEMPLATES = [
    {"cat":"lab_prescription","header":"XX医院检验处方","dept":"内科","items":["血常规+CRP","肝功能+肾功能","空腹血糖+糖化血红蛋白","血脂四项"],"usage":"检验申请\n空腹采血","lab_no":"LAB20250315001"},
    {"cat":"lab_prescription","header":"XX医院检验申请单","dept":"心内科","items":["心肌酶谱","肌钙蛋白I","BNP","凝血功能"],"usage":"急诊检验\n需立即采血","lab_no":"LAB20250412003"},
    {"cat":"lab_prescription","header":"XX医院检验处方","dept":"消化内科","items":["肝功能全套","乙肝五项","丙肝抗体","腹部B超"],"usage":"检验申请\n空腹","lab_no":"LAB20250520007"},
    {"cat":"lab_prescription","header":"XX医院检验申请","dept":"内分泌科","items":["甲状腺功能五项","甲状腺抗体","甲状腺B超"],"usage":"检验申请","lab_no":"LAB20250601012"},
    {"cat":"lab_prescription","header":"XX医院检验处方","dept":"肾内科","items":["尿常规+沉渣","24小时尿蛋白","肾功能","肾脏B超"],"usage":"检验申请\n需留取24小时尿","lab_no":"LAB20250708005"},
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
    if t.get("doctor"):
        lines.append(f"医师：{t['doctor']}")
    if t.get("rx_no"):
        lines.append(f"处方号：{t['rx_no']}")
    if t.get("insurance"):
        lines.append(f"医保类型：{t['insurance']}　医保卡号：{t['card']}")
    if t.get("lab_no"):
        lines.append(f"检验单号：{t['lab_no']}")
    lines.append("Rp:")
    for j, item in enumerate(t["items"]):
        lines.append(f"  {j+1}. {item}")
    lines.append(f"用法：{t['usage']}")
    if t.get("note"):
        lines.append(f"备注：{t['note']}")
    return lines

def gen_img(lines, w, h, diff, noise, rotate=False, stamp=False, lowres=False, yellow=False, blur=False, crossed=False):
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
            a_val = random.randint(40, 100)
            c = (a_val, a_val, a_val)
        elif diff == "medium":
            xo, yo = random.randint(-1,1), random.randint(-1,1)
            c = (random.randint(0,30), random.randint(0,30), random.randint(0,30))
        else:
            xo, yo = 0, 0
            c = (0, 0, 0)
        
        # Draw strikethrough for corrections
        if crossed and "~~" in line:
            parts = line.split("~~")
            x_pos = 25 + xo
            for i, part in enumerate(parts):
                draw.text((x_pos, y+yo), part, fill=c, font=font)
                bbox = draw.textbbox((x_pos, y+yo), part, font=font)
                x_pos = bbox[2]
                if i % 2 == 0 and i < len(parts) - 1:  # Strikethrough the crossed part
                    draw.line([(25+xo, y+yo+8), (x_pos, y+yo+8)], fill=(200, 0, 0), width=2)
        else:
            draw.text((25+xo, y+yo), line, fill=c, font=font)
        
        y += random.randint(24, 32) if diff == "hard" else 28
    
    if noise > 0:
        np.random.seed(hash(str(lines)[:50]) % 2**32)
        n_arr = np.random.normal(0, noise, (h, w, 3))
        arr = np.clip(np.array(img).astype(np.float32) + n_arr, 0, 255).astype(np.uint8)
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
    
    os.makedirs(os.path.join(BASE, "e_prescription"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "insurance"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "correction"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "lab_prescription"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "variants2"), exist_ok=True)
    
    idx = 4000
    
    # 1. 电子处方 (80)
    print("E-prescriptions...")
    for i in range(80):
        t = E_PRESCRIPTION[i % len(E_PRESCRIPTION)]
        n, g, a, m, d = gen_patient(idx+i)
        diff = ["easy","medium","hard"][i%3]
        noise = [0, 10, 25][i%3]
        lines = make_text(t, n, g, a, m, d)
        fname = f"e_prescription/ep_{i:04d}.png"
        img = gen_img(lines, 900, 600, diff, noise, stamp=(i%4==0), rotate=(i%5==0))
        fields = {"hospital":t["header"],"department":t["dept"],"patient_name":n,"gender":g,"age":str(a),"date":f"2025年{m}月{d}日","prescription_items":t["items"],"usage":t["usage"],"doctor":t.get("doctor",""),"rx_no":t.get("rx_no","")}
        img.save(os.path.join(BASE, fname))
        ann[fname] = {"category":"e_prescription","source":"synthetic","text_full":"\n".join(lines),"fields":fields,"difficulty":diff}
        idx += 1
    
    # 2. 医保处方 (80)
    print("Insurance prescriptions...")
    for i in range(80):
        t = MEDICAL_INSURANCE[i % len(MEDICAL_INSURANCE)]
        n, g, a, m, d = gen_patient(idx+i)
        diff = ["easy","medium","hard"][i%3]
        noise = [0, 10, 25][i%3]
        lines = make_text(t, n, g, a, m, d)
        fname = f"insurance/ins_{i:04d}.png"
        img = gen_img(lines, 850, 600, diff, noise, stamp=(i%3==0), rotate=(i%4==0))
        fields = {"hospital":t["header"],"department":t["dept"],"patient_name":n,"gender":g,"age":str(a),"date":f"2025年{m}月{d}日","prescription_items":t["items"],"usage":t["usage"],"insurance":t.get("insurance",""),"card":t.get("card","")}
        img.save(os.path.join(BASE, fname))
        ann[fname] = {"category":"insurance","source":"synthetic","text_full":"\n".join(lines),"fields":fields,"difficulty":diff}
        idx += 1
    
    # 3. 涂改处方 (60)
    print("Correction prescriptions...")
    for i in range(60):
        t = CORRECTION_TEMPLATES[i % len(CORRECTION_TEMPLATES)]
        n, g, a, m, d = gen_patient(idx+i)
        diff = "hard"
        noise = random.randint(20, 35)
        lines = make_text(t, n, g, a, m, d)
        fname = f"correction/cr_{i:04d}.png"
        img = gen_img(lines, 850, 600, diff, noise, crossed=True, stamp=(i%3==0), rotate=(i%4==0))
        fields = {"hospital":t["header"],"department":t["dept"],"patient_name":n,"gender":g,"age":str(a),"date":f"2025年{m}月{d}日","prescription_items":t["items"],"usage":t["usage"]}
        img.save(os.path.join(BASE, fname))
        ann[fname] = {"category":"correction","source":"synthetic","text_full":"\n".join(lines),"fields":fields,"difficulty":diff,"note":"Contains strikethrough corrections"}
        idx += 1
    
    # 4. 检验处方 (60)
    print("Lab prescriptions...")
    for i in range(60):
        t = LAB_TEMPLATES[i % len(LAB_TEMPLATES)]
        n, g, a, m, d = gen_patient(idx+i)
        diff = ["easy","medium","hard"][i%3]
        noise = [0, 10, 25][i%3]
        lines = make_text(t, n, g, a, m, d)
        fname = f"lab_prescription/lp_{i:04d}.png"
        img = gen_img(lines, 900, 650, diff, noise, stamp=(i%4==0))
        fields = {"hospital":t["header"],"department":t["dept"],"patient_name":n,"gender":g,"age":str(a),"date":f"2025年{m}月{d}日","prescription_items":t["items"],"usage":t["usage"],"lab_no":t.get("lab_no","")}
        img.save(os.path.join(BASE, fname))
        ann[fname] = {"category":"lab_prescription","source":"synthetic","text_full":"\n".join(lines),"fields":fields,"difficulty":diff}
        idx += 1
    
    # 5. 更多变体 (280)
    print("More variants...")
    all_tmpls = E_PRESCRIPTION + MEDICAL_INSURANCE + CORRECTION_TEMPLATES + LAB_TEMPLATES
    variant_combos = [
        ("easy", 0, False, False, False, False, False, 800, 550),
        ("easy", 5, False, True, False, False, False, 800, 550),
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
        ("easy", 0, False, False, False, False, False, 900, 500),
        ("hard", 40, True, True, False, False, True, 800, 600),
    ]
    
    for i in range(280):
        t = all_tmpls[i % len(all_tmpls)]
        n, g, a, m, d = gen_patient(idx+i)
        v = variant_combos[i % len(variant_combos)]
        diff, noise, rot, stamp, lowres, yellow, blur, w, h = v
        lines = make_text(t, n, g, a, m, d)
        fname = f"variants2/v2_{i:04d}.png"
        img = gen_img(lines, w, h, diff, noise, rot, stamp, lowres, yellow, blur)
        img.save(os.path.join(BASE, fname))
        fields = {"hospital":t["header"],"department":t["dept"],"patient_name":n,"gender":g,"age":str(a),"date":f"2025年{m}月{d}日","prescription_items":t["items"],"usage":t["usage"]}
        note_parts = []
        if lowres: note_parts.append("low resolution")
        if yellow: note_parts.append("yellowed paper")
        if blur: note_parts.append("motion blur")
        ann[fname] = {"category":t.get("cat","variants"),"source":"synthetic_variant","text_full":"\n".join(lines),"fields":fields,"difficulty":diff}
        if note_parts:
            ann[fname]["note"] = "; ".join(note_parts)
        idx += 1
    
    with open(os.path.join(BASE, "annotations.json"), "w", encoding="utf-8") as f:
        json.dump(ann, f, indent=2, ensure_ascii=False)
    
    total = len(ann)
    complete = len([v for v in ann.values() if v.get("text_full") and "待人工" not in v.get("text_full", "")])
    cats = {}
    for v in ann.values():
        cats[v["category"]] = cats.get(v["category"], 0) + 1
    
    print(f"\n=== Phase 5 Complete ===")
    print(f"Total: {total}")
    print(f"Complete: {complete}")
    print(f"Categories: {cats}")

if __name__ == "__main__":
    main()
