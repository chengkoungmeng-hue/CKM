r"""CKM 的 hub 端材料採集。

這一支和 `C:\Projects\CKM\devops\fetch_catering_pulse.py`(已凍結)是**兩件不同的事**,不要合併:

* 專案 repo 的生成器 → 產出**網站內容**,去重帳本在 repo
* 這一支            → 產出**站外行銷的材料**,帳本在 Marketing/CKM/<平台>/

來源清單刻意和專案那邊重複。Owner 裁定 2026-08-23:「跟專案用同樣的來源也可以,
只是要拆開,不要去影響到。」網址是設定不是程式——各自一份不會分歧,而且 hub 的
採集壞掉不會影響專案發文。

同一則來源被網站寫一篇、又被社群寫一篇,是允許的(AGENTS.md §9.5-2)。
"""
import os
import sys
from datetime import timedelta, timezone

sys.stdout.reconfigure(encoding="utf-8")

# 2026-08-30 自 DevOps hub 遷入。collect.py 與 report_paths.py 現在與本檔同層,
# 原本指向 Pulse/ 與 Pulse/lib/ 的兩行推導因此合併為一行。
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from report_paths import artefact, cleanup                      # noqa: E402
from collect import fetch_rss, score_relevance, build_payload, write_json, write_briefing  # noqa: E402

TZ = timezone(timedelta(hours=7))
PROJECT = "CKM"

# 與 fetch_catering_pulse.py 的 FEEDS 相同,各自一份。
#
# 注意:CKM 網站的 pulse 生成已於 2026-08-23 凍結(見該 repo 的 AGENTS.md §15),
# 但這一支不受影響——它產出的是 Facebook 的材料,不是網站文章。兩件事本來就分開。
FEEDS = {
    "https://auntieemily.com/feed/": "Auntie Emily's Kitchen",
    "https://en.christinesrecipes.com/feeds/posts/default?alt=rss": "Christine's Recipes",
    "https://www.chinasichuanfood.com/feed/": "China Sichuan Food",
    "https://omnivorescookbook.com/feed/": "Omnivore's Cookbook",
    "https://thewoksoflife.com/feed/": "The Woks of Life",
    "https://www.thehongkongcookery.com/feeds/posts/default?alt=rss": "The Hong Kong Cookery",
    "https://www.huangkitchen.com/feed/": "Huang Kitchen",
}

# 受眾是金邊辦桌的客人,不是家庭料理讀者。宴席規模的菜才有用——
# 一人份的快炒和便當菜對「席開二十桌」的人沒有意義。
MUST = (r"banquet|wedding|feast|celebration|whole fish|whole chicken|roast|"
        r"braise|braised|steamed|soup|stew|abalone|scallop|prawn|crab|lobster|"
        r"pork belly|duck|suckling|Cantonese|Teochew|Chinese New Year")
REJECT = r"single serving|for one|meal prep|lunch box|air fryer|30-minute|weeknight"


def main():
    items = score_relevance(fetch_rss(FEEDS, TZ), must_match=MUST, reject=REJECT)
    payload = build_payload(PROJECT, TZ, items,
                            feeds_count=len(FEEDS),
                            relevance_pattern={"must": MUST, "reject": REJECT})

    stale = cleanup(PROJECT)
    if stale:
        print(f"[OK] 清除 {len(stale)} 個過期報告資料夾")

    write_json(artefact(PROJECT, "json"), payload)

    kept = sum(1 for i in items if i["relevance"]["score"] > 0)
    print(f"[{PROJECT}] {len(items)} 則素材,其中 {kept} 則命中相關性")
    print(f"  {artefact(PROJECT, 'json')}")
    # 一則都沒抓到就是來源全掛,那需要人看,不要綠燈帶過。
    return 0 if items else 1


if __name__ == "__main__":
    raise SystemExit(main())
