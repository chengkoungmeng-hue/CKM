"""四個專案共用的材料採集與 pulse.json 契約。

為什麼要有共用層
----------------
四支 pulse 各自實作了一次 RSS 抓取、日期解析與去重。實測 2026-08-23:
TWProbe 781 行、Sunder 1,074、CKM 2,140、PressaGen 152,而其中 RSS 那段做的是同一件事。
更要緊的是**它們的產出格式各不相同**,所以 marketing 的 skill 沒辦法用同一套邏輯讀。

這一層只解決後者:**pulse.json 的形狀統一**。各專案的選題邏輯、閘門、發布路徑仍然各自
獨立——那些是它們自己的事,而且 Sunder 與 CKM 的真本在各自的 repo 裡(AGENTS.md §8-2)。

來源可以和專案重複,但要各自一份
--------------------------------
Owner 裁定 2026-08-23:「跟專案用同樣的來源也可以,只是要拆開,不要去影響到。」
複製一支 2,140 行的產生器是錯的(那會分歧,今天已經有兩個實例);複製一份 RSS 網址
清單不是——網址是設定不是程式,而且各自一份代表 hub 的採集壞掉不會影響專案發文。

什麼算「材料」
--------------
列一堆標題不是材料。這一層給的是**事實與訊號**:誰、什麼、什麼時候、可引用的數字、
為什麼它通過了相關性門檻。**角度不在這裡**——那需要判斷,是 agent 的工作。
一個 collector 如果連「該用什麼角度寫」都幫你決定了,產出的會是四篇一模一樣的文章。
"""
import html
import json
import re
import sys
import urllib.request
import time
from urllib.parse import urlsplit
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

# 警告走 stderr。Windows 主控台預設 cp1252,不設這行中文會被逸出成十六進位
# 碼位——那不是壞掉,但沒有人讀得懂,等於警告沒有發出去。
sys.stderr.reconfigure(encoding="utf-8")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

# 有些來源對通用瀏覽器 UA 直接回 429,對具名的 bot UA 反而正常。實測 2026-08-23:
#
#   Chrome UA  https://www.reddit.com/r/SaaS/hot.rss  -> HTTP 429
#   具名 UA    同一個網址                              -> 200,25 筆
#
# Reddit 的 API 規則本來就要求可辨識的 UA。所以 UA 是每個 collector 自己的設定,
# 不是這一層寫死的常數——把它寫死,PressaGen 四個來源會有三個永遠拿不到東西。
#
# 順帶一提 `old.reddit.com/r/<板>/.rss` 是陷阱:它回 200 與 320 KB,但內容是 HTML
# 不是 feed,解析出 0 筆。那正是下面 no-entries 警告存在的理由。

SCHEMA_VERSION = "pulse/1"


# CDATA 要先拆掉,再剝標籤。順序反過來會把內容一起吃掉:
# `<[^>]+>` 在 `<![CDATA[Wi-Fi 8 is the first...]]>` 裡,會從 `<!` 一路吃到 `]]>`
# 的那個 `>`——中間整段標題都在裡面。實測 2026-08-23,hnrss 的 20 筆全部因此被丟掉
# (標題解析成空字串,然後被「沒有標題就跳過」靜默略過),而外層只看到「這個來源今天
# 沒東西」。這正是 §0 那句話的實例:**用製造改動的同一套假設去檢查,檢查不到東西**——
# 我先前用 `grep -c '<item>'` 確認過 feed 有料,那證明的是 HTTP 層,不是解析層。
CDATA = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.S)


def _text(s):
    """把 feed 欄位的內容變成純文字。**四個步驟的順序都是有理由的。**

    先拆 CDATA、再解實體、再剝標籤、最後收白。中間兩步反過來就會漏:Blogspot 的
    `<content type='html'>` 裡,HTML 是被跳脫成實體的(`&lt;i&gt;`)。若先剝標籤再解
    實體,剝的時候那裡還是純文字、沒有標籤可剝,解完實體才變回 `<i>`——而那時候已經
    沒有人再剝一次了。實測 2026-08-23,Christine's Recipes 的四則摘要就這樣把 `<i>`
    印進了 briefing。

    解完實體要再剝一次標籤,而不是把剝標籤挪到最前面:兩個位置都可能有標籤,
    做兩次才兩邊都乾淨。
    """
    s = CDATA.sub(chr(92) + "1", s or "")      # 反斜線一號;直接寫會被多層轉義吃掉
    s = re.sub(r"<[^>]+>", " ", s)             # 原生標籤
    s = html.unescape(s)                       # &lt;i&gt; -> <i>
    s = re.sub(r"<[^>]+>", " ", s)             # 上一步還原出來的標籤
    return re.sub(r"\s+", " ", s).strip()


