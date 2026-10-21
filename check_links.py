#!/usr/bin/env python3
"""Check the links on a page and keep its page/links.csv up to date.

    check_links.py taiwan                 check every link on the Taiwan page
    check_links.py taiwan --report r.json also write every attempt, for a closer look

Each link is fetched as a browser would (following redirects, up to three tries) and given a verdict:
ok, moved-ok (it answered after redirecting elsewhere), soft-404 (it answered with a "not found" page,
or by dropping you on the site's front page), http-error, dns (the name no longer exists - confirmed with
Google's public DNS), unreachable, tls, blocked (403/429, often a bot wall) or proxy (the checking
machine's own network refused it).

page/links.csv keeps what has been decided by hand: a fixed link (with its old address in url and the
new one in replacement) stays fixed, and a link marked broken stays broken unless it now answers. For
the rest, a clear answer sets the status - ok, or broken for 404/410 and names that no longer exist -
and anything unclear (timeouts, 5xx, bot walls, certificate errors) is left for a person to judge: an
existing status is kept, a new link is entered as unchecked. The checked date is updated either way.
It is gentle with servers: one request at a time, at least --gap seconds (default 3) between any
two, at least --host-gap seconds (default 10) between two to the same host - the queue is ordered so
other hosts go in between - and a failing link is tried only once more, at least --retry-gap seconds
(default 30) later. A page of 270 links takes about a quarter of an hour.

A site that blocks or throttles foreign visitors can look dead from one machine and be fine from another,
so a broken verdict on anything but a 404/410 or a vanished name is worth a second look.
"""
import csv, glob, json, os, re, subprocess, sys, tempfile, time, urllib.parse, urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
LINK = re.compile(r"\[([^\[\]]+)\]\(([^)\s]+)\)")
BARE = re.compile(r"(?<![\"'=(>\]])\bhttps?://[^\s<>)\]]+")
NOT_FOUND = re.compile(r"(404|page not found|not be found|no longer available|does not exist|找不到|查無|頁面不存在|無此頁面|error 404)", re.I)

def urls_of(d):
    """{url: [where, ...]} for the page's markdown, books.csv and config.json."""
    found = {}
    def add(u, where):
        u = u.strip().rstrip(".,;")
        if u.startswith(("http://", "https://")):
            found.setdefault(u, []).append(where)
    page = os.path.join(d, "page")
    for md in glob.glob(os.path.join(page, "*.md")):
        section = ""
        for n, line in enumerate(open(md, encoding="utf-8"), 1):
            if line.startswith("# "):
                section = line[2:].strip()
            for m in LINK.finditer(line):
                add(m.group(2), f"{section} (line {n}): {m.group(1)[:70]}")
            for m in BARE.finditer(LINK.sub("", line)):
                add(m.group(0), f"{section} (line {n})")
    books = os.path.join(page, "books.csv")
    if os.path.exists(books):
        for n, r in enumerate(csv.DictReader(open(books, encoding="utf-8")), 2):
            for part in (r.get("links") or "").split(" ; "):
                if part.strip():
                    add(part.split()[-1], f"books.csv row {n}: {r['title'][:70]}")
            for m in LINK.finditer(r.get("notes") or ""):
                add(m.group(2), f"books.csv row {n} notes: {r['title'][:60]}")
    cfg = json.load(open(os.path.join(page, "config.json"), encoding="utf-8"))
    for k in ("lede", "credits"):
        for p in cfg.get(k, []):
            for m in LINK.finditer(p):
                add(m.group(2), f"config {k}: {m.group(1)[:60]}")
    return found

def dns_exists(host):
    """Ask Google's public DNS whether the name exists at all (Status 3 = NXDOMAIN)."""
    try:
        q = urllib.request.Request(f"https://dns.google/resolve?name={urllib.parse.quote(host)}&type=A", headers={"User-Agent": UA})
        j = json.load(urllib.request.urlopen(q, timeout=20))
        return j.get("Status") != 3, j.get("Status"), [a.get("data") for a in j.get("Answer", [])]
    except Exception as e:
        return None, str(e), []

