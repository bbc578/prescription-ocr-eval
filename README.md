# Chinese Medical Prescription OCR Evaluation Dataset

## 中文医疗处方 OCR 评估数据集

[English](#overview) | [中文](#概述)

---

## Overview

This is an evaluation dataset for **Chinese medical prescription OCR** (Optical Character Recognition). It contains images of both Traditional Chinese Medicine (TCM) prescriptions and Western medicine prescriptions, with ground-truth text annotations.

**Why this dataset?** Chinese medical prescriptions are a high-value OCR scenario with real industry demand (hospital digitization, pharmacy automation, medical record management). However, no publicly available benchmark dataset exists for this domain. Existing OCR datasets focus on general documents, receipts, or forms — none specifically target the unique challenges of medical prescriptions: specialized medical terminology, mixed printed/handwritten content, complex layout structures, and domain-specific abbreviations.

## Dataset Statistics

| Category | Count | Source | Difficulty |
|----------|-------|--------|------------|
| TCM prescriptions (中药处方) | 32 | Synthetic + Web | Medium |
| Western medicine prescriptions (西药处方) | 31 | Synthetic + Web | Medium |
| Handwritten prescriptions (手写处方) | 1 | Web | Hard |
| **Total** | **64** | | |

## Directory Structure

```
prescription-ocr-eval/
├── README.md                    # This file
├── images/
│   ├── tcm/                     # TCM prescription images
│   │   ├── tc_synth_000.png     # Synthetic (auto-annotated)
│   │   ├── tc_0564769c.jpg      # Web-collected (manual annotation needed)
│   │   └── ...
│   ├── western/                 # Western medicine prescription images
│   │   ├── we_synth_000.png     # Synthetic (auto-annotated)
│   │   └── ...
│   ├── handwritten/             # Handwritten prescriptions
│   │   └── ...
│   └── annotations.json         # Ground-truth annotations
├── scripts/
│   ├── download_images.py       # Image collection script
│   └── generate_annotations.py  # Annotation generation script
└── docs/
    └── annotation_guidelines.md # Annotation standards
```

## Annotation Format

Each image in `annotations.json` has the following structure:

```json
{
  "tcm/tc_synth_000.png": {
    "category": "tcm",
    "source": "synthetic",
    "text_full": "XX中医院处方笺\n姓名：张三　性别：男　年龄：45岁...",
    "fields": {
      "hospital": "XX中医院处方笺",
      "department": "中医内科",
      "patient_name": "张三",
      "gender": "男",
      "age": "45",
      "date": "2025年3月15日",
      "prescription_items": ["黄芪 15g", "当归 10g", ...],
      "usage": "水煎服，日一剂"
    },
    "difficulty": "medium"
  }
}
```

### Fields Description

- `category`: Image category (`tcm`, `western`, `handwritten`)
- `source`: Data source (`synthetic` for generated images, `web` for real-world images)
- `text_full`: Full text content of the prescription (ground truth for OCR evaluation)
- `fields`: Structured key-value pairs for information extraction evaluation
  - `hospital`: Hospital/clinic name on the prescription header
  - `department`: Medical department
  - `patient_name`: Patient name
  - `gender`: Patient gender
  - `age`: Patient age
  - `date`: Prescription date
  - `prescription_items`: List of prescribed medicines with dosage
  - `usage`: Medication instructions
- `difficulty`: Annotation difficulty level (`easy`, `medium`, `hard`)

## Evaluation Protocol

This dataset supports two evaluation modes:

### 1. Full-Text OCR Evaluation
Compare the OCR output against `text_full` using standard metrics:
- **Character Error Rate (CER)**: Levenshtein distance at character level
- **Word Error Rate (WER)**: Levenshtein distance at word level
- **Exact Match Rate**: Percentage of images with perfect OCR

### 2. Structured Information Extraction Evaluation
Compare extracted key-value pairs against `fields` using:
- **Field-level F1**: Precision, recall, F1 for each field type
- **Item-level accuracy**: For `prescription_items`, check if all items are correctly extracted

## Challenges Specific to Medical Prescriptions

1. **Specialized vocabulary**: TCM herb names (黄芪, 当归, 白术), drug names (阿莫西林, 奥美拉唑), medical abbreviations (tid, qd, po, prn)
2. **Mixed content**: Printed headers with handwritten additions
3. **Complex layout**: Multi-column prescription items, dosage information, usage instructions
4. **Noise and degradation**: Real prescriptions may have stains, folds, or low-quality printing
5. **Similar characters**: Many Chinese medicine names share similar radicals (e.g., 芪/芪, 术/木)

## Usage

```python
import json

with open("images/annotations.json", "r", encoding="utf-8") as f:
    annotations = json.load(f)

for image_path, meta in annotations.items():
    print(f"Image: {image_path}")
    print(f"  Category: {meta['category']}")
    print(f"  Ground truth: {meta['text_full'][:100]}...")
```

## License

This dataset is released under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
- Synthetic images: Generated programmatically, free to use
- Web-collected images: Sourced from publicly available references, used for research purposes only

## Citation

If you use this dataset, please cite:
```
@dataset{prescription_ocr_eval_2026,
  title={Chinese Medical Prescription OCR Evaluation Dataset},
  author={Yihao Tang},
  year={2026},
  url={https://github.com/bbc578/prescription-ocr-eval}
}
```

## Contact

For questions or contributions, please open an issue on GitHub or contact tangyh@mail2.sysu.edu.cn.
