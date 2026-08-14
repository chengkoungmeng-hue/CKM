# CKM 部落格配圖 — 生成 Prompt（15 篇）

給 Gemini / Nano Banana 使用。所有 prompt 為英文（影像模型對英文理解較準），說明為中文。

---

## 一、規格

| 用途 | 現況 | 建議生成 | 存放位置 | 檔名 |
| :--- | :--- | :--- | :--- | :--- |
| 內文圖 | 1024×1024 WebP | **1600×900（16:9）** | `public/images/` | `blog_NN_inline_khmer.webp` |
| 封面圖 | PNG ~0.9 MB | **1600×900（16:9）** | `src/assets/grounded_images/` | `ckm_blog_NN.png` |

**為什麼改 16:9**：版面用 `aspect-[16/9] object-cover` 顯示，目前的正方形圖上下各被裁掉約 28%，構圖重心常常被切掉。直接出 16:9 就不會被裁。

**13、14、15 篇目前完全沒有內文圖**（`blog_13/14/15_inline_khmer.webp` 不存在），優先補這三張。

---

## 二、共用風格區塊

**每一則 prompt 後面都接這一段**，確保 15 張看起來像同一組：

```
STYLE: Photorealistic editorial food photography, shot on a full-frame camera with a
35mm or 50mm lens, natural daylight or warm tungsten, shallow depth of field.
Muted "quiet luxury" palette — deep charcoal blacks, warm champagne gold highlights,
soft off-white. Restrained and elegant, never garish or oversaturated.
SETTING: Cambodia, Phnom Penh. All people must be Cambodian (Khmer).
NEGATIVE: no text, no lettering, no signage, no logos, no watermarks, no captions,
no distorted hands, no extra fingers, no plastic-looking food, no Western banquet
styling, no Japanese or Thai styling, no stock-photo smiles at camera.
ASPECT RATIO: 16:9
```

> **關鍵**：一定要加 `no text`。影像模型寫高棉文一定是亂碼，而網站主要讀者就是高棉語使用者 —— 圖上出現假高棉字會立刻穿幫。

---

## 三、15 篇 Prompt

### 01 — 八道菜傳統菜單
> 主題：整桌八道菜的全貌

```
Overhead flat-lay of a full Khmer-Chinese wedding banquet round table set for ten
guests. Eight distinct dishes arranged across the table: a cold appetizer platter,
a whole crispy roast suckling pig, cereal-butter prawns, a whole steamed fish in
soy sauce, a dark herbal soup in a lidded tureen, lotus-leaf wrapped rice parcels,
and a traditional Khmer coconut dessert. White tablecloth, gold-rimmed porcelain,
small glasses of tea. Warm overhead light.
```

### 02 — 價格與預算規劃
> 主題：籌備與討論的場景，不是食物

```
A Cambodian couple in their late twenties sitting at a table with an older Khmer
catering manager, reviewing a printed menu and a notebook. Blank paper, no visible
writing. Two sample dishes on the table beside them. Afternoon light through a
window. Calm, professional, consultative mood. Shot from a slight side angle,
faces partly turned away.
```

### 03 — 試菜
> 主題：小份量試吃，不是正式宴席

```
An intimate food tasting session: four small portions of Khmer-Chinese banquet
dishes plated individually on white porcelain, arranged on a dark wooden table.
A Cambodian couple and an older woman seated, tasting thoughtfully with chopsticks
and spoons. Natural window light from the left. Quiet, focused, evaluative mood.
```

### 04 — 衛生與溫控
> 主題：行動廚房的作業紀律

```
Interior of a professional mobile catering kitchen in Cambodia. A Khmer chef in a
clean white jacket and gloves lifting the lid of a large stainless steel holding
container, steam rising. Stacked covered food containers, clean stainless prep
surfaces, an insulated cooler beside. Bright, clinical, orderly. No clutter.
```

### 05 — 企業活動外燴
> 主題：公司場地的自助餐

```
An elegant buffet line set up inside a modern corporate office lobby in Phnom Penh.
Chafing dishes with warm lids, a long table with dark cloth and gold accents,
Cambodian office workers in business attire serving themselves. Glass windows,
contemporary interior. Late afternoon light. Professional, understated.
```

### 06 — 招牌菜（烤乳豬 + 鮑魚湯）
> 主題：招牌菜的工藝細節

```
Close-up of a whole roast suckling pig with lacquered mahogany-red crackling skin,
being carved by a Khmer chef's hands with a cleaver on a wooden board. Crisp skin
fragments visibly separating. Beside it, slightly out of focus, a dark ceramic bowl
of herbal abalone broth. Warm directional light raking across the skin texture.
```

