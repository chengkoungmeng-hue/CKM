"""行銷帳本的統一 schema 與查重。

為什麼要統一
------------
2026-08-23 量到九個平台帳本裡有資料的三份,是三種不同的 post 形狀:

    CKM/Facebook      alt_text, date, format, id, image_asset, language,
                      source_pulse_id, status, topic, zero_link_verified
    Sunder/LinkedIn   content, format, hashtags, hook, id, key_metrics,
                      published_at, status, target_audience, topic, urn
    TWProbe/Threads   content, hook, id, image_filename, image_prompt,
                      math_formula, metrics, pain_point_core, published_at,
                      topic_tag, url

日期欄位就有三個名字(`date` / `published_at` / 無)。一個要跨平台查重的機制,
不可能建在三種形狀上——所以 agent 實際上從來沒有真的查過重。

**而且沒有任何一份記錄來源網址。** Owner 的要求包含「不重複引用相同的連結」,
在現行結構下辦不到。

查重的範圍是「單一表面」,不是全域
----------------------------------
Owner 裁定 2026-08-23:「專案的網站不能重複,外部平台的也是不能重複,
但是他們交叉重疊是沒關係的。」

    Sunder 官網的文章            ← 彼此不可重複(去重帳本在 Sunder repo)
    Marketing/Sunder/LinkedIn/   ← 彼此不可重複(這裡)
    兩者之間                      ← **可以是同一個題目、同一個來源**

理由:網站文章與社群貼文是給不同讀者、不同形式的兩個產物。同一則報導寫成一篇
2,500 字白皮書、再寫成一則 LinkedIn 短文,那不是重複,那是同一份工作的兩種輸出。
同理,TWProbe 的一個洞見可以同一天出現在 Threads 和一則 PTT 回覆裡。

**所以 `check()` 只讀該平台自己的帳本,不跨平台、也不讀專案 repo 的去重帳本。**
這不是疏漏——如果哪天有人覺得「應該全域查重比較嚴謹」而把它們串起來,結果是
LinkedIn 發過的題目讓官網不能寫,那個限制沒有任何人要求過。

三種重複,三種後果
------------------
| 重複的東西 | 讀者看到什麼 | 判定方式 |
| 同一個題目 | 「這個我上週看過」 | `topic` 完全比對 |
| 同一句開場 | 「這是機器寫的」 | `hook` 相似度 ≥ 0.70 |
| 同一篇來源 | 「他只是在轉貼」 | `source_urls` 交集 |

第三種最容易發生也最難自己發現:同一則報導會出現在多個 feed 裡,
換個標題就看不出來是同一篇。所以查的是網址不是標題。

`extra` 的用意
--------------
各平台真的有自己的欄位(Threads 的 `math_formula`、LinkedIn 的 `urn`)。
硬塞進共用 schema 會讓 schema 長到沒有人維護,所以它們進 `extra`,
共用層不碰。**共用的欄位才是查重的依據,其餘各平台自便。**
"""
import difflib
import io
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

SCHEMA_VERSION = "ledger/1"
MARKETING = r"C:\Projects\DevOps\Marketing"

# 各專案的 Marketing 根目錄。2026-08-30 加入。
#
# 在此之前,ledger / audit_devops / content_gate 三支都是用 listdir 或 os.walk
# 列舉 MARKETING 底下的專案。那個做法有一個不會報錯的失敗模式:專案的內容一旦
# 搬出 hub,三支工具就靜默地少掃一個專案,而跨專案查重的涵蓋範圍因此縮小,
# 稽核卻照樣印「4 大專案全部達標」。**列舉目錄等於讓涵蓋範圍取決於檔案擺在哪裡。**
# 改成顯式註冊表之後,少了一個專案會是查得到的事實,不是看不見的縮減。
# 2026-08-30 自 DevOps hub 遷入。原本這裡登記四個專案,已裁到只剩本專案——
# 四個 repo 各留一份完整清單會讓別人的網域與設定散佈到不需要它的地方,
# 而且下一個人讀到會以為這支工具還在管四個專案。
MARKETING_ROOTS = {
    'CKM': 'C:\\Projects\\CKM\\devops\\Marketing',
}


