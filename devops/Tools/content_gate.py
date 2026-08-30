"""發文前的機械檢查:零外鏈、AI 味、長度、帳本查重、圖文數值對齊。

為什麼是函式庫而不是選單
------------------------
前身是 `Tools/devops_copilot.py`,一支互動式選單。它的檢查邏輯是對的,但 owner 明說
不會自己去跑那支檔案——AI agent 才是實際的操作介面。一個沒有人開的選單不會被維護,
只會腐化:同一天 `devops_cli.py` 的選單裡就有一個指向已刪除檔案的項目。

所以:邏輯留下、選單刪除。agent 寫完貼文後呼叫 `check()`,把結果攤給 owner 看。

這支只做**機械上可判定**的事
----------------------------
「這段話的節奏像機器」不在這裡,那需要人讀。把不可判定的東西寫進閘門,結果是閘門
一直誤報、然後被關掉。owner 讀中文是母語,掃一眼的成本極低——機器擋掉可檢查的,
人擋掉其餘的,兩者不要互相假裝。

用法
----
    python content_gate.py --project TWProbe --platform Threads --file draft.txt
    python content_gate.py --project TWProbe --platform Threads --file draft.txt \\
        --card-id tw-cliff-001
    python content_gate.py --project TWProbe --platform Threads --file draft.txt \\
        --source-url https://money.udn.com/... --source-url https://...

    from content_gate import check
    issues, warnings, stats = check(text, platform="Threads",
                                    project="TWProbe", source_urls=[...], card_id="tw-cliff-001")
"""
import argparse
import io
import json
import os
import re
import sys
import ledger  # 同目錄;Marketing 的專案根註冊表在此模組

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 2026-08-30:改由 __file__ 推導本專案的 devops/。原本寫死 DevOps hub,
# 而 hub 已於當日退役為純憑證庫。
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKETING_DIR = os.path.join(ROOT_DIR, "Marketing")

# --------------------------------------------------------------------- AI 味
# 硬退:出現就是模板套話,沒有例外。
AI_HARD_ZH = [
    "心臟真的要很大顆", "三大現實", "三大痛點",
    "讓我們來看看", "讓我們一起", "總結來說", "綜上所述", "不可否認",
    "在當今快節奏", "在當今", "值得注意的是", "眾所周知",
    "不僅僅是", "更是一種", "隨著時代的進步", "扮演著重要的角色",
    "首先，其次，最後", "由此可見", "總的來說",
]

AI_HARD_EN = [
    "delve into", "tapestry", "in today's fast-paced", "let's dive in",
    "it's not just", "navigating the", "unlock the power", "game-changer",
    "in conclusion,", "moreover,", "furthermore,", "it's worth noting that",
    "at the end of the day,", "when it comes to",
]

# 簡體中文詞彙滲入繁體文案。
ZH_CN_LEAK = {
    "質量": "品質", "信息": "資訊", "視頻": "影片", "網絡": "網路",
    "軟件": "軟體", "硬件": "硬體", "數據庫": "資料庫", "服務器": "伺服器",
    "打印": "列印", "屏幕": "螢幕", "鼠標": "滑鼠", "internet": "網際網路",
    "激活": "啟用", "默認": "預設", "優化": "最佳化", "接口": "介面",
    "項目": "專案", "水平": "水準", "渠道": "通路", "力度": "力道",
}

# 軟性:提醒看一眼,不擋。
AI_SOFT_ZH = ["其實", "基本上", "換句話說", "簡單來說", "事實上"]

# CKM 高棉文外國文字與語法過濾白名單 (Whitelist)
CKM_ALLOWED_RANGES = [
    (0x1780, 0x17FF),   # Khmer
    (0x19E0, 0x19FF),   # Khmer symbols
    (0x0020, 0x007E),   # printable ASCII
    (0x00A0, 0x00FF),   # latin-1 supplement
    (0x2000, 0x206F),   # general punctuation
]
CKM_ALLOWED_CHARS = set("\n\r\t")

CKM_SCRIPTS = [
    (0x0E00, 0x0E7F, "Thai"), (0x0900, 0x097F, "Devanagari"),
    (0x0980, 0x09FF, "Bengali"), (0x4E00, 0x9FFF, "CJK (Chinese/Japanese)"),
    (0x3040, 0x30FF, "Kana"), (0x0590, 0x05FF, "Hebrew"),
    (0x0600, 0x06FF, "Arabic"), (0xAC00, 0xD7AF, "Hangul"),
    (0x3000, 0x303F, "CJK punctuation"),
]

