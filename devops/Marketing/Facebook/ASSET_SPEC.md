# CKM — Facebook Visual & Media Asset Specification (素材規範)

本規格定義 CKM 在 Facebook 平台的所有視覺圖卡、排版與生圖 Prompt 標準。

---

## 1. 影像尺寸與比例標準

| 項目 | 規範標準 | 備註說明 |
| :--- | :--- | :--- |
| **標準比例** | **1:1 (1080 × 1080 px) 或 4:5 (1080 × 1350 px) 奢華美食攝影** | 符合 Meta 演算法最佳全螢幕展示比例 |
| **色彩體系** | **奢華暗金黑底 (#0B0F19 / #1A1F2C) 搭配自然暖光與金黃琥珀色** | 頂級粵菜外燴宴席質感，杜絕廉價感 |
| **文字政策** | **100% NO TEXT（純視覺攝影，零文字、零水印、零促銷字眼）** | 杜絕 Meta OCR 廣告降權，防止高棉文排版破碎 |
| **元數據脫敏** | **強制通過 `Tools/image_cleaner.py` 清洗所有 C2PA / EXIF / IPTC** | **杜絕 Meta 自動掛上 AI 標籤，保護 100% 自然觸及率** |
| **輸出格式** | 產出脫敏完成之純淨圖檔至 `Downloads/`，供 Owner 直接發布 | 節省 API 成本，維持最高畫質 |

---

## 2. 視覺排版架構 (Layout Blueprint)

- **主體**：星級大廚現場分切頂級吉品鮑魚、熱氣蒸騰的花膠濃湯、五星級私宴長桌燭光布場。
- **氛圍**：極致微距景深（Macro Depth of Field）、米其林星級擺盤、高級宴會光影質感。
- **禁止**：任何文字、任何宣傳字眼、任何英文或中文標籤。

---

## 3. 專屬生圖 Prompt 範例模板 (100% No Text Policy)

```text
Cinematic culinary photography of luxury Cantonese banquet catering in Phnom Penh, South African dried abalone braised in rich golden broth, steaming hot, plated on fine dark ceramic dinnerware, Michelin-star presentation, soft warm ambient lighting, elegant banquet setting in background with bokeh, 8k resolution, photorealistic, shot on Hasselblad, --no text, watermark, logos, letters, words
```
