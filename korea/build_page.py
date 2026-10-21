#!/usr/bin/env python3
"""Build index.html: the Primary Sources page for modern Korean history.

    build_page.py [--md page/modern-korea.md] [--out index.html]
    build_page.py --from "/path/to/modern-korea.md"     copy that file into page/ first, then build
    build_page.py --no-bump                             rebuild without a new version number

The page is made of these, none of which this script edits by hand:

    page/modern-korea.md   the list itself. Edit it and run this script again.
    page/version.txt       the build number shown at the foot of the page, raised by one each build
    page/books.csv         the books online: one row a book (author, title, year, language, links, notes)
    site/page.css          the look of the page (serif, the layout of the Japan page)
    site/books.*           the table the books are shown in: search, filters, sorting, an entry in full

It follows the design of the Modern Japanese History page (github.com/kmlawson/japan-bib). The books
are shown in the same searchable, sortable table that page has, but with no database behind it: the rows
of books.csv are written into the page as JSON, wherever a line of the markdown reads `<!--books-->`.
In books.csv, `links` holds one or more copies separated by " ; ", each a URL with an optional label
before it ("Vol 1 https://..."); `notes` may use markdown links and *italics*.

A bullet ending in the marker `<!--pills-->`, at any depth, becomes bubbles: if it ends in a colon its
indented list turns into a row of small bubbles, otherwise the bullet itself becomes one. Any other
indented list stays an ordinary list, nested as deep as it is indented.

Each `# heading` in the markdown becomes a section of the page with a button of its own at the top,
in the order they are written. Nothing but the buttons is shown when the page opens: pressing a
button reveals that section, pressing it again - or clicking the section's own heading - hides it.
The first `# heading` is the page title; the list of sections underneath it is left out, since the
buttons say the same thing, and the "See also" links after it are set as one line under the title.
"""
import argparse, csv, datetime, html, json, os, re, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(HERE, "page", "modern-korea.md")
OUT = os.path.join(HERE, "index.html")
SITE = os.path.join(HERE, "site")
VERSION = os.path.join(HERE, "page", "version.txt")   # the number shown at the foot, one per published build
BOOKS = os.path.join(HERE, "page", "books.csv")
BOOKS_MARK = "<!--books-->"     # a line of the markdown that reads this becomes the table of books
BOOKS_PLACEHOLDER = 'Search author, title, notes… (e.g.  gale   "korean folk"   author:underwood   -german)'
BOOKS_EXPORT = 'korea-books'            # the name the exported CSV and BibTeX files start with
REPO = "https://github.com/kmlawson/primary-sources/tree/master/korea"
DESCRIPTION = ("A list of open access primary sources for the study of modern Korean history, aimed "
               "primarily at students working with sources in English.")
LEDE = ("This page is part of a collection assembling links to historical primary sources that are open "
        "on the web. It should be seen as a work in progress, and corrections or suggestions for "
        "additions are most welcome. These resources may be especially useful to students of modern "
        "Korean history who are looking for inspiration and primary sources for use in their essays who "
        "a) are limited to the English language (though some Korean language sources will be listed below"
        " too) b) lack access to subscription databases that universities with strong East Asia "
        "collections may offer, and c) are in lockdown due to a global pandemic.")
# the foot of the page: who helped, and how to reach the editor. Markdown links are allowed.
CREDITS = [
    "Contributors: Links, suggestions and corrections with help of Konrad M. Lawson, Holly Stephens, Owen "
    "Miller, Vladimir Tikhonov, and Matt Van Volkenburg. Many links already found assembled thanks to the "
    "[Royal Asiatic Society-Korea Branch](http://www.raskb.com/) and some of the library guides above.",
    "We most welcome your corrections or suggestions for additions to the page. You can reach Konrad at "
    "kmlawson@froginawell.net or @kmlawson on Twitter.",
    "The code and design of this page were created with the use of Anthropic Claude with Konrad M. Lawson at "
    "the prompt, following the design of the "
    "[Modern Japanese History](https://froginawell.net/reference/modern-japan/) page. The links themselves "
    "were gathered over several years by Konrad and the contributors named above. Feel free to use this page "
    "as a starting point for building your own collection of resources: the list is kept as markdown on "
    "GitHub, and pull requests and forks are welcome.",
]


def version(bump=True):
    """1.0001, 1.0002 ... one step for each build meant for the site. --no-bump leaves it alone."""
    n = 0
    if os.path.exists(VERSION):
        m = re.search(r"(\d+)\s*$", open(VERSION, encoding="utf-8").read().strip())
        n = int(m.group(1)) if m else 0
    if bump:
        n = n % 9999 + 1
        os.makedirs(os.path.dirname(VERSION), exist_ok=True)
        open(VERSION, "w", encoding="utf-8").write(f"{n}\n")
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


