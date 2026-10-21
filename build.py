#!/usr/bin/env python3
"""Build the Primary Sources pages: one index.html in each page's directory.

    build.py                      build every page (every directory with a page/config.json)
    build.py korea taiwan         build only these
    build.py --no-bump            rebuild without new version numbers

Each page's directory holds its own content; everything they share is here and in site/:

    <dir>/page/config.json  title, the opening paragraph(s), the credits at the foot, the colours, and the
                            labels for the book table (see CONFIG below)
    <dir>/page/*.md         the list itself (the one markdown file in page/). Edit it and build again.
    <dir>/page/books.csv    the books online, one row a book (optional; see the books section below)
    <dir>/page/version.txt  the build number shown at the foot of the page, raised by one each build
    site/page.css           the look of every page (serif; the layout of the Japan page)
    site/books.*            the table the books are shown in: search, tags, filters, sorting, an entry in full

They follow the design of the Modern Japanese History page (github.com/kmlawson/japan-bib).

The markdown: each `# heading` becomes a section of the page with a button of its own at the top, in the
order they are written. Nothing but the buttons is shown when the page opens: pressing a button reveals
that section, pressing it again - or clicking the section's own heading - hides it. The first `# heading`
is the page title; the list of sections underneath it is left out, since the buttons say the same thing,
and the "See also" links after it are set as one line under the title. `## heading` is a sub-heading.

The books: a line of the markdown reading `<!--books-->` becomes the table of books, and the section it is
in becomes the books section - like the Japan page's Digitized Books, it is always on the page, after the
other sections, with a solid button of its own at the end of the row. The rows of books.csv are written
into the page as JSON; there is no database. Its columns:

    author, title, year     as they should be shown; the first four-digit number in year sorts and filters
    imprint                 place and publisher, shown in the entry
    language                English, German ... for the Language filter
    links                   one or more copies separated by " ; ", each a URL with an optional label before
                            it ("Vol 1 https://... ; Vol 2 https://...")
    tags                    separated by " ; ". Each tag becomes a button above the table; tags that are
                            date ranges (1886-1942) are set in a row of their own as periods
    notes                   shown under the title; markdown links and *italics* work

A bullet ending in the marker `<!--pills-->`, at any depth, becomes bubbles: if it ends in a colon its
indented list turns into a row of small bubbles, otherwise the bullet itself becomes one. Any other
indented list stays an ordinary list, nested as deep as it is indented.
"""
import argparse, csv, datetime, glob, html, json, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "site")
REPO = "https://github.com/kmlawson/primary-sources/tree/master/"
BOOKS_MARK = "<!--books-->"     # a line of the markdown that reads this becomes the table of books
PILLS_MARK = "<!--pills-->"     # put this at the end of a bullet and its indented list becomes bubbles

# page/config.json: what each page sets for itself. Markdown links and *italics* are allowed in lede and credits.
CONFIG = {
    "title": None,              # the page title; the first # heading of the markdown is used if this is left out
    "description": "",          # one sentence for <meta name="description">
    "lede": [],                 # the opening paragraph(s), under the title
    "credits": [],              # the paragraphs at the foot of the page
    "books_placeholder": "Search author, title, notes…",
    "export": "books",          # the name the exported CSV and BibTeX files start with
    "colors": {                 # the page's accent: buttons, links, highlights. Light and dark.
        "light": {"accent": "#12539e", "accent-ink": "#fff", "hit": "#cfe3ff", "link": "#1257a8"},
        "dark": {"accent": "#5aa2ff", "accent-ink": "#0f1621", "hit": "#204a7a", "link": "#8cc2ff"},
    },
}


