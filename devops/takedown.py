"""Remove a pulse entry at a rights holder's request, in one command.

A photographer or a publisher gets in touch saying a photograph on ckmkh.com is theirs
(`src/pages/disclaimer.astro` routes them to Telegram or to the phone number, because
this site publishes no email address). The owner has to be able to finish the removal
and reply with proof inside five minutes, without reading any of this repository. That
is the whole design brief:

  - one command, one flag, either the slug or the source hostname (a hostname may match
    several entries -- one email about one blog usually means all of them);
  - it shows exactly what it will touch and does nothing until that is confirmed, and
    with neither --dry-run nor --yes it is a dry run, because the safe default for a
    destructive tool run under pressure is to print rather than to delete;
  - it ends by printing a reply the owner can paste into the email.

What it does NOT do, on purpose: commit, push or deploy. Those are the owner's actions
(AGENTS.md 1 treats a push as publishing), and the follow-up commands are printed instead.

Indexing is NOT reimplemented here. `notify_indexing.py` already owns IndexNow
submission and is imported; the --notify step calls into it. AGENTS.md 15 requires the
live URL to be checked before anything is submitted -- for a takedown that check is
inverted, so --notify refuses to submit while the page still returns 200, which would
tell Google to recrawl a page that is still there.

Usage:

    python devops/takedown.py --slug <slug|id|url>        # dry run, prints the plan
    python devops/takedown.py --source <hostname>         # dry run, may match several
    python devops/takedown.py --slug <slug> --yes         # actually removes
    python devops/takedown.py --notify <url>              # after the deploy is live

Exit codes: 0 success, 1 refused or a step failed, 2 nothing matched (so a mistyped
slug can never be read as "already gone").
"""

import argparse
import datetime
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "devops"))

import notify_indexing  # noqa: E402  -- reused rather than reimplemented

DATA_PATH = os.path.join(ROOT, "src", "data", "pulseData.json")
REDIRECTS_PATH = os.path.join(ROOT, "public", "_redirects")
BASE_URL = notify_indexing.BASE_URL
LIST_PATH = "/pulse/"
LIST_URL = BASE_URL + LIST_PATH
# Only files under this prefix are ever deleted. An image_url is model-adjacent data and
# a takedown runs under time pressure; nothing outside the pulse image folder is in scope.
IMAGE_PREFIX = "images/pulse/"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


# --------------------------------------------------------------------------- helpers

def plural(n, noun):
    return "%d %s%s" % (n, noun, "" if n == 1 else "s")


def load_entries():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        raw = f.read()
    return json.loads(raw), raw.endswith("\n")


def write_entries(entries, trailing_newline):
    """Write pulseData.json back in the exact shape the pipeline writes it.

    `fetch_catering_pulse.py` uses ensure_ascii=False and indent=2, and the file on disk
    round-trips byte-for-byte under those options. Anything else would show up as a
    whole-file diff around a one-entry deletion.
    """
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
        if trailing_newline:
            f.write("\n")


def normalise_slug(raw):
    """Accept a slug, an id, a path or a full URL -- whatever the owner has to hand."""
    s = (raw or "").strip()
    if "://" in s:
        s = urllib.parse.urlparse(s).path
    s = s.strip().strip("/")
    if s.startswith("pulse/"):
        s = s[len("pulse/"):]
    return s.strip("/")


def host_of(url):
    try:
        host = (urllib.parse.urlparse(url or "").hostname or "").lower()
    except ValueError:
        return ""
    return host[4:] if host.startswith("www.") else host


def match_entries(entries, slug=None, source=None):
    """Return [(index, entry)] for the removal target."""
    if slug:
        wanted = normalise_slug(slug)
        hits = [(i, e) for i, e in enumerate(entries) if e.get("slug") == wanted]
        if not hits:
            # The owner may well have the id alias (/pulse/pulse-31/) rather than the slug.
            hits = [(i, e) for i, e in enumerate(entries) if e.get("id") == wanted]
        return hits
    wanted_host = host_of(source if "://" in source else "https://" + source.strip())
    if not wanted_host:
        return []
    out = []
    for i, e in enumerate(entries):
        # Both fields, because they can differ: source_link is the article the Khmer
        # piece comments on, image_source_link is the page the photograph came from and
        # is the one a photographer's email will name. Missing either would leave an
        # entry behind after an email that named the site correctly.
        hosts = {host_of(e.get("source_link")), host_of(e.get("image_source_link"))}
        if any(h and (h == wanted_host or h.endswith("." + wanted_host)) for h in hosts):
            out.append((i, e))
    return out