### 07 — 新居入厝宴
> 主題：私人住宅庭院的宴席

```
A catering setup in the courtyard of a Cambodian villa in a gated residential
compound. Three round tables with white cloths and red chairs under a small white
marquee, a portable serving station to one side, a parked catering van in the
background. Late afternoon golden light, tropical plants, tiled driveway.
```

### 08 — 服務動線
> 主題：服務生的協調節奏

```
Four Cambodian waitstaff in matching dark uniforms moving in a coordinated line
through a banquet hall, each carrying a covered serving platter at shoulder height.
Motion slightly blurred to convey rhythm. Round tables with seated guests softly
out of focus in the background. Warm interior lighting.
```

### 09 — 戶外帳篷與基礎設施
> 主題：場地搭建的規模

```
A large white event marquee being assembled on an open lot in Cambodia, metal frame
partly covered, round tables stacked nearby. Behind it, a temporary outdoor kitchen
station with gas burners and large woks under a separate canopy. Cambodian crew
working. Late afternoon, dramatic sky, dry ground.
```

### 10 — 六十年廚師傳承
> 主題：老師傅的手與火

```
Close-up of an elderly Khmer master chef's weathered hands controlling a large
carbon-steel wok over a roaring open flame, ingredients mid-toss above the pan.
The chef's face partly visible, concentrated, not looking at camera. Dark kitchen
background, the fire as the main light source. Deep shadows, warm amber tones.
```

### 11 — 套餐選擇
> 主題：不同等級的對比

```
Three round banquet tables photographed in a row at a slight angle, each set to a
different tier: the first simple with plain white cloth and basic settings, the
second with gold-rimmed plates and cloth napkins, the third fully dressed with
floral centerpiece, charger plates and glassware. Neutral hall background, even
soft lighting. The progression should read clearly left to right.
```

### 12 — 產業趨勢
> 主題：傳統與現代的融合

```
A contemporary Khmer-Chinese banquet setup blending tradition and modern design:
a round table with minimalist dark ceramic tableware, a low modern floral
arrangement, warm pendant lights above, and a traditional whole steamed fish
presented as the centerpiece. Clean modern venue with concrete and wood.
Sophisticated, current, uncluttered.
```

### 13 — 總鋪師工藝
> 主題：收尾裝盤的專注

```
A Khmer head chef in a dark chef's jacket finishing a signature banquet dish,
using tweezers or a spoon to place a final garnish on a large platter. Extreme
concentration, hands steady, face angled down. Stainless prep counter, other
plated dishes waiting in soft focus behind. Single warm overhead light source.
```

### 14 — 主廚團隊
> 主題：團隊協作

```
A team of five Cambodian chefs working together in a temporary outdoor catering
kitchen, each at a different station: one at the wok, one plating, one at a
steamer stack, two prepping. Coordinated movement, matching aprons. Steam and
motion in the air. Shot wide to show the whole operation. Warm practical lighting,
dusk outside.
```

### 15 — 鮑魚湯
> 主題：單品的貴氣

```
A single elegant serving of premium abalone herbal soup in a fine dark ceramic
bowl with a gold rim, whole abalone visible in a rich amber broth with goji
berries and herbs. Steam rising. Placed on dark slate with a gold spoon beside.
Dramatic side lighting, deep shadows, luxurious and restrained. Macro detail on
the broth surface.
```

---

## 四、生成後處理

1. **轉檔壓縮**：輸出轉 WebP，目標 100–200 KB（對齊現有檔案）。
   ```bash
   python compress_images.py
   ```
   或用 `sharp` / `cwebp -q 82`。

2. **13、14、15 篇要手動加內文圖標籤**（目前沒有）。在文章中段插入：
   ```html
   <img src="/images/blog_13_inline_khmer.webp" alt="（用高棉文描述畫面內容）" class="w-full aspect-[16/9] object-cover rounded-sm my-8 shadow-md border border-slate-200" />
   ```
   `alt` 一定要寫高棉文，且描述畫面而非塞關鍵字。

3. **封面圖若也要換**，放 `src/assets/grounded_images/ckm_blog_NN.png`，Astro 會自動產生 AVIF 與 1200×630 的分享卡，不需手動處理。

---

## 五、兩點提醒

**不要把這些圖放進首頁圖庫。** 首頁 `#gallery` 的標題寫著「រូបភាពពិតៗ」（真實照片）。部落格配圖是示意用途沒問題，但放進宣稱真實照片的區塊就變成不實陳述。

**人物臉部盡量側面或低頭。** 影像模型正面人臉容易出現恐怖谷，側臉、專注工作的角度成功率高很多，也更像紀實攝影而非商業素材。