def fetch(url):
    with tempfile.NamedTemporaryFile(delete=False) as f:
        body = f.name
    cmd = ["curl", "-sS", "-g", "-L", "--max-redirs", "10", "--max-time", "40", "--connect-timeout", "20", "-A", UA,
           "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "-H", "Accept-Language: en,zh-TW;q=0.8",
           "--compressed", "-o", body, "-w", "%{http_code}\t%{url_effective}\t%{num_redirects}\t%{content_type}", url]
    p = subprocess.run(cmd, capture_output=True, text=True)
    code, final, redirs, ctype = (p.stdout.split("\t") + ["", "", "", ""])[:4]
    try:
        text = open(body, "rb").read(400000).decode("utf-8", "replace")
    except Exception:
        text = ""
    os.unlink(body)
    title = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
    return {"code": int(code or 0), "final": final, "redirects": int(redirs or 0), "type": ctype, "curl_exit": p.returncode,
            "error": p.stderr.strip()[:300], "title": re.sub(r"\s+", " ", title.group(1)).strip()[:200] if title else "",
            "notfound_text": bool(NOT_FOUND.search(re.sub(r"<script.*?</script>", "", text[:60000], flags=re.S | re.I))) and len(text) < 60000,
            "size": len(text)}

def verdict(url, a):
    if a["curl_exit"] == 6:
        return "dns"
    if "CONNECT tunnel failed" in a["error"] or a["curl_exit"] == 56 and "403" in a["error"]:
        return "proxy"
    if a["curl_exit"] in (35, 51, 58, 60, 90, 91):
        return "tls"
    if a["code"] == 0:
        return "unreachable"
    if a["code"] in (401, 403, 429, 503) and a["code"] != 404:
        return "blocked" if a["code"] != 503 else "http-error"
    if a["code"] >= 400:
        return "http-error"
    o, f = urllib.parse.urlsplit(url), urllib.parse.urlsplit(a["final"])
    deep = o.path.strip("/") or o.query
    if deep and f.path.strip("/") in ("", "index.html", "index.php", "index.jsp", "default.aspx", "en", "zh-tw") and not f.query and a["redirects"]:
        return "soft-404"                      # a deep link that now lands on the front page
    if a["notfound_text"] and "html" in a["type"]:
        return "soft-404"
    if a["redirects"] and (o.netloc.lower().removeprefix("www.") != f.netloc.lower().removeprefix("www.")
                           or o.path.rstrip("/") != f.path.rstrip("/")):
        return "moved-ok"
    return "ok"

class Polite:
    """Hands out one fetch at a time, never sooner than `gap` seconds after the last request, nor
    `host_gap` seconds after the last request to the same host."""
    def __init__(self, gap, host_gap):
        self.gap, self.host_gap, self.last, self.by_host = gap, host_gap, 0.0, {}

    def ready_in(self, url):
        now, host = time.monotonic(), urllib.parse.urlsplit(url).hostname
        return max(self.last + self.gap - now, self.by_host.get(host, -1e9) + self.host_gap - now, 0)

    def fetch(self, url):
        time.sleep(self.ready_in(url))
        try:
            return fetch(url)
        finally:
            self.last = time.monotonic(); self.by_host[urllib.parse.urlsplit(url).hostname] = self.last


def settled(a):
    """No point asking again: it answered, or said plainly that the page is gone."""
    return a["verdict"] in ("ok", "moved-ok", "soft-404", "proxy") or (a["verdict"] == "http-error" and a["code"] in (404, 410))