def image_rel_path(entry):
    """Repo-relative path of the entry's own image file, or None.

    Returns None for an empty field and for an off-site URL: an https image_url is not
    a file this repository can delete, and saying so is more useful than a silent skip.
    """
    img = (entry.get("image_url") or "").strip()
    if not img.startswith("/"):
        return None
    rel = img.lstrip("/")
    if not rel.startswith(IMAGE_PREFIX):
        return None
    return os.path.join("public", *rel.split("/"))


def orphan_files(entry, deleted_rel):
    """Other files in the pulse image folder that carry this entry's slug.

    A rehosted photograph is written as `<slug>.webp` while the entry's own share card
    stays on disk as `<slug>-card.png`, so removing the entry usually leaves one behind.
    They are listed, never deleted: the card is CKM's own render and nobody has claimed
    it, and a takedown script that deletes files nobody asked about is a worse tool.
    """
    slug = entry.get("slug") or ""
    folder = os.path.join(ROOT, "public", *IMAGE_PREFIX.strip("/").split("/"))
    if not slug or not os.path.isdir(folder):
        return []
    keep = os.path.basename(deleted_rel) if deleted_rel else None
    out = []
    for name in sorted(os.listdir(folder)):
        if name.startswith(slug) and name != keep:
            out.append("public/%s%s" % (IMAGE_PREFIX, name))
    return out


def redirect_line(source_path):
    """One `_redirects` line to `/pulse/`, in the file's existing column style.

    Every /pulse/ redirect already in the file separates the columns with two spaces,
    and the slash-less variant carries a third space so the target column still lines
    up. Matching that exactly keeps the diff to the lines actually added.
    """
    sep = "  " if source_path.endswith("/") else "   "
    return "%s%s%s  301" % (source_path, sep, LIST_PATH)


def redirect_sources(text):
    """Every source path already declared in `_redirects`."""
    out = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if parts:
            out.add(parts[0])
    return out


def plan_redirects(text, slugs):
    """(lines to append, [(old alias line, new alias line)]) -- computed, not written."""
    existing = redirect_sources(text)
    additions = []
    for slug in slugs:
        with_slash = "/pulse/%s/" % slug
        if with_slash in existing:
            continue  # already redirected; running this twice must be a no-op
        additions.append(redirect_line(with_slash))
        additions.append(redirect_line("/pulse/%s" % slug))

    # The /pulse/pulse-NN/ id aliases point at the slug URL that is about to disappear.
    # Left alone they would 301 into a 404 -- the alias exists so an indexed URL never
    # breaks (AGENTS.md 15), so it has to follow the page to the listing instead.
    dead_targets = {"/pulse/%s/" % s for s in slugs}
    rewrites = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[1] in dead_targets and not line.strip().startswith("#"):
            rewrites.append((line, redirect_line(parts[0])))
    return additions, rewrites


def apply_redirects(additions, rewrites, slugs, reason):
    text = open(REDIRECTS_PATH, "r", encoding="utf-8").read()
    if rewrites:
        # Line by line, not a whole-file replace: a substring replace can hit a line
        # nobody looked at.
        mapping = dict(rewrites)
        text = "\n".join(mapping.get(line, line) for line in text.split("\n"))
    if additions:
        today = datetime.date.today().isoformat()
        # One hostname can match a dozen entries, and a comment line naming all of them
        # is unreadable next to the two-column rules it introduces.
        what = ", ".join(slugs) if len(slugs) <= 2 else "%d pulse pages" % len(slugs)
        header = "# Takedown %s: %s removed at the rights holder's request" % (today, what)
        if reason:
            header += " (%s)" % reason
        text = text.rstrip("\n") + "\n\n" + header + "\n" + "\n".join(additions) + "\n"
    with open(REDIRECTS_PATH, "w", encoding="utf-8") as f:
        f.write(text)


def http_head(url):
    """(status, location) without following the redirect. Errors return (None, None)."""
    class _NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None

    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=15) as resp:
            return resp.status, resp.headers.get("Location")
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location") if e.headers else None
    except Exception as e:
        print("  could not reach %s: %s" % (url, e))
        return None, None


# ------------------------------------------------------------------------ reporting

