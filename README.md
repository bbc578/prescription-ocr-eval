# 医疗处方 OCR 评估集

## 项目简介

本数据集是一个面向**医疗处方文字识别**场景的高质量评估集，用于评测 OCR 模型在医疗处方文档上的识别能力。

**选题理由**：医疗处方是 OCR 领域的稀缺场景，公开 benchmark 几乎为零，但医院数字化转型有真实刚需。处方包含专业医学术语、特殊格式（Rp:）、中西医混合排版，对 OCR 模型提出独特挑战。

## 数据集统计

| 指标 | 数值 |
|------|------|
| 总图片数 | 674 |
| 已标注 | 670 |
| 待人工标注 | 4（网络下载实拍图） |
| 处方类型 | 10（中药/西药/中西结合/手写/住院/急诊/颗粒/特殊/中药扩展/西药扩展） |
| 覆盖科室 | 57 |
| 难度分布 | Easy: 168 / Medium: 268 / Hard: 238 |

## 目录结构

```
prescription-ocr-eval/
├── README.md                    # 本文件
├── images/
│   ├── annotations.json         # 标注文件（核心）
│   ├── tcm/                     # 中药处方图片 (182张)
│   ├── western/                 # 西药处方图片 (181张)
│   ├── handwritten/             # 手写风格处方 (51张)
│   ├── mixed/                   # 中西医结合处方 (50张)
│   ├── inpatient/               # 住院处方 (60张)
│   ├── emergency/               # 急诊处方 (40张)
│   ├── granule/                 # 中药配方颗粒 (40张)
│   └── special/                 # 特殊处方 (70张)
├── scripts/
│   ├── expand_dataset.py        # 数据集生成脚本
│   ├── generate_annotations.py  # 标注生成脚本
│   └── download_images.py       # 网络图片下载脚本
└── docs/
    └── annotation_guide.md      # 标注规范文档
```

## 标注格式

每张图片在 `annotations.json` 中有对应条目，格式如下：

```json
{
  "images/tcm/tc_0000.png": {
    "category": "tcm",           // 类别: tcm/western/mixed/handwritten
    "source": "synthetic",        // 来源: synthetic/web
    "text_full": "XX省中医院处方笺\n姓名：张三...",  // 完整文字
    "fields": {
      "hospital": "XX省中医院处方笺",
      "department": "中医内科",
      "patient_name": "张三",
      "gender": "男",
      "age": "41",
      "date": "2025年11月8日",
      "prescription_items": ["黄芪 15g", "当归 10g", ...],
      "usage": "水煎服，日一剂"
    },
    "difficulty": "medium"        // 难度: easy/medium/hard
  }
}
```

## 场景覆盖

### 中药处方（28 科室）
中医内科、针灸推拿科、中医外科、妇科、儿科、皮肤科、骨伤科、肛肠科、耳鼻喉科、眼科、肿瘤科、全科、肾病科、脾胃科、肺病科、心病科、肝病科、脑病科、风湿科、内分泌科、男科、治未病科、推拿科、糖尿病科、甲状腺科、乳腺科、血液科、中医泌尿科

### 西药处方（23 科室）
内科、呼吸内科、消化内科、心内科、神经内科、皮肤科、骨科、妇产科、泌尿外科、眼科、耳鼻喉科、口腔科、儿科、急诊科、全科、风湿免疫科、血液科、内分泌科、肾内科、胸外科、感染科、变态反应科、全科门诊

### 住院处方（6 科室）
心内科、神经外科、骨科、呼吸内科、产科、新生儿科

### 急诊处方（4 科室）
急诊科、急诊外科、急诊内科、急诊ICU

### 中药配方颗粒（4 科室）
中医内科、脾胃科、全科、妇科

### 特殊处方（7 科室）
精神科、皮肤科、肿瘤内科、麻醉科、康复科、营养科、疼痛科

### 难度等级
- **Easy**（168张）：白色背景，标准字体，清晰排版
- **Medium**（268张）：轻微噪点，模拟打印质量波动
- **Hard**（238张）：明显噪点，模拟实拍条件（纸张泛黄、字迹模糊、手写风格、轻微旋转）

## 使用方法

### 加载数据
```python
import json

with open("images/annotations.json", "r", encoding="utf-8") as f:
    annotations = json.load(f)

# 遍历所有标注
for image_path, info in annotations.items():
    print(f"{image_path}: {info['category']} ({info['difficulty']})")
```

### 评估 OCR 模型
```python
from difflib import SequenceMatcher

def char_accuracy(pred, gt):
    return SequenceMatcher(None, pred, gt).ratio()

# 对每张图片计算字符级准确率
for image_path, info in annotations.items():
    gt_text = info["text_full"]
    # pred_text = your_ocr_model.predict(image_path)
    # accuracy = char_accuracy(pred_text, gt_text)
```

## 数据特点

1. **稀缺场景**：医疗处方 OCR 公开 benchmark 几乎为零
2. **专业术语**：包含中药名（黄芪、当归）、西药名（阿莫西林、奥美拉唑）、医学缩写（tid、po、qd）
3. **结构化格式**：医院名、患者信息、Rp: 标记、药品列表、用法说明
4. **中西医覆盖**：中药处方、西药处方、中西医结合处方
5. **多难度梯度**：从清晰打印到模拟手写，覆盖不同真实场景
6. **结构化标注**：除全文外，还提供字段级标注（医院、科室、药品等）

## 致谢

本评估集为 PaddleOCR 全球衍生模型挑战赛（第十届飞桨黑客马拉松）参赛作品。

## 许可证

本数据集仅供学术研究和竞赛使用，不得用于商业用途。