def projects():
    """回傳所有登記的專案名。取代 os.listdir(MARKETING)。"""
    return sorted(MARKETING_ROOTS)


def project_dir(project):
    """回傳該專案的 Marketing 根目錄。"""
    if project not in MARKETING_ROOTS:
        raise KeyError(f"未登記的專案 {project!r};可用:{', '.join(projects())}")
    return MARKETING_ROOTS[project]
TZ = timezone(timedelta(hours=8))

# 開場白相似度門檻。與 content_gate.py 共用同一個數字,兩邊要一起改。
# 校準見 content_gate.py:實測 0.42 是不同角度(該過)、0.94 是換兩個字(該擋)。
HOOK_DUP_RATIO = 0.70

# 共用欄位。查重只看這些;其餘進 extra。
POST_FIELDS = [
    "id",            # 平台內唯一
    "status",        # queued | published
    "published_at",  # ISO 日期
    "url",           # 發布後回填
    "topic",         # 這篇在講什麼,查重用
    "hook",          # 開場白,查重用
    "source_urls",   # 引用了哪些來源,查重用
    "pulse_item_ids",  # 用了 pulse.json 裡的哪幾筆素材
    "assets",        # 圖檔名
    "metrics",       # views / likes / replies / follows
    "extra",         # 平台自有欄位
]


def path_for(project, platform):
    return os.path.join(project_dir(project), platform, "ledger.json")


def load(project, platform):
    p = path_for(project, platform)
    if not os.path.exists(p):
        raise FileNotFoundError(f"找不到帳本:{p}")
    return json.load(io.open(p, encoding="utf-8"))


