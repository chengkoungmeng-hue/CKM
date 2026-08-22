"""Render the /pulse/ share card as a PNG.

One card per pulse entry. The card is drawn from the entry's own Khmer text, so
nothing from any third party is reproduced -- it replaces the practice of
downloading a photograph from the source recipe blog.

Layout (variant C, chosen 2026-08-22): a single key point set large, with the
dish title as a small attribution line. The title is deliberately NOT the headline
of the card: Facebook and Telegram already render og:title and og:description as
text beside the image, so repeating it there wastes the only surface that can
carry something else.

Khmer needs complex text shaping (COENG subscripts stack below the base
consonant). Pillow does that only when built against raqm. Measured on the
ubuntu-latest runner 2026-08-22: Pillow 12.3.0 reports raqm 0.10.5 and a shaped/
naive advance ratio of 0.556, i.e. shaping is active. Windows wheels report
raqm=False, so a local render is NOT evidence -- render in CI when verifying.

Usage:
    python devops/render_pulse_card.py --slug <pulse-slug>      # one entry
    python devops/render_pulse_card.py --all                    # rebuild every card
    python devops/render_pulse_card.py --sample                 # first 3, for eyeballing
"""
import argparse
import io
import json
import os
import sys
import unicodedata

from PIL import Image, ImageDraw, ImageFont, features

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

# ---------------------------------------------------------------- constants
PULSE_DATA = os.path.join("src", "data", "pulseData.json")
FONT_DIR = os.path.join("devops", "fonts")
OUT_DIR = os.path.join("public", "images", "pulse")

# Brand palette, authoritative from tailwind.config.mjs (AGENTS.md section 9).
ONYX = (23, 23, 23)
CHAMPAGNE = (197, 160, 89)
WHITE = (245, 245, 245)
SLATE = (148, 163, 184)
HAIRLINE = (48, 43, 33)

W, H = 1200, 675  # 16:9, the Open Graph size
SS = 2            # supersample, downscaled at save time

# Khmer combining marks carry no advance width of their own; a line that is all
# base consonants is much wider than one dense with subscripts, so wrapping is
# measured, never counted.
COENG = "\u17d2"


def font_path(weight: int) -> str:
    """Hanuman, the family the site already self-hosts (AGENTS.md section 8).

    public/fonts/ carries woff2 for the browser and FreeType cannot read woff2,
    so devops/fonts/ holds a ttf converted from the same source with fontTools.
    It lives outside public/ deliberately: shipped there it would be 112 KB of
    site assets nothing ever requests. Falls back to the runner's Noto Serif
    Khmer, which shapes correctly but is off-brand -- warn rather than drift.
    """
    ttf = os.path.join(FONT_DIR, f"hanuman-khmer-{weight}-normal.ttf")
    if os.path.exists(ttf):
        return ttf
    for noto in (
        f"/usr/share/fonts/truetype/noto/NotoSerifKhmer-{'Bold' if weight >= 700 else 'Regular'}.ttf",
        "C:\\Windows\\Fonts\\KhmerUI.ttf",
    ):
        if os.path.exists(noto):
            print(f"   [WARN] {ttf} missing; falling back to {noto} (off-brand)")
            return noto
    raise FileNotFoundError(f"no Khmer font available for weight {weight}")