class Page:
    def __init__(self, d):
        self.dir = os.path.join(ROOT, d)
        self.name = d
        cfg = json.load(open(os.path.join(self.dir, "page", "config.json"), encoding="utf-8"))
        self.cfg = {**CONFIG, **cfg}
        mds = sorted(glob.glob(os.path.join(self.dir, "page", "*.md")))
        if len(mds) != 1:
            sys.exit(f"{d}/page/ should hold exactly one markdown file, not {len(mds)}")
        self.md = mds[0]
        self.books = os.path.join(self.dir, "page", "books.csv")
        self.version_file = os.path.join(self.dir, "page", "version.txt")
        self.out = os.path.join(self.dir, "index.html")

    def version(self, bump=True):
        """1.0001, 1.0002 ... one step for each build meant for the site. --no-bump leaves it alone."""
        n = 0
        if os.path.exists(self.version_file):
            m = re.search(r"(\d+)\s*$", open(self.version_file, encoding="utf-8").read().strip())
            n = int(m.group(1)) if m else 0
        if bump:
            n = n % 9999 + 1
            open(self.version_file, "w", encoding="utf-8").write(f"{n}\n")
        return f"1.{max(n, 1):04d}"


# ---------------------------------------------------------------- markdown
LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
BARE = re.compile(r"(?<![\"'=(>])\bhttps?://[^\s<>)\]]+")
BOLD = re.compile(r"\*\*([^*]+)\*\*")
ITAL = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")
CODE = re.compile(r"`([^`]+)`")
ITAL_LINK = re.compile(r"(?<!\*)\*\[([^\]]+)\]\(([^)\s]+)\)\*(?!\*)")


def inline(text):
    """One line of markdown to HTML: links (plain or bare), bold, italic, code."""
    text = ITAL_LINK.sub(r"[*\1*](\2)", text)   # *[title](url)*: the italics go inside the link
    out, last = [], 0
    for m in LINK.finditer(text):
        out.append(esc_runs(text[last:m.start()]))
        out.append(f'<a href="{html.escape(m.group(2), quote=True)}" target="_blank" rel="noopener">'
                   f'{esc_runs(m.group(1))}</a>')
        last = m.end()
    out.append(esc_runs(text[last:]))
    return "".join(out)


def esc_runs(text):
    """Escape, then mark up what is left: bare URLs become links, *word* italic, **word** bold.
    A `code` span is set as it is written, with nothing inside it turned into a link."""
    parts = CODE.split(text)          # odd items are the insides of code spans
    out = []
    for i, part in enumerate(parts):
        t = html.escape(part)
        if i % 2:
            out.append(f"<code>{t}</code>")
            continue
        t = BARE.sub(lambda m: f'<a href="{m.group(0)}" target="_blank" rel="noopener">{m.group(0)}</a>', t)
        t = BOLD.sub(r"<strong>\1</strong>", t)
        t = ITAL.sub(r"<em>\1</em>", t)
        out.append(t)
    return "".join(out)


def pill_item(text):
    """A nested item under a heading that ends in a colon: the link becomes a small bubble, and
    whatever the line says after it stays beside the bubble as a quiet note."""
    m = LINK.match(text.strip())
    if not m:
        return "<li>" + inline(text) + "</li>"
    rest = text.strip()[m.end():].lstrip(" -–—–")
    note = f'<span class="pill-note">{inline(rest)}</span>' if rest.strip() else ""
    return (f'<li><a class="pill-link" href="{html.escape(m.group(2), quote=True)}" target="_blank" '
            f'rel="noopener">{esc_runs(m.group(1))}</a>{note}</li>')