def save(project, platform, data):
    data["updated_at"] = datetime.now(TZ).isoformat()
    p = path_for(project, platform)
    io.open(p, "w", encoding="utf-8", newline="\n").write(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    return p


def normalise_post(raw):
    """把任何一種舊形狀轉成共用形狀,平台自有欄位收進 extra。"""
    out = {k: None for k in POST_FIELDS}
    out["source_urls"] = []
    out["pulse_item_ids"] = []
    out["assets"] = []
    out["metrics"] = {}
    out["extra"] = {}

    alias = {
        "date": "published_at",
        "topic_tag": "topic",
        "key_metrics": "metrics",
        "image_filename": "assets",
        "image_asset": "assets",
        "urn": None,          # LinkedIn 的內部 id,進 extra
    }

    for k, v in raw.items():
        target = alias.get(k, k if k in POST_FIELDS else None)
        if target is None:
            out["extra"][k] = v
        elif target == "assets":
            out["assets"] = [v] if isinstance(v, str) else list(v or [])
        elif target == "metrics":
            out["metrics"] = v if isinstance(v, dict) else {"raw": v}
        else:
            out[target] = v

    if not out["status"]:
        out["status"] = "published" if out.get("url") else "queued"
    return out


def _norm_asset(a):
    """標準化素材識別碼，例如 'TWProbe_2026-08-23_tw-cliff-001.png' -> 'tw-cliff-001'。"""
    if not a:
        return ""
    base = os.path.basename(str(a)).lower()
    base = re.sub(r'^[a-z]+_\d{4}-\d{2}-\d{2}_', '', base)  # 去除專案前綴與日期
    base = os.path.splitext(base)[0]
    return base.strip()


def check(project, platform, topic=None, hook=None, content=None, assets=None, source_urls=None, exclude_id=None):
    """回傳 (blocking, warnings)。blocking 非空代表硬退 (重複機率為 0 鐵律)。"""
    data = load(project, platform)
    posts = data.get("posts", [])
    blocking, warnings = [], []
    srcs = set(source_urls or [])
    
    cand_assets = {_norm_asset(a) for a in (assets or []) if _norm_asset(a)}

    for p in posts:
        pid = p.get("id", "?")
        if exclude_id and pid == exclude_id:
            continue
        if p.get("status") == "cancelled":
            continue

        when = (p.get("published_at") or "")[:10] or "待發布草稿"

        # 1. 圖卡素材嚴格查重 (重複機率 0 鐵律)
        if cand_assets:
            p_assets = {_norm_asset(a) for a in (p.get("assets") or []) if _norm_asset(a)}
            # 亦檢查 extra 裡的 card_id / image_prompt
            extra_card = _norm_asset(p.get("extra", {}).get("card_id") or "")
            if extra_card:
                p_assets.add(extra_card)
            
            asset_overlap = cand_assets & p_assets
            if asset_overlap:
                blocking.append(
                    f"【圖卡素材衝突】圖卡 『{list(asset_overlap)[0]}』 已在 {pid}({when}) 使用過！嚴禁重複使用相同圖卡。"
                )

        # 2. 題目完全比對
        if topic and p.get("topic") and topic.strip() == str(p["topic"]).strip():
            # 若為通用標籤 (#房貸 / #預售屋)，進一步比對內文，若非通用則直接擋
            if not topic.startswith("#"):
                blocking.append(f"【題目重複】題目與 {pid}({when}) 完全相同:『{topic}』")

        # 3. Hook 開場白相似度比對
        if hook and p.get("hook"):
            r = difflib.SequenceMatcher(None, hook.strip()[:60],
                                        str(p["hook"]).strip()[:60]).ratio()
            if r >= HOOK_DUP_RATIO:
                blocking.append(f"【開場白衝突】開場白與 {pid}({when}) 相似度 {r:.0%} (≥ {HOOK_DUP_RATIO:.0%}):『{str(p['hook'])[:28]}...』")
            elif r >= HOOK_DUP_RATIO - 0.15:
                warnings.append(f"開場白與 {pid} 相似度 {r:.0%}，建議微調切入角度")

        # 4. 全文內容相似度比對 (Full-Text Content Overlap)
        p_content = p.get("extra", {}).get("content") or p.get("content") or ""
        if content and p_content:
            clean_cand = re.sub(r"\s+", "", content)
            clean_prev = re.sub(r"\s+", "", p_content)
            content_ratio = difflib.SequenceMatcher(None, clean_cand, clean_prev).ratio()
            if content_ratio >= 0.50:
                blocking.append(
                    f"【全文文案重複】文案與 {pid}({when}) 內容重疊度高達 {content_ratio:.0%} (門檻 50%)！嚴禁重複發布相似文案。"
                )

        # 5. 來源網址交集
        overlap_src = srcs & set(p.get("source_urls") or [])
        if overlap_src:
            blocking.append(
                f"【引用來源重複】來源與 {pid}({when}) 重複: {list(overlap_src)[0][:70]}"
            )

    return blocking, warnings


def reserve_draft(project, platform, post_data):
    """生成文案後立即在帳本中預約 (status='pending')，防止後續回合或並行任務撞車。"""
    blocking, warnings = check(
        project,
        platform,
        topic=post_data.get("topic"),
        hook=post_data.get("hook"),
        content=post_data.get("extra", {}).get("content") or post_data.get("content"),
        assets=post_data.get("assets"),
        source_urls=post_data.get("source_urls"),
        exclude_id=post_data.get("id")
    )
    if blocking:
        raise ValueError("無法預約草稿，偵測到重複內容:\n" + "\n".join(f"• {b}" for b in blocking))

    data = load(project, platform)
    posts = data.setdefault("posts", [])
    
    # 若已有同 ID 則更新，否則插入
    pid = post_data.get("id")
    normed = normalise_post(post_data)
    normed["status"] = "pending"
    normed["updated_at"] = datetime.now(TZ).isoformat()
    
    existing_idx = next((i for i, p in enumerate(posts) if p.get("id") == pid), None)
    if existing_idx is not None:
        posts[existing_idx] = normed
    else:
        posts.insert(0, normed)
    
    save(project, platform, data)
    return normed


def publish_post(project, platform, post_id, url=None, metrics=None):
    """使用者發布後將草稿轉為正式已發布 (status='published') 並登記網址。"""
    data = load(project, platform)
    posts = data.get("posts", [])
    target = next((p for p in posts if p.get("id") == post_id), None)
    if not target:
        raise KeyError(f"在 {project}/{platform} 帳本中找不到 post id: {post_id}")
    
    target["status"] = "published"
    if url:
        target["url"] = url
    target["published_at"] = datetime.now(TZ).isoformat()
    if metrics:
        target["metrics"] = metrics
    
    save(project, platform, data)
    return target


def append(project, platform, post):
    """寫入一筆。呼叫前請先 check()——這裡不重複檢查。"""
    data = load(project, platform)
    data.setdefault("posts", []).insert(0, normalise_post(post))
    return save(project, platform, data)


def migrate_all(dry_run=True):
    """把九個帳本轉成共用 schema。既有資料一筆不丟,只是換位置。"""
    changed = []
    for project in projects():
        pdir = project_dir(project)
        if not os.path.isdir(pdir):
            continue
        for platform in sorted(os.listdir(pdir)):
            p = path_for(project, platform)
            if not os.path.exists(p):
                continue
            data = json.load(io.open(p, encoding="utf-8"))
            before = json.dumps(data, ensure_ascii=False, sort_keys=True)
            data["schema_version"] = SCHEMA_VERSION
            data["project"] = data.get("project", project)
            data["platform"] = data.get("platform", data.pop("channel", platform))
            data.setdefault("zero_link_policy", True)
            data["posts"] = [normalise_post(x) for x in data.get("posts", [])]
            after = json.dumps(data, ensure_ascii=False, sort_keys=True)
            if before != after:
                changed.append(f"{project}/{platform}")
                if not dry_run:
                    save(project, platform, data)
def status():
    """一次看完所有帳本。"""
    rows = []
    for project in projects():
        pdir = project_dir(project)
        if not os.path.isdir(pdir):
            continue
        for platform in sorted(os.listdir(pdir)):
            p = path_for(project, platform)
            if not os.path.exists(p):
                continue
            d = json.load(io.open(p, encoding="utf-8"))
            posts = d.get("posts", [])
            pub = [x for x in posts if x.get("status") == "published"]
            last = max((x.get("published_at") or "" for x in posts), default="")
            srcs = {u for x in posts for u in (x.get("source_urls") or [])}
            rows.append((f"{project}/{platform}", len(posts), len(pub),
                         last[:10] or "—", len(srcs), d.get("schema_version", "?")))
    return rows


def review(target_project=None):
    """分析各平台發文數據，產出最佳 Hook 開場白排行榜與數據補填提醒。"""
    all_posts = []
    pending_metrics = []

    for project in projects():
        if target_project and project != target_project:
            continue
        pdir = project_dir(project)
        if not os.path.isdir(pdir):
            continue
        for platform in sorted(os.listdir(pdir)):
            p = path_for(project, platform)
            if not os.path.exists(p):
                continue
            d = json.load(io.open(p, encoding="utf-8"))
            for post in d.get("posts", []):
                if post.get("status") != "published":
                    continue
                metrics = post.get("metrics") or {}
                views = metrics.get("views") or metrics.get("impressions") or 0
                likes = metrics.get("likes") or 0
                replies = metrics.get("replies") or metrics.get("comments") or 0
                shares = metrics.get("shares") or metrics.get("reposts") or 0
                score = round(likes * 5 + replies * 10 + shares * 15 + views * 0.05, 1)

                hook = post.get("hook") or (post.get("topic") or "")
                
                # 判定 Hook 類型
                if any(k in hook for k in ["萬", "億", "%", "成", "元", "算式", "數字"]):
                    archetype = "數字算式型"
                elif any(k in hook for k in ["條", "法", "央行", "管制", "消保", "銀行法"]):
                    archetype = "法規揭密型"
                elif any(k in hook for k in ["注意", "小心", "地雷", "違約", "陷阱", "斷崖", "缺口", "痛點"]):
                    archetype = "痛點避坑型"
                else:
                    archetype = "觀點敘事型"

                post_info = {
                    "project": project,
                    "platform": platform,
                    "id": post.get("id"),
                    "published_at": (post.get("published_at") or "")[:10],
                    "hook": hook,
                    "topic": post.get("topic"),
                    "url": post.get("url"),
                    "views": views,
                    "likes": likes,
                    "replies": replies,
                    "shares": shares,
                    "score": score,
                    "archetype": archetype,
                    "has_metrics": bool(views or likes or replies or shares)
                }
                all_posts.append(post_info)
                if not post_info["has_metrics"] and post.get("url"):
                    pending_metrics.append(post_info)

    return all_posts, pending_metrics


def print_review(target_project=None):
    posts, pending = review(target_project)
    print("=" * 72)
    print("        社群發布成效與最佳 Hook 開場白複盤報告 (LEDGER REVIEW)")
    print("=" * 72)
    print(f"  • 累計已發布貼文: {len(posts)} 篇 ｜ 已有成效數據: {len([p for p in posts if p['has_metrics']])} 篇")
    
    total_views = sum(p["views"] for p in posts)
    total_likes = sum(p["likes"] for p in posts)
    print(f"  • 累計總觀看次數: {total_views:,} 次 ｜ 累計總讚數: {total_likes:,} 個\n")

    # 按成效分數排序
    ranked = sorted(posts, key=lambda x: (x["score"], x["likes"], x["views"]), reverse=True)

    print("🏆 TOP 最佳表現貼文與 Hook 排行榜：")
    print("-" * 72)
    for idx, p in enumerate(ranked[:6], 1):
        metrics_str = f"{p['views']} 觀看 / {p['likes']} 讚 / {p['replies']} 回覆" if p['has_metrics'] else "暫無數據"
        print(f"  {idx}. [{p['project']}/{p['platform']}] [{p['archetype']}] {metrics_str}")
        print(f"     Hook: 『{p['hook'][:65]}...』" if len(p['hook']) > 65 else f"     Hook: 『{p['hook']}』")
        if p.get("url"):
            print(f"     連結: {p['url']}")
        print()

    if pending:
        print("⏳ 待追蹤回補數據的貼文 (已發布但尚未填入 views/likes)：")
        print("-" * 72)
        for p in pending[:5]:
            print(f"  • [{p['project']}/{p['platform']}] ({p['published_at']}) {p['hook'][:40]}...")
            print(f"    URL: {p['url']}")
        print()

    print("=" * 72 + "\n")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    if "--review" in sys.argv:
        proj = None
        for i, a in enumerate(sys.argv):
            if a == "--project" and i + 1 < len(sys.argv):
                proj = sys.argv[i + 1]
        print_review(proj)
        raise SystemExit(0)

    if "--status" in sys.argv:
        rows = status()
        print(f"{'專案/平台':26}{'貼文':>5}{'已發':>5}{'最近':>12}{'來源':>6}  schema")
        print("-" * 66)
        for name, n, pub, last, srcs, ver in rows:
            print(f"{name:26}{n:>5}{pub:>5}{last:>12}{srcs:>6}  {ver}")
        print()
        print(f"共 {len(rows)} 個平台帳本。專案網站的來源帳本另外兩份在各自的 repo,")
        print("刻意不合併——官網與外站交叉重疊是允許的(AGENTS.md §9.5-2)。")
        raise SystemExit(0)

    apply = "--apply" in sys.argv
    changed = migrate_all(dry_run=not apply)
    print(f"需要轉換的帳本:{len(changed)}")
    for c in changed:
        print("  ", c)
    if not apply:
        print("\n(乾跑。加 --apply 才會寫入)")