def describe(matches, additions, rewrites):
    print("Affected entries: %d" % len(matches))
    for _, e in matches:
        rel = image_rel_path(e)
        print("")
        print("  id           %s" % e.get("id"))
        print("  slug         %s" % e.get("slug"))
        print("  page         %s/pulse/%s/" % (BASE_URL, e.get("slug")))
        print("  title (km)   %s" % e.get("title_km"))
        print("  source       %s" % (e.get("source_link") or "(none recorded)"))
        print("  source title %s" % (e.get("source_title_en") or "(none recorded)"))
        print("  photo credit %s" % (e.get("image_source_link") or "(none recorded)"))
        if rel:
            full = os.path.join(ROOT, rel)
            if os.path.exists(full):
                print("  image file   %s (%d bytes) -- will be DELETED"
                      % (rel.replace(os.sep, "/"), os.path.getsize(full)))
            else:
                print("  image file   %s -- already absent" % rel.replace(os.sep, "/"))
        else:
            img = (e.get("image_url") or "").strip()
            print("  image file   %s" % ("none to delete (off-site: %s)" % img if img
                                         else "none recorded"))
        for other in orphan_files(e, rel):
            print("  also on disk  %s -- NOT deleted (our own render, no rights claim)"
                  % other)
    print("")
    print("public/_redirects: %d line(s) to append, %d alias line(s) to retarget"
          % (len(additions), len(rewrites)))
    for line in additions:
        print("  + %s" % line)
    for old, new in rewrites:
        print("  ~ %s" % old.strip())
        print("    -> %s" % new)


def print_reply(matches, indexed):
    """The email reply. Every sentence in it must be true when it is printed."""
    today = datetime.date.today().isoformat()
    print("")
    print("=" * 78)
    print("REPLY TO THE RIGHTS HOLDER (Telegram, email, wherever they wrote from)")
    print("=" * 78)
    print("Thank you for your message. The material has been removed.")
    print("")
    print("Removed on %s:" % today)
    for _, e in matches:
        print("  - Page: %s/pulse/%s/ (deleted; now permanently redirected to %s)"
              % (BASE_URL, e.get("slug"), LIST_URL))
        rel = image_rel_path(e)
        if rel:
            print("    Image: %s/%s (file deleted from the server)"
                  % (BASE_URL, rel.replace(os.sep, "/")[len("public/"):]))
        if e.get("image_source_link"):
            print("    Photograph credited to: %s" % e.get("image_source_link"))
        if (e.get("source_link") or "").startswith("http"):
            print("    Article referenced: %s" % e.get("source_link"))
    print("")
    print("The page has been removed from our content data and the image file has been")
    print("deleted. The old address returns a permanent redirect to our index page.")
    if indexed:
        print("We have also asked Google and Bing to recrawl the removed address so it")
        print("drops out of their results.")
    print("")
    print("If any other material of yours appears on ckmkh.com, please reply to this")
    print("message and it will be removed the same way.")
    print("=" * 78)


def print_followups(slugs, reason=""):
    print("")
    print("FOLLOW-UP -- nothing below has been run; this script does not deploy.")
    print("")
    print("  1. Check the content gate and refresh the generated indexes:")
    print("       python devops/check_content.py --strict")
    print("       python devops/generate_llms_txt.py")
    print("  2. Commit and push (the Publish workflow purges the edge and resubmits):")
    print('       git add src/data/pulseData.json public/_redirects public/images/pulse '
          'public/llms.txt public/llms-full.txt')
    print('       git commit -m "fix(pulse): remove %s at the rights holder\'s request" \\'
          % ", ".join(slugs))
    print('         -m "Root Cause: %s" \\' % (reason or
          "a third-party photograph was rehosted on a pulse page."))
    print('         -m "Impact: %s and the image file(s)." \\' % plural(len(slugs), "pulse page"))
    print('         -m "Verification: python devops/check_content.py --strict"')
    print("       git push")
    print("  3. Once Cloudflare Pages has rebuilt, confirm the removal and tell the")
    print("     search engines (this checks the URL is really gone before submitting):")
    for slug in slugs:
        print("       python devops/takedown.py --notify %s/pulse/%s/" % (BASE_URL, slug))
    print("  4. Optional, and the fastest visible result: Search Console > Removals >")
    print("     New request, for the same URL. That hides it from Google within hours,")
    print("     which is what the rights holder actually checks.")


# ----------------------------------------------------------------------------- modes