CKM_DOUBLED = ["លោកលោក", "យើងយើង", "និងនិង", "ដែលដែល", "ការការសុំ", "ការការធ្វើ"]
CKM_MISSPELLINGS = {
    "ដើមីបី": "ដើម្បី",
    "គួចៀសវាង": "គួរចៀសវាង",
    "បាយខ្ទប់ស្លឹកឈូក": "បាយខ្ចប់ស្លឹកឈូក",
}
CKM_ABSOLUTES = [
    (r"១០០\s*%", "絕對值百分比承諾 (100%)"),
    (r"គ្មានការចំណាយលាក់កំបាំង", "絕對值『完全無隱藏費用』承諾"),
    (r"ធានា\s*១០០", "絕對保證承諾"),
]


def _km_script_name(cp):
    for lo, hi, name in CKM_SCRIPTS:
        if lo <= cp <= hi:
            return name
    return "U+%04X" % cp


def _check_ckm_khmer(text):
    """專門為 CKM 高棉文進行外國字元白名單過濾、疊字與過度承諾檢查。"""
    issues = []
    warns = []
    
    # 1. 外國文字過濾 (Thai, Devanagari, CJK, etc.)
    for i, ch in enumerate(text):
        if ch in CKM_ALLOWED_CHARS:
            continue
        cp = ord(ch)
        if any(lo <= cp <= hi for lo, hi in CKM_ALLOWED_RANGES):
            continue
        ctx = text[max(0, i - 15):i + 12].replace("\n", " ")
        issues.append(f"【外國文字污染】偵測到 {_km_script_name(cp)} 字元 {ch!r} (U+{cp:04X}): ...{ctx}... (Hanuman 字型無法排版，會產生豆腐方塊)")

    # 2. 疊字檢查 (Doubled Words)
    for w in CKM_DOUBLED:
        if w in text:
            issues.append(f"【高棉文重複疊字】出現語法錯誤疊字: {w!r}")

    # 3. 錯別字檢查 (Misspellings)
    for bad, good in CKM_MISSPELLINGS.items():
        if bad in text:
            issues.append(f"【高棉文錯別字】出現常見錯字 {bad!r}，正確應為 {good!r}")

    # 4. 絕對值承諾 (Absolutes)
    for pat, label in CKM_ABSOLUTES:
        if re.search(pat, text):
            issues.append(f"【絕對值過度承諾】出現 {label}，違反 CKM 憲政第 11 條紅線！")

    # 5. 英文單字替代警告
    for eng_w in ["Catering", "VIP", "HACCP", "Buffet"]:
        if re.search(r"\b" + eng_w + r"\b", text, re.IGNORECASE):
            warns.append(f"【英文單字替換】文案中出現 '{eng_w}'，建議替換為對應高棉文尊榮行話")

    return issues, warns


# 平台字數區間。來源:各平台 SKILL.md
PLATFORM_LENGTH = {
    "Threads": (250, 450),
    "X": (100, 280),
    "LinkedIn": (600, 1800),
    "Facebook": (80, 400),
    "Mobile01": (300, 1500),
    "PTT": (300, 2000),
}


def _zh_chars(text):
    """不計空白與換行的字元數。中文字數用這個算,不要用 len()。"""
    return len(re.sub(r"\s", "", text))


def _extract_numbers_from_card(card_obj):
    """遞迴提取卡片中出現的所有金額、數字與百分比字串。"""
    extracted = []
    def _walk(val, prefix=""):
        if isinstance(val, str):
            # 尋找金額、萬、億、百分比、年、月等數值字串
            matches = re.findall(r"(?:NT\$\s*)?[\d,.]+\s*(?:萬|億|%|年|人|元|/月)?", val)
            for m in matches:
                m_clean = m.strip()
                if m_clean and any(c.isdigit() for c in m_clean):
                    extracted.append((prefix, m_clean, val))
        elif isinstance(val, dict):
            for k, v in val.items():
                _walk(v, f"{prefix}.{k}" if prefix else k)
        elif isinstance(val, list):
            for i, v in enumerate(val):
                _walk(v, f"{prefix}[{i}]")
    _walk(card_obj)
    return extracted