def render(lines, books=""):
    """A section's body: bullet lists (nested to any depth), sub-headings and paragraphs.

    A bullet ending in the marker <!--pills--> becomes bubbles, at any depth: if its text ends in a
    colon, its indented list becomes a row of small bubbles (ul.pills); otherwise the bullet itself is
    the bubble, and anything indented under it stays an ordinary list beneath it. The marker itself
    never shows. A line reading <!--books--> is replaced by the table of books."""
    out, para, items = [], [], []          # items: [(indent, text), ...] of the list being read

    def close_para():
        if para:
            out.append("<p>" + inline(" ".join(para).strip()) + "</p>")
            para.clear()

    def tree():
        """The bullets read so far as nodes {text, mark, kids}; a bullet is nested under the one
        above it when it is indented further, whatever the number of spaces."""
        root = {"kids": []}
        stack = [(-1, root)]
        for indent, text in items:
            while indent <= stack[-1][0]:
                stack.pop()
            node = {"text": text.replace(PILLS_MARK, "").rstrip(), "mark": PILLS_MARK in text, "kids": []}
            stack[-1][1]["kids"].append(node)
            stack.append((indent, node))
        return root["kids"]

    def own_pill(n):
        return n["mark"] and not n["text"].endswith(":")   # the bullet itself is the bubble

    def item(n, as_pill):
        head = pill_item(n["text"]) if as_pill else "<li>" + inline(n["text"]) + "</li>"
        if not n["kids"]:
            out.append(head)
            return
        out.append(head[:-len("</li>")])   # the nested list lives inside its parent item
        sub(n["kids"], n["mark"])
        out.append("</li>")

    def sub(kids, pills):
        out.append('<ul class="pills">' if pills else "<ul>")
        for k in kids:
            if not pills and own_pill(k):
                out.append('<li class="pill-own"><ul class="pills">' + pill_item(k["text"]) + "</ul>")
                if k["kids"]:
                    sub(k["kids"], False)
                out.append("</li>")
            else:
                item(k, pills)
        out.append("</ul>")

    def close_lists():
        """Write out the list just read. A top-level bubble stands on its own, outside any list."""
        run = []
        def flush():
            if run:
                sub(run, False)
                run.clear()
        for n in tree():
            if own_pill(n):
                flush()
                out.append('<ul class="pills">' + pill_item(n["text"]) + "</ul>")
                if n["kids"]:
                    sub(n["kids"], False)
            else:
                run.append(n)
        flush()
        items.clear()

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            close_para()
            continue
        if line.strip() == BOOKS_MARK:
            close_para(); close_lists()
            out.append(books)
            continue
        m = re.match(r"^(\s*)[-*+]\s+(.*)$", line)
        if m:
            close_para()
            items.append((len(m.group(1).expandtabs(4)), m.group(2)))
            continue
        m = re.match(r"^(#{2,6})\s+(.*)$", line)
        if m:
            close_para(); close_lists()
            level = min(len(m.group(1)) + 1, 6)        # ## -> h3, ### -> h4
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            continue
        close_lists()
        para.append(line.strip())
    close_para(); close_lists()
    return "\n".join(out)


def sections(md):
    """[(heading, [lines]), ...] - the first one is the page title and whatever follows it."""
    out, head, body = [], None, []
    for line in md.splitlines():
        m = re.match(r"^#\s+(.*)$", line)
        if m:
            if head is not None or body:
                out.append((head, body))
            head, body = m.group(1).strip(), []
        else:
            body.append(line)
    if head is not None or body:
        out.append((head, body))
    return out


def slug(s):
    return "s-" + re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def also_line(lines):
    """The "See also" list under the title, as one centred line of links for the head of the page."""
    links = [inline(m.group(1)) for m in (re.match(r"^[-*+]\s+(.*)$", l.strip()) for l in lines) if m]
    if not links:
        return ""
    return '<p class="also">' + ' <span class="sep">·</span> '.join(links) + "</p>"


def split_intro(lines):
    """The title section: its leading bullet list repeats the buttons, so it is dropped; the rest
    (the "See also" links) is kept for the head of the page."""
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    while i < len(lines) and re.match(r"^\s*[-*+]\s+", lines[i]):
        i += 1
    return lines[i:]


