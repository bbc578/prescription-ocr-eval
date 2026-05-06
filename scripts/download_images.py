#!/usr/bin/env python3
"""Download Chinese medical prescription images using multiple search strategies."""
import os, json, time, hashlib, requests, re
from urllib.parse import quote

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

def search_and_download_bing(query, save_dir, prefix, max_count=10):
    """Search Bing images and download results."""
    url = f"https://www.bing.com/images/search?q={quote(query)}&first=1&count={max_count}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        text = resp.text
        
        # Try multiple URL patterns
        urls = []
        # Pattern 1: murl in JSON
        urls += re.findall(r'"murl"\s*:\s*"(https?://[^"]+)"', text)
        # Pattern 2: src attributes with image extensions
        urls += re.findall(r'src="(https?://[^"]+\.(?:jpg|jpeg|png|webp))"', text)
        # Pattern 3: data-src
        urls += re.findall(r'data-src="(https?://[^"]+\.(?:jpg|jpeg|png|webp))"', text)
        # Pattern 4: any image URL in the response
        urls += re.findall(r'(https?://[^"<>\s]+\.(?:jpg|jpeg|png|webp))', text)
        
        # Deduplicate while preserving order
        seen = set()
        unique_urls = []
        for u in urls:
            if u not in seen and len(u) > 30:
                seen.add(u)
                unique_urls.append(u)
        
        downloaded = []
        for img_url in unique_urls[:max_count]:
            fname = download_image(img_url, save_dir, prefix)
            if fname:
                downloaded.append(fname)
            time.sleep(0.2)
        return downloaded
    except Exception as e:
        print(f"  Error: {e}")
        return []

def search_unsplash_placeholder(query, save_dir, prefix, max_count=10):
    """Use placeholder medical images from unsplash/pexels as fallback."""
    # This is a fallback - we'll use programmatically generated images instead
    return []