def check_all(urls, gap=3, host_gap=10, retry_gap=30):
    """Check the URLs one at a time. A failure is tried once more, at least retry_gap seconds later,
    and only a failure that repeats counts. The queue picks whichever URL's host can be asked soonest."""
    polite = Polite(gap, host_gap)
    queue = [(0.0, u) for u in urls]                     # (not before, url)
    tries = {u: [] for u in urls}
    done = 0
    while queue:
        now = time.monotonic()
        queue.sort(key=lambda q: max(q[0] - now, polite.ready_in(q[1])))
        not_before, u = queue.pop(0)
        time.sleep(max(not_before - time.monotonic(), 0))
        a = polite.fetch(u); a["verdict"] = verdict(u, a); tries[u].append(a)
        if not settled(a) and len(tries[u]) < 2:
            queue.append((time.monotonic() + retry_gap, u))
            continue
        done += 1
        print(f"  {done}/{len(urls)} {a['verdict']:<11} {u[:90]}", flush=True)
    return {u: finish(u, t) for u, t in tries.items()}


def finish(url, tries):
    v = tries[-1]["verdict"]
    rec = {"url": url, "verdict": v, "attempts": tries}
    if v == "dns":
        host = urllib.parse.urlsplit(url).hostname
        exists, status, answers = dns_exists(host)
        rec["dns_check"] = {"exists": exists, "status": status, "answers": answers}
        if exists:                             # the name is real: the sandbox could not resolve it
            rec["verdict"] = "unreachable"
    return rec


FIELDS = ["url", "status", "checked", "replacement", "note"]

def clear_status(rec):
    """ok / broken when the check is unambiguous, otherwise None (a person should judge)."""
    v, a = rec["verdict"], rec["attempts"][-1]
    if v in ("ok", "moved-ok"):
        return "ok"
    if v == "dns" or (v == "http-error" and a["code"] in (404, 410)):
        return "broken"
    return None

if __name__ == "__main__":
    import argparse, datetime
    ap = argparse.ArgumentParser()
    ap.add_argument("page"); ap.add_argument("--report")
    ap.add_argument("--gap", type=float, default=3, help="seconds between any two requests")
    ap.add_argument("--host-gap", type=float, default=10, help="seconds between two requests to the same host")
    ap.add_argument("--retry-gap", type=float, default=30, help="seconds before a failing link is tried again")
    args = ap.parse_args()
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.page.strip("/"))
    path = os.path.join(d, "page", "links.csv")
    old = {r["url"]: r for r in csv.DictReader(open(path, encoding="utf-8"))} if os.path.exists(path) else {}
    by_new = {r["replacement"]: r for r in old.values() if r.get("replacement")}
    where = urls_of(d)
    print(len(where), "distinct URLs,", sum(map(len, where.values())), "uses", flush=True)
    results = check_all(list(where), args.gap, args.host_gap, args.retry_gap)
    today = datetime.date.today().isoformat()
    rows = {u: r for u, r in old.items()}
    for u, rec in results.items():
        clear = clear_status(rec)
        a = rec["attempts"][-1]
        seen = f'{rec["verdict"]}: HTTP {a["code"]}' + (f' -> {a["final"]}' if a["final"] and a["final"] != u else "")
        if u in by_new:                                 # a repaired link: check the new address, keep the record
            r = by_new[u]; r["checked"] = today
            if clear == "broken":
                r["note"] = f"the new address failed too ({seen})"
            continue
        r = rows.get(u) or {"url": u, "status": "unchecked", "replacement": "", "note": ""}
        if clear:
            r["status"] = clear
        r["checked"] = today
        if r["status"] != "fixed" and not clear:
            r["note"] = (r.get("note") or "").split(" | last check: ")[0] + f" | last check: {seen}"
        rows[u] = r
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader()
        for r in sorted(rows.values(), key=lambda r: (r["status"] != "broken", r["url"])):
            w.writerow({k: r.get(k, "") for k in FIELDS})
    if args.report:
        for u, rec in results.items():
            rec["where"] = where[u]
        json.dump(list(results.values()), open(args.report, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    from collections import Counter
    print("verdicts:", Counter(r["verdict"] for r in results.values()).most_common())
    print("links.csv:", Counter(r["status"] for r in rows.values()).most_common())