def check_card_alignment(text, card_id, project=None, platform=None, card_file=None):
    """核對文案中的數字與 cards.json 圖卡記載是否矛盾。"""
    issues = []
    warnings = []

    # 1. 尋找 cards.json
    candidates = []
    if card_file and os.path.exists(card_file):
        candidates.append(card_file)
    if project and platform:
        # 2026-08-30:改走 ledger 的專案根註冊表。專案內容搬出 hub 之後,
        # 直接拼 MARKETING_DIR 會指到不存在的路徑而讓 cards.json 靜默找不到。
        _proot = ledger.project_dir(project)
        candidates.append(os.path.join(_proot, platform, "cards.json"))
        candidates.append(os.path.join(_proot, "Threads", "cards.json"))

    card_path = next((p for p in candidates if os.path.exists(p)), None)
    if not card_path:
        warnings.append(f"未找到圖卡資料庫 cards.json (搜尋路徑: {candidates})，跳過圖文數值對齊。")
        return issues, warnings

    try:
        with open(card_path, "r", encoding="utf-8") as f:
            cards_data = json.load(f)
    except Exception as e:
        warnings.append(f"讀取 cards.json 失敗: {e}")
        return issues, warnings

    cards = cards_data.get("cards", [])
    target_card = next((c for c in cards if c.get("id") == card_id), None)
    if not target_card:
        issues.append(f"在 {card_path} 中找不到指定的圖卡 ID 『{card_id}』")
        return issues, warnings

    # 2. 檢驗特定核心欄位數值 (例如 delta.value, gap.value, tag 關鍵字)
    # 檢查 Tag / Title 中的數字
    tag_str = target_card.get("tag", "")
    if "萬" in tag_str:
        tag_num = re.search(r"([\d,.]+)\s*萬", tag_str)
        if tag_num:
            num_val = tag_num.group(1)
            # 若文案出現該關鍵概念（如 雙貸族），但數字不符
            if "雙貸族" in tag_str and "雙貸族" in text:
                m = re.search(r"([\d,.]+)\s*萬\s*(?:名|位|個|戶)?\s*雙貸族", text)
                if m and m.group(1).replace(",", "") != num_val.replace(",", ""):
                    issues.append(f"圖文數值衝突: 圖卡 {card_id} 標註『{num_val} 萬雙貸族』，但文案寫為『{m.group(1)} 萬雙貸族』")

    # 檢查 gap / delta 的差額數值
    gap_val = (target_card.get("delta") or target_card.get("gap") or {}).get("value", "")
    if gap_val:
        num_match = re.search(r"([\d,.]+)\s*(萬|元|/ 月|/月)?", gap_val)
        if num_match:
            val_core = num_match.group(1).replace(",", "")
            unit = num_match.group(2) or ""
            # 如果文案提及「多掏 / 差額 / 缺口」，檢查數字
            if "多掏" in text or "差額" in text or "缺口" in text:
                # 尋找文案中的缺口金額
                for trigger in ["多掏", "差額", "缺口", "多出", "多付"]:
                    if trigger in text:
                        m_txt = re.search(trigger + r"[^，。！？\n]*?([\d,.]+)\s*(萬|元)", text)
                        if m_txt:
                            txt_num = m_txt.group(1).replace(",", "")
                            txt_unit = m_txt.group(2)
                            if unit.startswith("萬") and txt_unit == "萬" and txt_num != val_core:
                                issues.append(f"圖文數值衝突: 圖卡 {card_id} 記載缺口/差額為『{gap_val}』，但文案寫為『{trigger} {txt_num} {txt_unit}』")

    warnings.append(f"圖卡數值對齊完成 (已核對圖卡: {card_id} - {target_card.get('title', '')[:30]})")
    return issues, warnings


