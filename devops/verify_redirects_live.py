"""Check every rule in public/_redirects against the live site, one request per rule.

Run this AFTER a deploy that touched public/_redirects. Comparing the file with dist/
is not a check of what the host applies: on 2026-11-14 e0c2ee5 took the file from 90
rules to 210, both pre-push checks compared it with dist/ and passed, and on
ckmkh.com every rule after the 100th returned 404 because Cloudflare stops reading the
file at its 101st dynamic rule (AGENTS.md section 3). Only a request to the live host
shows what it does.

For each rule this requests the source path without following redirects and compares
the status code and the Location header with what the file says. A dynamic rule is
probed with one representative path: `*` becomes `probe-x/` and each `:placeholder`
becomes `probe`, substituted into the target the way Cloudflare does (`:splat`).

Standard library only. Read-only: GET requests, nothing else.

Usage:
    python devops/verify_redirects_live.py [--base https://ckmkh.com] [--delay 0.1]

Exit status: 0 when every rule matches, 1 when any rule does not or a request fails.
"""

import argparse
import http.client
import os
import re
import sys
import time
import urllib.parse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REDIRECTS = os.path.join(ROOT, "public", "_redirects")
PLACEHOLDER = re.compile(r":([A-Za-z]\w*)")
# Cloudflare can treat non-browser clients differently (AGENTS.md section 18 records
# edge injection skipped for them), so the probe presents itself as a browser.
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")


def parse(path):
    """(line number, source, target, status) for every rule, in file order."""
    rules = []
    with open(path, encoding="utf-8") as fh:
        for n, raw in enumerate(fh.read().split("\n"), 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            tokens = re.split(r"\s+", re.sub(r"\s+#.*$", "", line))
            if len(tokens) not in (2, 3):
                sys.exit("line %d: expected 2 or 3 tokens, got %d -- fix the file first "
                         "(python devops/check_content.py)" % (n, len(tokens)))
            status = int(tokens[2]) if len(tokens) == 3 else 302
            rules.append((n, tokens[0], tokens[1], status))
    return rules


def probe(source, target):
    """(path to request, Location expected) for one rule."""
    path, expected = source, target
    if "*" in source:
        path = path.replace("*", "probe-x/", 1)
        expected = expected.replace(":splat", "probe-x/")
    for name in PLACEHOLDER.findall(source):
        path = path.replace(":" + name, "probe", 1)
        expected = expected.replace(":" + name, "probe")
    return path, expected


class Client:
    """One keep-alive connection, reopened when the server closes it."""

    def __init__(self, base):
        u = urllib.parse.urlsplit(base)
        if u.scheme != "https" or not u.hostname:
            sys.exit("--base must be an https:// origin, got %r" % base)
        self.host = u.hostname
        self.conn = None

    def get(self, path):
        for attempt in (1, 2):
            if self.conn is None:
                self.conn = http.client.HTTPSConnection(self.host, timeout=20)
            try:
                self.conn.request("GET", path, headers={"User-Agent": USER_AGENT})
                resp = self.conn.getresponse()
                resp.read()
                return resp.status, resp.getheader("Location")
            except (http.client.HTTPException, OSError):
                self.conn.close()
                self.conn = None
                if attempt == 2:
                    raise


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base", default="https://ckmkh.com")
    ap.add_argument("--file", default=REDIRECTS)
    ap.add_argument("--delay", type=float, default=0.1, help="seconds between requests")
    args = ap.parse_args()

    rules = parse(args.file)
    client = Client(args.base)
    origin = args.base.rstrip("/")
    bad = []
    for n, source, target, status in rules:
        path, expected = probe(source, target)
        url = origin + path
        try:
            got_status, location = client.get(path)
        except Exception as exc:  # report and keep going; the exit code carries it
            bad.append((n, source, "%d %s" % (status, expected), "request failed: %s" % exc))
            continue
        want = urllib.parse.urljoin(url, expected)
        have = urllib.parse.urljoin(url, location) if location else None
        ok = got_status == status and (status == 200 or have == want)
        if not ok:
            bad.append((n, path, "%d %s" % (status, expected),
                        "%d %s" % (got_status, location or "(no Location)")))
        time.sleep(args.delay)

    dynamic = sum(1 for _, s, _, _ in rules if "*" in s or PLACEHOLDER.search(s))
    print("%s: %d rules (%d static, %d dynamic) checked against %s"
          % (os.path.relpath(args.file, ROOT), len(rules), len(rules) - dynamic, dynamic, origin))
    print("match: %d | mismatch: %d" % (len(rules) - len(bad), len(bad)))
    for n, path, want, have in bad:
        print("  line %-4d %s\n            expected %s\n            got      %s" % (n, path, want, have))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