def do_notify(url):
    """Post-deploy step: prove the page is gone, then submit through notify_indexing."""
    status, location = http_head(url)
    print("Live check: %s -> HTTP %s%s"
          % (url, status, (" -> %s" % location) if location else ""))
    if status is None:
        print("::error::Could not reach the URL. Nothing submitted.")
        return 1
    if status == 200:
        print("::error::The page is still live. Either the deploy has not finished or the")
        print("         removal was never pushed. Submitting now would ask Google to")
        print("         recrawl a page that is still there. Nothing submitted.")
        return 1
    if status not in (301, 308, 404, 410):
        print("::error::Unexpected status %s; not submitting." % status)
        return 1

    # IndexNow needs no credential, so it is the one step that works from the owner's
    # machine. The Cloudflare purge and the Search Console sitemap need CI-only secrets
    # (AGENTS.md 16) and are done by the Publish workflow on push.
    ok = notify_indexing.submit_indexnow([url, LIST_URL])
    if not ok:
        print("::error::IndexNow did not accept the submission.")
        return 1
    print("")
    print("Submitted to IndexNow: %s and %s" % (url, LIST_URL))
    print("The edge cache purge and the Search Console sitemap resubmission are done by")
    print("the Publish workflow on push; they need secrets that only CI holds.")
    print("")
    print("You may now add this sentence to the reply, and it is true:")
    print('  "We have also asked Google and Bing to recrawl the removed address."')
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ap = argparse.ArgumentParser(
        description="Remove a pulse entry at a rights holder's request.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--slug", help="pulse slug, id, path or full URL")
    g.add_argument("--source", help="source hostname, e.g. thewoksoflife.com "
                                    "(may match several entries)")
    g.add_argument("--notify", metavar="URL",
                   help="post-deploy step: verify the URL is gone, then submit it")
    ap.add_argument("--yes", action="store_true", help="apply without the prompt")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the plan only (the default when --yes is absent)")
    ap.add_argument("--reason", default="",
                    help="short note recorded in the _redirects comment")
    args = ap.parse_args(argv)

    # Every path below is CWD-relative in the rest of this repo's tooling, and the owner
    # will run this from wherever the email was read.
    os.chdir(ROOT)

    if args.notify:
        return do_notify(args.notify)

    entries, trailing_newline = load_entries()
    matches = match_entries(entries, slug=args.slug, source=args.source)
    if not matches:
        what = args.slug or args.source
        print("::error::Nothing in %s matches %r." % (DATA_PATH, what))
        print("A typo must not look like a completed takedown, so this is a failure.")
        if args.slug:
            print("Known slugs containing that string:")
            needle = normalise_slug(args.slug).lower()
            near = [e.get("slug") for e in entries
                    if needle and needle in (e.get("slug") or "").lower()]
            for s in near[:10] or ["(none)"]:
                print("  %s" % s)
        else:
            hosts = sorted({host_of(e.get("source_link")) for e in entries} - {""})
            print("Source hostnames present: %s" % ", ".join(hosts))
        return 2

    slugs = [e.get("slug") for _, e in matches]
    redirects_text = open(REDIRECTS_PATH, "r", encoding="utf-8").read()
    additions, rewrites = plan_redirects(redirects_text, slugs)

    print("Takedown plan%s" % ("" if args.yes else " (DRY RUN -- nothing changed yet)"))
    print("")
    describe(matches, additions, rewrites)

    if not args.yes:
        # Default and --dry-run both show the plan and change nothing. The difference is
        # that the default then offers to go ahead, so the ordinary path is one command:
        # read the list, type yes. --dry-run never prompts, so it is safe in a script.
        if args.dry_run or not sys.stdin.isatty():
            print("")
            print("Dry run: no file was changed. Re-run with --yes to apply.")
            return 0
        answer = input("\nType 'yes' to remove the %d entry/entries above, or anything "
                       "else to leave them alone: " % len(matches))
        if answer.strip().lower() != "yes":
            print("Not confirmed. No file was changed.")
            return 0

    # 1. the data file -- do this first, so a later failure leaves the page unreachable
    #    rather than leaving a live page with its image deleted.
    drop_index = {i for i, _ in matches}
    remaining = [e for i, e in enumerate(entries) if i not in drop_index]
    write_entries(remaining, trailing_newline)
    print("Removed %s from %s (%d remain)."
          % (plural(len(matches), "entry").replace("entrys", "entries"),
             os.path.relpath(DATA_PATH, ROOT).replace(os.sep, "/"), len(remaining)))

    # 2. the image files
    still_used = {(e.get("image_url") or "").strip() for e in remaining}
    for _, e in matches:
        rel = image_rel_path(e)
        if not rel:
            continue
        if (e.get("image_url") or "").strip() in still_used:
            print("Kept %s -- another entry still points at it." % rel.replace(os.sep, "/"))
            continue
        full = os.path.join(ROOT, rel)
        if os.path.exists(full):
            os.remove(full)
            print("Deleted %s" % rel.replace(os.sep, "/"))
        else:
            print("Already absent: %s" % rel.replace(os.sep, "/"))

    # 3. the redirects
    apply_redirects(additions, rewrites, slugs, args.reason)
    print("Updated public/_redirects (%d added, %d retargeted)."
          % (len(additions), len(rewrites)))

    print_reply(matches, indexed=False)
    print_followups(slugs, args.reason)
    print("")
    print("Do not send the reply until step 2 is pushed and the redirect is live.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