def _link(block):
    """從一個 item/entry 取出文章網址。

    看起來該是一行,實際上有兩個坑,都是 2026-08-23 從 Christine's Recipes(Blogspot)
    量出來的——那個來源當天的 12 筆全部被丟掉:

    1. **屬性用單引號。** Blogspot 送的是 href='...',而原本的樣式只認雙引號,
       所以完全取不到。
    2. **第一個 <link> 不是文章。** Atom entry 依序是 rel='replies'(留言 feed)、
       rel='edit'、rel='self',文章在 rel='alternate'。取第一個會拿到留言 feed 的
       網址——那比取不到更糟:它是一個合法的網址,會通過所有檢查進到素材裡,
       而點下去不是那篇文章。
    """
    pats = [
        # Atom:優先找 rel=alternate,兩種引號都吃
        r"<link[^>]*rel=['\"]alternate['\"][^>]*href=['\"]([^'\"]+)",
        # 有些 Atom 把 href 寫在 rel 前面
        r"<link[^>]*href=['\"]([^'\"]+)['\"][^>]*rel=['\"]alternate",
        # RSS 2.0:<link>網址</link>
        r"<link>([^<]+)</link>",
        # 最後才退回「任何一個 href」
        r"<link[^>]*href=['\"]([^'\"]+)",
    ]
    for p in pats:
        m = re.search(p, block, re.I)
        if m:
            return _text(m.group(1))
    return ""


def parse_any_date(raw, tz):
    """RFC 2822 與 ISO 8601 都吃,失敗回 None。

    CKM 的 AGENTS.md §15 記載過:WordPress 送 RFC 2822、Blogspot 送 ISO 8601,
    只套一種解析器會讓 88 筆裡的 47 筆靜默塌成最舊。這裡兩種都試,
    而且**失敗回 None 而不是拋例外**——sorted() 中途拋錯會把整支跑掛掉。
    """
    if not raw:
        return None
    raw = raw.strip()
    try:
        d = parsedate_to_datetime(raw)
        return d.astimezone(tz) if d.tzinfo else d.replace(tzinfo=tz)
    except Exception:
        pass
    try:
        d = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return d.astimezone(tz) if d.tzinfo else d.replace(tzinfo=tz)
    except Exception:
        return None


def fetch_rss(feeds, tz, timeout=20, per_feed=12, user_agent=UA, host_delay=3):
    """feeds: {url: 來源名稱}。回傳正規化後的 item 清單。

    單一 feed 掛掉不該讓整次採集失敗——它只是少一個來源,而其餘來源仍然有料。
    但要印出來,不要靜默吞掉。
    """
    out = []
    last_host = None
    for url, source in feeds.items():
        # 同一個網域連續請求會被限流。實測 2026-08-23:一次執行連抓 Reddit 三個板,
        # 第一個 200、第二與第三個 429;分開單獨抓則三個都是 200。所以那不是封鎖,
        # 是節流——停一下就過,而少停這一下會讓兩個好好的來源看起來像掛了。
        host = urlsplit(url).netloc
        if host == last_host:
            time.sleep(host_delay)
        last_host = host
        try:
            req = urllib.request.Request(url, headers={"User-Agent": user_agent})
            xml = urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")
        except Exception as e:
            print(f"[WARN] feed 讀取失敗 {source}: {str(e)[:60]}", file=sys.stderr)
            continue

        # RSS 用 <item>,Atom 用 <entry>。兩種都收。
        blocks = re.findall(r"<item>(.*?)</item>", xml, re.S) or \
                 re.findall(r"<entry>(.*?)</entry>", xml, re.S)
        if not blocks:
            # 200 但零筆。最常見的成因是拿到 HTML 而不是 feed(見檔頭 old.reddit
            # 的例子),而那和「今天沒有新文章」在資料上長得一模一樣。不警告的話,
            # 一個壞掉的來源會安靜地變成「這個來源最近很冷清」。
            print(f"[WARN] {source} 回應 {len(xml)} 字元但解析出 0 筆;"
                  f"確認這個網址真的是 feed", file=sys.stderr)
            continue
        skipped = 0
        for b in blocks[:per_feed]:
            title_m = re.search(r"<title[^>]*>(.*?)</title>", b, re.S)
            title = _text(title_m.group(1)) if title_m else ""
            link = _link(b)
            date_m = re.search(r"<(?:pubDate|published|updated)>(.*?)</", b, re.S)
            dt = parse_any_date(_text(date_m.group(1)) if date_m else "", tz)
            # 收尾要指名收在哪個標籤,不能只寫 `</`。摘要裡本來就有 HTML,
            # 寫 `</` 會停在內文第一個 `</i>` 上,把 CDATA 切成沒有結尾的半截——
            # 於是 CDATA 拆不掉,`<i>` 原封不動印進 briefing。實測 2026-08-23,
            # Christine's Recipes 的摘要就是這樣開頭的。
            desc_m = re.search(
                "<(description|summary|content)[^>]*>(.*?)</" + chr(92) + "1>", b, re.S)
            summary = _text(desc_m.group(2))[:400] if desc_m else ""

            if not title or not link:
                skipped += 1
                continue
            out.append({
                "title": title,
                "url": link,
                "source": source,
                "summary": summary,
                "published_at": dt.isoformat() if dt else None,
                "age_hours": round((datetime.now(tz) - dt).total_seconds() / 3600, 1) if dt else None,
            })
        if skipped:
            print(f"[WARN] {source} 有 {skipped} 筆缺標題或連結而被略過;"
                  f"通常代表這個 feed 的格式沒被解析到", file=sys.stderr)
    return out


