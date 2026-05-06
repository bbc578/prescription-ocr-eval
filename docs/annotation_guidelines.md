# Annotation Guidelines / 标注规范

## General Rules

1. **Text accuracy**: Transcribe text exactly as it appears in the image. Do not correct typos or normalize characters.
2. **Line breaks**: Use `\n` to separate logical sections (header, patient info, prescription items, usage).
3. **Spacing**: Preserve original spacing within fields (e.g., full-width spaces `　` between key-value pairs).
4. **Missing fields**: If a field is not visible or illegible, use `"[不可读]"` for that field.

## Field Extraction Rules

### Hospital Name (header)
- Transcribe the full hospital/clinic name as printed on the prescription header
- Include "处方笺" or "处方" suffix if present
- Example: `XX市人民医院处方笺`

### Department
- Transcribe the department name exactly
- Common values: 内科, 外科, 中医科, 妇科, 皮肤科, 全科, 呼吸内科, 消化内科

### Patient Information
- **Name**: Transcribe exactly (may be masked with X in real prescriptions)
- **Gender**: 男 or 女
- **Age**: Number + 岁
- **Date**: Full date including year, month, day

### Prescription Items (Rp)
- List each item on a separate line
- Format: `[drug/herb name] [dosage]`
- For TCM: `黄芪 15g`, `当归 10g`
- For Western: `阿莫西林胶囊 0.5g×24粒`
- Include quantity specifications when present

### Usage Instructions
- Transcribe exactly as written
- Common abbreviations:
  - tid = three times a day
  - bid = twice a day
  - qd = once a day
  - qn = every night
  - po = per os (oral)
  - prn = as needed
  - ac = before meals

## Difficulty Levels

- **Easy**: Clear printed text, standard layout, no noise
- **Medium**: Minor noise, slight variations in font/spacing
- **Hard**: Handwritten text, significant noise, non-standard layout, partial occlusion