def load_font(weight: int, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(font_path(weight), size)


# ---------------------------------------------------------------- Khmer text
def cluster_split(text: str):
    """Split Khmer into orthographic clusters.

    AGENTS.md section 14 records a shipped defect: slicing Khmer on a codepoint
    index split a base consonant from its COENG and sent a dotted circle to the
    Google snippet. A cluster keeps a base together with everything that hangs
    off it -- subscripts introduced by COENG, and any combining mark.
    """
    clusters = []
    i = 0
    while i < len(text):
        start = i
        i += 1
        while i < len(text):
            ch = text[i]
            prev = text[i - 1]
            if prev == COENG:            # COENG binds the following consonant
                i += 1
                continue
            if ch == COENG:
                i += 1
                continue
            if unicodedata.combining(ch) or ("\u17b4" <= ch <= "\u17d1") or ch in "\u17dd":
                i += 1
                continue
            break
        clusters.append(text[start:i])
    return clusters


def truncate_clusters(text: str, draw, font, max_width: float) -> str:
    """Trim to fit, cutting only on cluster boundaries, adding a Khmer ellipsis."""
    if draw.textlength(text, font=font) <= max_width:
        return text
    clusters = cluster_split(text)
    ell = "\u2026"
    while clusters:
        clusters.pop()
        cand = "".join(clusters).rstrip() + ell
        if draw.textlength(cand, font=font) <= max_width:
            return cand
    return ell


def wrap_clusters(text: str, draw, font, max_width: float, max_lines: int):
    """Wrap on spaces where they exist, else on cluster boundaries.

    Khmer does not put spaces between words, so a space-only wrapper leaves one
    unbreakable run. Falling back to clusters keeps every base consonant with its
    subscripts, which is the part that must never be split.
    """
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width or not cur:
            cur = trial
            if draw.textlength(cur, font=font) <= max_width:
                continue
            # single token wider than the line: break it on clusters
            clusters = cluster_split(cur)
            cur = ""
            for cl in clusters:
                if draw.textlength(cur + cl, font=font) <= max_width:
                    cur += cl
                else:
                    lines.append(cur)
                    cur = cl
                    if len(lines) >= max_lines:
                        break
        else:
            lines.append(cur)
            cur = word
        if len(lines) >= max_lines:
            break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(lines) == max_lines and cur and cur not in lines:
        lines[-1] = cur
    # Last line may still overflow after the loop; trim it on clusters.
    if lines:
        lines[-1] = truncate_clusters(lines[-1], draw, font, max_width)
    return lines[:max_lines]


def pick_headline(entry: dict) -> str:
    """The shortest key point reads best at thumbnail size; fall back to summary."""
    points = [p for p in (entry.get("key_points_km") or []) if isinstance(p, str) and p.strip()]
    if points:
        return min(points, key=len).strip()
    return (entry.get("summary_km") or entry.get("title_km") or "").strip()


# ---------------------------------------------------------------- rendering
def render_card(entry: dict) -> Image.Image:
    img = Image.new("RGB", (W * SS, H * SS), ONYX)
    d = ImageDraw.Draw(img)

    f_quote = load_font(700, 40 * SS)
    f_brand = load_font(700, 19 * SS)
    f_attrib = load_font(400, 20 * SS)
    f_mono = ImageFont.truetype(font_path(400), 15 * SS)

    pad = 78 * SS
    inner = W * SS - pad * 2

    # Hairline inset border
    m = 32 * SS
    d.rectangle([m, m, W * SS - m, H * SS - m], outline=HAIRLINE, width=1 * SS)

    # Brand lockup: diamond echoing the site's section bullets, plus the name
    cx, cy, r = pad + 9 * SS, pad + 9 * SS, 9 * SS
    d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=CHAMPAGNE)
    d.text((pad + 28 * SS, pad - 2 * SS), "CKM CATERING", font=f_brand, fill=WHITE)

    category = (entry.get("category") or "").strip()
    if category:
        cw = d.textlength(category, font=f_attrib)
        d.text((W * SS - pad - cw, pad - 4 * SS), category, font=f_attrib, fill=CHAMPAGNE)

    # Headline: one key point, wrapped and vertically centred
    headline = pick_headline(entry)
    lines = wrap_clusters(headline, d, f_quote, inner, max_lines=4)
    line_h = int(40 * SS * 1.95)
    block_h = line_h * len(lines)
    y = (H * SS - block_h) // 2 - 10 * SS
    for line in lines:
        d.text((pad, y), line, font=f_quote, fill=WHITE)
        y += line_h

    # Attribution: the dish title, small, under a short rule
    rule_y = y + 18 * SS
    d.rectangle([pad, rule_y, pad + 64 * SS, rule_y + 2 * SS], fill=CHAMPAGNE)
    title = truncate_clusters((entry.get("title_km") or "").strip(), d, f_attrib, inner)
    d.text((pad, rule_y + 18 * SS), title, font=f_attrib, fill=SLATE)

    # Domain, bottom right
    dom = "ckmkh.com"
    dw = d.textlength(dom, font=f_mono)
    d.text((W * SS - pad - dw, H * SS - pad - 6 * SS), dom, font=f_mono, fill=SLATE)

    return img.resize((W, H), Image.LANCZOS)


def card_filename(entry: dict) -> str:
    return f"{entry.get('slug') or entry.get('id')}-card.png"


def write_card(entry: dict, out_dir: str = OUT_DIR) -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, card_filename(entry))
    render_card(entry).save(path, "PNG", optimize=True)
    return path


# ---------------------------------------------------------------- entry point
def load_entries():
    raw = json.load(io.open(PULSE_DATA, encoding="utf-8"))
    return raw if isinstance(raw, list) else raw.get("items") or raw.get("pulse") or []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", help="render one entry by slug or id")
    ap.add_argument("--all", action="store_true", help="rebuild every card")
    ap.add_argument("--sample", action="store_true", help="render the first 3 only")
    ap.add_argument("--out", default=OUT_DIR)
    args = ap.parse_args()

    print(f"[CARD] pillow raqm shaping: {features.check('raqm')}")
    if not features.check("raqm"):
        print("   [WARN] raqm is unavailable: Khmer subscripts will NOT stack.")
        print("          Windows wheels ship without it. Render in CI to verify.")

    entries = load_entries()
    if args.slug:
        entries = [e for e in entries if args.slug in (e.get("slug"), e.get("id"))]
        if not entries:
            print(f"[ERROR] no pulse entry matching {args.slug!r}")
            return 1
    elif args.sample:
        entries = entries[:3]
    elif not args.all:
        print("[ERROR] pass --slug, --all or --sample")
        return 1

    for e in entries:
        path = write_card(e, args.out)
        print(f"   wrote {path} ({os.path.getsize(path) // 1024} KB)")
    print(f"[CARD] {len(entries)} card(s) rendered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