def score_relevance(items, must_match=None, reject=None):
    """給每一則一個分數與理由。**回傳全部,不丟掉任何一則。**

    為什麼不過濾:被丟掉的東西沒有人看得到,而門檻訂錯的時候沒有任何跡象。
    保留分數與命中的關鍵字,agent 自己決定要不要用,owner 也看得到門檻是不是訂歪了。
    """
    must = re.compile(must_match) if must_match else None
    rej = re.compile(reject) if reject else None
    for it in items:
        blob = f"{it['title']} {it.get('summary', '')}"
        hits = sorted({m.group(0) for m in must.finditer(blob)}) if must else []
        bad = sorted({m.group(0) for m in rej.finditer(blob)}) if rej else []
        it["relevance"] = {
            "score": len(hits) - 2 * len(bad),
            "matched": hits,
            "rejected": bad,
        }
    items.sort(key=lambda x: (-x["relevance"]["score"],
                              x["age_hours"] if x["age_hours"] is not None else 9999))
    return items


def build_payload(project, tz, items, **extra):
    """所有專案共用的 pulse.json 形狀。

    marketing 的 skill 讀的是這個。欄位不要各專案自己加減——
    加了就要在這裡加,否則 skill 對某個專案會讀不到。
    """
    now = datetime.now(tz)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "project": project,
        "report_date": now.strftime("%Y-%m-%d"),
        "generated_at": now.isoformat(),
        "items_count": len(items),
        "items": items,
    }
    payload.update(extra)
    return payload


def write_briefing(path, project, payload, top=12):
    """給人讀的偵查摘要。刻意只放判斷需要的東西,不是把 JSON 換行印一遍。"""
    items = payload.get("items", [])
    lines = [
        f"# {project} 每日情報摘要 — {payload['report_date']}",
        "",
        f"> 產生時間:{payload['generated_at']}  ",
        f"> 素材:{len(items)} 則",
        "",
        "---",
        "",
        "## 值得看的",
        "",
    ]
    for it in items[:top]:
        rel = it.get("relevance", {})
        tag = f"[{rel.get('score', 0):+d}]" if rel else ""
        age = f"{it['age_hours']:.0f}h" if it.get("age_hours") is not None else "—"
        lines.append(f"### {tag} {it['title']}")
        lines.append("")
        lines.append(f"* 來源:{it['source']} ｜ {age} 前")
        if rel.get("matched"):
            lines.append(f"* 命中:{'、'.join(rel['matched'][:6])}")
        if it.get("summary"):
            lines.append(f"* {it['summary'][:180]}")
        lines.append(f"* {it['url']}")
        lines.append("")

    if payload.get("ptt"):
        p = payload["ptt"]
        lines += ["---", "", "## PTT", "",
                  f"可回覆 {len(p.get('reply_opportunities', []))} 則、"
                  f"熱議 {len(p.get('hot_threads', []))} 則", ""]

    lines += ["---", "",
              "> 痛點、熱搜與相關性分數是**選題訊號**,只用來決定寫什麼。",
              "> 不要放進任何對外的貼文或 PDF——那等於把內容策略攤開給同業看。", ""]

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    return path


def write_json(path, payload):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path