def check(text, platform=None, ledger_path=None, project=None, source_urls=None, card_id=None, card_file=None, exclude_id=None):
    """回傳 (issues, warnings, stats)。issues 是硬退,warnings 是請看一眼。"""
    issues, warnings = [], []

    # 1. 零外鏈。所有平台一致,連結放個人檔案或粉專資訊,不放貼文內。
    urls = re.findall(r"https?://[^\s]+", text)
    if urls:
        issues.append(f"發現 {len(urls)} 個外部連結,違反零外鏈規則:{urls[0][:60]}")

    # 2. AI 模板套話
    for phrase in AI_HARD_ZH + AI_HARD_EN:
        if phrase.lower() in text.lower():
            issues.append(f"AI 模板套話:『{phrase}』")

    # 3. 簡體詞彙滲入
    for cn, tw in ZH_CN_LEAK.items():
        if cn in text:
            issues.append(f"簡體/中國用語『{cn}』,台灣寫『{tw}』")

    # 4. 軟性提醒
    for phrase in AI_SOFT_ZH:
        n = text.count(phrase)
        if n >= 2:
            warnings.append(f"『{phrase}』出現 {n} 次,連用會有填充感")

    # 5. 長度
    chars = _zh_chars(text)
    if platform in PLATFORM_LENGTH:
        lo, hi = PLATFORM_LENGTH[platform]
        if chars < lo:
            warnings.append(f"{platform} 建議 {lo}~{hi} 字,目前 {chars} 字偏短")
        elif chars > hi:
            warnings.append(f"{platform} 建議 {lo}~{hi} 字,目前 {chars} 字偏長")

    # 6. 全形半形。中文段落裡混用半形標點是最容易被認出的機器痕跡之一。
    if re.search(r"[一-鿿][,.!?;:]", text):
        warnings.append("中文字後面接半形標點,台灣寫法用全形，。！？")

    # 7. 圖文數值對齊檢查 (若指定 --card-id)
    if card_id:
        c_issues, c_warns = check_card_alignment(text, card_id, project=project, platform=platform, card_file=card_file)
        issues.extend(c_issues)
        warnings.extend(c_warns)

    # 7.5. 若為 CKM 專案或包含高棉文，執行高棉文外國文字與語法過濾 (Whitelist & Anti-Accident)
    if project == "CKM" or any(0x1780 <= ord(c) <= 0x17FF for c in text):
        km_issues, km_warns = _check_ckm_khmer(text)
        issues.extend(km_issues)
        warnings.extend(km_warns)

    # 8. 帳本嚴格查重 (圖片素材、全文、開場白、引用來源)，整段委派給 ledger.py (重複機率 0 鐵律)
    if project and platform:
        try:
            from ledger import check as ledger_check
            head = text.strip().splitlines()[0].strip() if text.strip() else ""
            # 提取話題標籤作為 topic
            tags = re.findall(r"#[^\s#]+", text)
            cand_topic = tags[0] if tags else None
            cand_assets = []
            if card_id:
                cand_assets.append(card_id)

            blocking, warns = ledger_check(
                project,
                platform,
                topic=cand_topic,
                hook=head,
                content=text,
                assets=cand_assets,
                source_urls=source_urls,
                exclude_id=exclude_id
            )
            issues.extend(blocking)
            warnings.extend(warns)
        except FileNotFoundError as e:
            warnings.append(f"找不到帳本,查重未執行:{e}")
        except Exception as e:
            warnings.append(f"帳本查重失敗:{e}")
    elif ledger_path:
        warnings.append("只給了 --ledger 路徑;查重需要 --project 與 --platform")

    return issues, warnings, {"chars": chars, "urls": len(urls), "platform": platform, "card_id": card_id}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--platform", choices=sorted(PLATFORM_LENGTH))
    ap.add_argument("--project", help="查重與圖卡比對需要;例:TWProbe")
    ap.add_argument("--ledger", help="舊參數,保留相容;查重請改用 --project/--platform")
    ap.add_argument("--card-id", help="核對圖卡數值一致性與圖卡防重 (例如 tw-cliff-001)")
    ap.add_argument("--asset", action="append", default=[], help="素材檔名或圖卡 ID 查重")
    ap.add_argument("--exclude-id", help="排除自身的 post id 避免自我碰撞 (例如 th-2026-004)")
    ap.add_argument("--card-file", help="指定 cards.json 路徑 (選填)")
    ap.add_argument("--source-url", action="append", default=[],
                    help="這篇引用了哪些來源;可重複給,用來擋重複引用同一篇報導")
    ap.add_argument("--file", help="草稿檔;不給就從 stdin 讀")
    args = ap.parse_args()

    text = io.open(args.file, encoding="utf-8").read() if args.file else sys.stdin.read()
    issues, warnings, stats = check(text, args.platform, args.ledger,
                                    project=args.project, source_urls=args.source_url,
                                    card_id=args.card_id or (args.asset[0] if args.asset else None),
                                    card_file=args.card_file,
                                    exclude_id=args.exclude_id)

    print(f"[GATE] {stats['platform'] or '未指定平台'} | {stats['chars']} 字 | "
          f"{stats['urls']} 個連結" + (f" | 圖卡 {stats['card_id']}" if stats.get('card_id') else ""))
    for i in issues:
        print(f"  [退回] {i}")
    for w in warnings:
        print(f"  [注意] {w}")
    if not issues and not warnings:
        print("  機械檢查全過。")
    print()
    print("  機械檢查只擋得住可判定的東西。節奏、語氣、是否像真人,請自己讀一遍——")
    print("  這一步不要交給機器,也不要假裝機器做得到。")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