# ----------------------------------------------------------------- the books
def read_books(path):
    """The rows of books.csv as the table wants them: links split into {label, url}, tags into a list,
    and the first year as a number for sorting and the year filter."""
    out = []
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            get = lambda k: (r.get(k) or "").strip()
            links = []
            for part in get("links").split(" ; "):
                part = part.strip()
                if part:
                    label, _, url = part.rpartition(" ")
                    links.append({"label": label.strip(), "url": url})
            m = re.search(r"\d{4}", get("year"))
            out.append({"author": get("author"), "title": get("title"), "year": get("year"),
                        "year_num": int(m.group(0)) if m else None, "imprint": get("imprint"),
                        "language": get("language"), "links": links,
                        "tags": [t.strip() for t in get("tags").split(";") if t.strip()], "notes": get("notes")})
    return out


def books_block(page):
    """The table of books, with its rows as JSON beside it ("</" escaped so no row can end the script)."""
    if not os.path.exists(page.books):
        return ""
    tmpl = open(os.path.join(SITE, "books.html"), encoding="utf-8").read().strip()
    tmpl = tmpl.replace("__PLACEHOLDER__", html.escape(page.cfg["books_placeholder"], quote=True))
    tmpl = tmpl.replace('<div class="books" id="books">',
                        f'<div class="books" id="books" data-export="{html.escape(page.cfg["export"])}">', 1)
    data = json.dumps(read_books(page.books), ensure_ascii=False).replace("</", "<\\/")
    return tmpl + f'\n<script type="application/json" id="books-data">{data}</script>'


def palette(colors):
    """The page's accent colours, light and dark, as the custom properties site/page.css uses."""
    decl = lambda c: ";".join(f"--{k}:{v}" for k, v in c.items())
    return (f':root{{{decl(colors["light"])}}}\n'
            f'@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{{decl(colors["dark"])}}}}}\n'
            f':root[data-theme="dark"]{{{decl(colors["dark"])}}}')


# ----------------------------------------------------------------- the page
def build(page, bump=True):
    md = open(page.md, encoding="utf-8").read()
    secs = sections(md)
    title = page.cfg["title"] or secs[0][0] or "Primary Sources"
    rest = split_intro(secs[0][1])
    body = secs[1:]
    # the section that holds the table goes last and stays open, as the Japan page's search does
    books = books_block(page)
    special = [(h, l) for h, l in body if books and any(x.strip() == BOOKS_MARK for x in l)]
    body = [(h, l) for h, l in body if (h, l) not in special]

    part = lambda name: open(os.path.join(SITE, name), encoding="utf-8").read().strip()
    css = palette(page.cfg["colors"]) + "\n" + part("page.css") + ("\n" + part("books.css") if books else "")

    buttons = ['<button type="button" class="jump openall" data-target="all" aria-expanded="false">Open All</button>']
    buttons += [f'<button type="button" class="jump" data-target="{slug(h)}" aria-expanded="false">{html.escape(h)}</button>'
                for h, _ in body]
    buttons += [f'<button type="button" class="jump search" data-target="{slug(h)}">{html.escape(h)}</button>'
                for h, _ in special]
    lede = "\n    ".join(f'<p class="lede">{inline(p)}</p>' for p in page.cfg["lede"])

    parts = [f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(page.cfg["description"])}">
<style>
{css}
</style>
</head>
<body class="page">
<div class="wrap">
  <header class="site">
    <h1>{html.escape(title)}</h1>
    {lede}
    {also_line(rest)}
  </header>
  <nav class="jumps">
    <div class="sections">
      {"\n      ".join(buttons)}
    </div>
  </nav>''']

    for h, lines in body:
        parts.append(f'''  <section class="md" id="{slug(h)}" hidden>
    <h2 tabindex="0" role="button" title="Hide this section">{html.escape(h)}</h2>
    <div class="body">
{render(lines)}
    </div>
  </section>''')
    for h, lines in special:
        parts.append(f'''  <section class="books-section" id="{slug(h)}">
    <h2>{html.escape(h)}</h2>
    <div class="body">
{render(lines, books)}
    </div>
  </section>''')

    ver, today = page.version(bump), datetime.date.today().strftime("%d %B %Y").lstrip("0")
    credits = "\n    ".join(f"<p>{inline(c)}</p>" for c in page.cfg["credits"])
    parts.append(f'''  <footer class="credit" id="credits">
    {credits}
    <p class="version">Version {ver} · Last Updated: {today} ·
      <a href="{REPO}{page.name}" target="_blank" rel="noopener">Source on GitHub</a></p>
  </footer>''')

    parts.append('''</div>
