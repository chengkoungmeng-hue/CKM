"""每日報告與素材的落點契約:輸出至 `Downloads/<Project>-report/<Project>_<YYYY-MM-DD>_<內容名稱>.<ext>`。

路徑與管理原則
--------------
Owner 裁定 2026-08-23:
1. 報告與圖片直接放置於 `Downloads/<Project>-report/` 專案目錄下，不再另外建立日期子目錄。
2. 檔名自帶日期 `<Project>_<YYYY-MM-DD>_<名稱>.<ext>`，一打開專案資料夾即可一覽全部產出，用完可整包刪除。
3. 發布查重完全依賴各平台永久維護的 `Marketing/<專案>/<平台>/ledger.json`（SSOT），即使 Downloads 內的報告被刪除，查重防重依然 100% 準確運作。

標準產出清單
------------
| 類型代號     | 檔名結尾        | 用途 / 內容 |
| json         | pulse.json      | 給 agent: 全部採集資料、痛點與相關性分數 |
| briefing     | briefing.md     | 給 owner: 人類可讀偵查摘要 |
| briefing_pdf | briefing.pdf    | 給 owner: 可截圖的四卡排版簡報 (lib/briefing_pdf.py) |
| digest       | digest.pdf      | 給群組: 僅新聞、無選題內部訊號 |
"""
import os
import shutil
from datetime import datetime, timedelta, timezone

# 預設使用 Windows 使用者 Downloads 目錄 (檔案總管「下載」)，確保使用者一開就能看見
USER_DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")
DOWNLOADS_ROOT = USER_DOWNLOADS

# 各專案的當地時區。日期用當地日期,不用 UTC
PROJECT_TZ = {
    "TWProbe": timezone(timedelta(hours=8)),    # 台北
    "Sunder": timezone(timedelta(hours=8)),     # 台北
    "CKM": timezone(timedelta(hours=7)),        # 金邊
    "PressaGen": timezone(timedelta(hours=8)),  # 營運端在台北
}

KEEP_DAYS = 4

# 四份產出的標準檔名結尾。
ARTEFACTS = {
    "json": "pulse.json",            # 給 agent:全部資料
    "briefing": "briefing.md",       # 給 owner:偵查摘要
    "briefing_pdf": "briefing.pdf",  # 同上,排版成可截圖的版面(lib/briefing_pdf.py)
    "digest": "digest.pdf",          # 給群組:只有新聞,無選題訊號
}


def today(project):
    tz = PROJECT_TZ.get(project, timezone(timedelta(hours=8)))
    return datetime.now(tz).strftime("%Y-%m-%d")


def report_dir(project="TWProbe", date_str=None, create=True):
    """回傳 Downloads/<Project>-report/ 目錄，預設會建立。"""
    p = os.path.join(DOWNLOADS_ROOT, f"{project}-report")
    if create:
        os.makedirs(p, exist_ok=True)
    return p


def artefact(project, kind, date_str=None, create=True):
    """回傳某一份產出的完整路徑: Downloads/<Project>-report/<Project>_<Date>_<ARTEFACT>"""
    if kind not in ARTEFACTS:
        raise KeyError(f"未知的產出類型 {kind!r};可用:{', '.join(ARTEFACTS)}")
    r_dir = report_dir(project, date_str, create=create)
    date_tag = date_str or today(project)
    filename = f"{project}_{date_tag}_{ARTEFACTS[kind]}"
    return os.path.join(r_dir, filename)


def custom_path(project, filename_suffix, date_str=None, create=True):
    """自訂後綴檔案路徑: Downloads/<Project>-report/<Project>_<Date>_<filename_suffix>"""
    r_dir = report_dir(project, date_str, create=create)
    date_tag = date_str or today(project)
    filename = f"{project}_{date_tag}_{filename_suffix}"
    return os.path.join(r_dir, filename)


def cleanup(project=None, keep_days=KEEP_DAYS, dry_run=False):
    """刪掉 Downloads/<Project>-report/ 裡超過保留期的舊產出檔案。"""
    removed = []
    projects = [project] if project else sorted(PROJECT_TZ)
    for proj in projects:
        proj_root = os.path.join(DOWNLOADS_ROOT, f"{proj}-report")
        if not os.path.isdir(proj_root):
            continue
        tz = PROJECT_TZ.get(proj, timezone(timedelta(hours=8)))
        cutoff = (datetime.now(tz) - timedelta(days=keep_days)).date()
        for fname in sorted(os.listdir(proj_root)):
            fpath = os.path.join(proj_root, fname)
            if not os.path.isfile(fpath):
                continue
            parts = fname.split("_")
            if len(parts) >= 2:
                try:
                    d = datetime.strptime(parts[1], "%Y-%m-%d").date()
                    if d < cutoff:
                        removed.append(fpath)
                        if not dry_run:
                            try:
                                os.remove(fpath)
                            except OSError:
                                pass
                except ValueError:
                    pass
    return removed


if __name__ == "__main__":
    print(f"產出目標根目錄: {DOWNLOADS_ROOT}")
    print("今日產出契約路徑:")
    for p in sorted(PROJECT_TZ):
        r_dir = report_dir(p)
        print(f"  [{p}] 目錄: {r_dir}")
        for k in ARTEFACTS:
            path = artefact(p, k, create=False)
            exists = "存在" if os.path.exists(path) else "未產出"
            print(f"    • {k:<12}: {os.path.basename(path)} ({exists})")