def download_image(url, save_dir, prefix):
    """Download an image."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, stream=True)
        if resp.status_code != 200:
            return None
        
        data = resp.content
        if len(data) < 5000:
            return None
        
        # Check if it's actually an image
        if data[:3] == b'\xff\xd8\xff' or data[:8] == b'\x89PNG\r\n\x1a\n' or data[:4] == b'RIFF':
            ext = ".png" if data[:8] == b'\x89PNG\r\n\x1a\n' else ".jpg"
            filename = f"{prefix}_{hashlib.md5(url.encode()).hexdigest()[:8]}{ext}"
            filepath = os.path.join(save_dir, filename)
            with open(filepath, "wb") as f:
                f.write(data)
            return filename
        return None
    except:
        return None

def generate_synthetic_prescriptions(save_dir, count=30):
    """Generate synthetic prescription images using PIL."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        os.system("pip3.10 install Pillow -q")
        from PIL import Image, ImageDraw, ImageFont
    
    # Chinese prescription templates
    tcm_templates = [
        {"header": "XX中医院处方笺", "dept": "中医内科", "items": ["黄芪 15g", "当归 10g", "白术 12g", "茯苓 15g", "甘草 6g"], "usage": "水煎服，日一剂"},
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
    
    generated = []
    
    # Try to find a Chinese font
    font_path = None
    for fp in ["/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
               "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
               "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
               "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"]:
        if os.path.exists(fp):
            font_path = fp
            break
    
    if not font_path:
        # Install a Chinese font
        os.system("apt-get install -y fonts-wqy-zenhei 2>/dev/null || true")
        for fp in ["/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
                   "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"]:
            if os.path.exists(fp):
                font_path = fp
                break
    
    all_templates = [(t, "tcm") for t in tcm_templates] + [(t, "western") for t in western_templates]
    
    for i in range(count):
        template, category = all_templates[i % len(all_templates)]
        prefix = "tc" if category == "tcm" else "we"
        
        # Create image
        img = Image.new("RGB", (800, 600), "#FFFFF0")
        draw = ImageDraw.Draw(img)
        
        try:
            font_title = ImageFont.truetype(font_path, 28) if font_path else ImageFont.load_default()
            font_body = ImageFont.truetype(font_path, 20) if font_path else ImageFont.load_default()
            font_small = ImageFont.truetype(font_path, 16) if font_path else ImageFont.load_default()
        except:
            font_title = font_body = font_small = ImageFont.load_default()
        
        # Add slight rotation/variation for realism
        import random
        random.seed(i)
        
        y = 30
        # Header
        draw.text((200, y), template["header"], fill="black", font=font_title)
        y += 50
        
        # Horizontal line
        draw.line([(30, y), (770, y)], fill="black", width=2)
        y += 15
        
        # Patient info (fake)
        name = random.choice(["张三", "李四", "王五", "赵六", "陈七", "刘八"])
        gender = random.choice(["男", "女"])
        age = random.randint(25, 75)
        date = f"2025年{random.randint(1,12)}月{random.randint(1,28)}日"
        
        draw.text((40, y), f"姓名：{name}　性别：{gender}　年龄：{age}岁　日期：{date}", fill="black", font=font_body)
        y += 35
        draw.text((40, y), f"科室：{template['dept']}　门诊号：{random.randint(10000,99999)}", fill="black", font=font_body)
        y += 40
        
        # Rx symbol
        draw.text((40, y), "Rp:", fill="black", font=font_title)
        y += 40
        
        # Prescription items
        for j, item in enumerate(template["items"]):
            x_offset = 60 + random.randint(-5, 5)
            draw.text((x_offset, y), f"{j+1}. {item}", fill="black", font=font_body)
            y += 35
        
        y += 15
        draw.line([(30, y), (770, y)], fill="black", width=1)
        y += 15
        
        # Usage
        draw.text((40, y), f"用法：{template['usage']}", fill="black", font=font_body)
        y += 40
        
        # Doctor signature area
        draw.text((550, y), "医师：_______", fill="black", font=font_body)
        y += 30
        draw.text((550, y), "审核：_______", fill="black", font=font_body)
        
        # Add some noise/aging effect
        for _ in range(random.randint(5, 20)):
            x = random.randint(0, 799)
            y_noise = random.randint(0, 599)
            draw.point((x, y_noise), fill=(200, 200, 200))
        
        filename = f"{prefix}_synth_{i:03d}.png"
        filepath = os.path.join(save_dir, filename)
        img.save(filepath)
        generated.append(filename)
    
    return generated

def main():
    base_dir = "/root/prescription-ocr-eval/images"
    stats = {"tcm": 0, "western": 0, "handwritten": 0}
    all_files = {"tcm": [], "western": [], "handwritten": []}
    
    queries = {
        "tcm": ["中药处方 图片", "中医处方笺 实拍", "中药方剂 处方单", "中药饮片 处方"],
        "western": ["医院处方单 图片", "西药处方笺", "门诊处方 样本", "医院处方 打印"],
        "handwritten": ["手写处方 中医", "医生手写药方", "老中医处方", "手写处方笺"],
    }
    
    # Try downloading from Bing first
    for category, qlist in queries.items():
        save_dir = os.path.join(base_dir, category)
        print(f"\n=== Downloading {category} ===")
        for query in qlist:
            print(f"  Searching: {query}")
            downloaded = search_and_download_bing(query, save_dir, category[:2], max_count=8)
            all_files[category].extend(downloaded)
            stats[category] += len(downloaded)
            print(f"  Got {len(downloaded)} images (total: {stats[category]})")
            if stats[category] >= 30:
                break
    
    # Generate synthetic images to fill gaps
    print("\n=== Generating synthetic prescriptions ===")
    for category in ["tcm", "western"]:
        save_dir = os.path.join(base_dir, category)
        needed = max(0, 30 - stats[category])
        if needed > 0:
            print(f"  Generating {needed} {category} images...")
            generated = generate_synthetic_prescriptions(save_dir, count=needed)
            all_files[category].extend(generated)
            stats[category] += len(generated)
    
    # Save manifest
    manifest = {}
    for category, files in all_files.items():
        for f in files:
            manifest[f] = {"category": category, "source": "synthetic" if "synth" in f else "web"}
    
    with open(os.path.join(base_dir, "manifest.json"), "w") as fp:
        json.dump(manifest, fp, indent=2, ensure_ascii=False)
    
    print(f"\n=== Summary ===")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print(f"  Total: {sum(stats.values())}")

if __name__ == "__main__":
    main()