<button id="totop" type="button" class="totop" title="Back to the top" aria-label="Back to the top" hidden>↑</button>
<script>
// Each button opens or closes its section; a section's own heading closes it. The books section is
// always on the page, so its button only scrolls to it.
const openAll = document.querySelector("nav.jumps button.openall");
function setOpen(sec, open) {
  sec.hidden = !open;
  const b = document.querySelector(`nav.jumps button[data-target="${sec.id}"]`);
  if (b) b.setAttribute("aria-expanded", open ? "true" : "false");
}
function syncOpenAll() {
  const secs = [...document.querySelectorAll("section.md")];
  const all = secs.length && secs.every(s => !s.hidden);
  openAll.textContent = all ? "Close All" : "Open All";
  openAll.setAttribute("aria-expanded", all ? "true" : "false");
}
openAll.addEventListener("click", () => {
  const secs = [...document.querySelectorAll("section.md")];
  const open = secs.some(s => s.hidden);
  for (const s of secs) setOpen(s, open);
  syncOpenAll();
  if (open && secs.length) secs[0].scrollIntoView({ behavior: "smooth", block: "start" });
});
for (const b of document.querySelectorAll("nav.jumps button:not(.openall)")) {
  b.addEventListener("click", () => {
    const sec = document.getElementById(b.dataset.target);
    if (!sec) return;
    if (b.classList.contains("search")) { sec.scrollIntoView({ behavior: "smooth", block: "start" }); return; }
    const open = sec.hidden;
    setOpen(sec, open);
    syncOpenAll();
    if (open) sec.scrollIntoView({ behavior: "smooth", block: "start" });
  });
}
// a way back up from the middle of a long list
const toTop = document.getElementById("totop");
addEventListener("scroll", () => { toTop.hidden = scrollY < 400; }, { passive: true });
toTop.addEventListener("click", () => scrollTo({ top: 0, behavior: "smooth" }));

for (const h of document.querySelectorAll("section.md > h2")) {
  const close = () => {
    const sec = h.parentElement;
    setOpen(sec, false);
    syncOpenAll();
    const b = document.querySelector(`nav.jumps button[data-target="${sec.id}"]`);
    if (b) b.scrollIntoView({ behavior: "smooth", block: "center" });
  };
  h.addEventListener("click", close);
  h.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); close(); } });
}
</script>
''' + (f"<script>\n{part('books.js')}\n</script>\n" if books else "") + '''</body>
</html>
''')
    open(page.out, "w", encoding="utf-8").write("\n".join(parts))
    return title, [h for h, _ in body], [h for h, _ in special]


def all_pages():
    return sorted(os.path.basename(os.path.dirname(os.path.dirname(p)))
                  for p in glob.glob(os.path.join(ROOT, "*", "page", "config.json")))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pages", nargs="*", help="page directories to build (default: all)")
    ap.add_argument("--no-bump", dest="bump", action="store_false", help="rebuild without new version numbers")
    args = ap.parse_args()
    for d in args.pages or all_pages():
        page = Page(d.strip("/"))
        title, heads, special = build(page, args.bump)
        print(f"{d}/index.html: {title!r}, {len(heads)} sections" +
              (f" + {special[0]!r} (books)" if special else "") + f", version {page.version(False)}")