PILLS_MARK = "<!--pills-->"     # put this at the end of a bullet and its indented list becomes bubbles


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
            out.append(f"<h3>{inline(m.group(2))}</h3>")
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
    label, links = "", []
    for line in lines:
        t = line.strip()
        if not t:
            continue
        m = re.match(r"^[-*+]\s+(.*)$", t)
        if m:
            links.append(inline(m.group(1)))
        elif not label:
            label = t.rstrip(":")
    if not links:
        return ""
    # the lede already says "See also:", so the line itself is just the links
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
def read_books(path=BOOKS):
    """The rows of books.csv as the table wants them: links split into {label, url}, and the first year
    as a number for sorting and the year filter."""
    out = []
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            links = []
            for part in (r.get("links") or "").split(" ; "):
                part = part.strip()
                if not part:
                    continue
                label, _, url = part.rpartition(" ")
                links.append({"label": label.strip(), "url": url})
            m = re.search(r"\d{4}", r.get("year") or "")
            out.append({"author": (r.get("author") or "").strip(), "title": (r.get("title") or "").strip(),
                        "year": (r.get("year") or "").strip(), "year_num": int(m.group(0)) if m else None,
                        "language": (r.get("language") or "").strip(), "links": links,
                        "notes": (r.get("notes") or "").strip()})
    return out


def books_block():
    """The table of books, with its rows as JSON beside it ("</" escaped so no row can end the script)."""
    if not os.path.exists(BOOKS):
        return ""
    tmpl = open(os.path.join(SITE, "books.html"), encoding="utf-8").read().strip()
    tmpl = tmpl.replace("__PLACEHOLDER__", html.escape(BOOKS_PLACEHOLDER, quote=True))
    tmpl = tmpl.replace('<div class="books" id="books">', f'<div class="books" id="books" data-export="{BOOKS_EXPORT}">', 1)
    data = json.dumps(read_books(), ensure_ascii=False).replace("</", "<\\/")
    return tmpl + f'\n<script type="application/json" id="books-data">{data}</script>'


# ----------------------------------------------------------------- the page
def build(md_path, out_path, bump=True):
    md = open(md_path, encoding="utf-8").read()
    secs = sections(md)
    title = secs[0][0] or "Primary Sources"
    rest = split_intro(secs[0][1])
    body = secs[1:]

    part = lambda name: open(os.path.join(SITE, name), encoding="utf-8").read().strip()
    css = part("page.css")
    books = books_block()
    if books:
        css += "\n" + part("books.css")

    buttons = ['<button type="button" class="jump openall" data-target="all" aria-expanded="false">Open All</button>']
    buttons += [f'<button type="button" class="jump" data-target="{slug(h)}" aria-expanded="false">{html.escape(h)}</button>'
                for h, _ in body]

    parts = [f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(DESCRIPTION)}">
<style>
{css}
</style>
</head>
<body class="page">
<div class="wrap">
  <header class="site">
    <h1>{html.escape(title)}</h1>
    <p class="lede">{html.escape(LEDE)}</p>
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
{render(lines, books)}
    </div>
  </section>''')

    ver, today = version(bump), datetime.date.today().strftime("%d %B %Y").lstrip("0")
    credits = "\n    ".join(f"<p>{inline(c)}</p>" for c in CREDITS)
    parts.append(f'''  <footer class="credit" id="credits">
    {credits}
    <p class="version">Version {ver} · Last Updated: {today} ·
      <a href="{REPO}" target="_blank" rel="noopener">Source on GitHub</a></p>
  </footer>''')

    parts.append('''</div>
<button id="totop" type="button" class="totop" title="Back to the top" aria-label="Back to the top" hidden>↑</button>
<script>
// Each button opens or closes its section; a section's own heading closes it.
const openAll = document.querySelector("nav.jumps button.openall");
function setOpen(sec, open) {
  sec.hidden = !open;
  const b = document.querySelector(`nav.jumps button[data-target="${sec.id}"]`);
  if (b) b.setAttribute("aria-expanded", open ? "true" : "false");
}
function syncOpenAll() {
  const secs = [...document.querySelectorAll("section.md")];
  const all = secs.every(s => !s.hidden);
  openAll.textContent = all ? "Close All" : "Open All";
  openAll.setAttribute("aria-expanded", all ? "true" : "false");
}
openAll.addEventListener("click", () => {
  const secs = [...document.querySelectorAll("section.md")];
  const open = secs.some(s => s.hidden);
  for (const s of secs) setOpen(s, open);
  syncOpenAll();
  if (open) secs[0].scrollIntoView({ behavior: "smooth", block: "start" });
});
for (const b of document.querySelectorAll("nav.jumps button:not(.openall)")) {
  b.addEventListener("click", () => {
    const sec = document.getElementById(b.dataset.target);
    if (!sec) return;
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
    open(out_path, "w", encoding="utf-8").write("\n".join(parts))
    return title, [h for h, _ in body]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", default=MD)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--from", dest="src", help="copy this markdown into page/ before building")
    ap.add_argument("--no-bump", dest="bump", action="store_false", help="rebuild without a new version number")
    args = ap.parse_args()
    if args.src:
        os.makedirs(os.path.dirname(MD), exist_ok=True)
        shutil.copyfile(args.src, MD)
        print("copied", args.src, "->", os.path.relpath(MD, HERE))
    title, heads = build(args.md, args.out, args.bump)
    print(f"{os.path.relpath(args.out, HERE)}: {title!r} with {len(heads)} sections, version {version(False)}")
    for h in heads:
        print("   ", h)
