# Primary Sources

Lists of open access primary sources for the study of East and Southeast Asian history, published as
static pages at <https://kmlawson.github.io/primary-sources/>. They follow the design of the
[Modern Japanese History](https://froginawell.net/reference/modern-japan/) page
([kmlawson/japan-bib](https://github.com/kmlawson/japan-bib)).

| page | directory |
|---|---|
| Modern Korean History | `korea/` |
| History of Taiwan | `taiwan/` |
| History of Modern Shanghai | `shanghai/` |
| Missionary Perspectives on China | `missionaries/` |
| History of Burma | `burma/` |
| The Malay World | `malay-world/` |

`index.html` at the root is the home page linking to them; it is written by hand.

How the pages came to be, the decisions made along the way and what is still to do are in
[docs/HISTORY.md](docs/HISTORY.md); the October 2026 link check of the Taiwan page is reported in
[docs/link-check-taiwan-2026-10.md](docs/link-check-taiwan-2026-10.md).

## Editing a page

Each page's directory holds its own content, in `page/`:

- **`*.md`** — the list itself. Each `# heading` becomes a section with a button of its own at the top of
  the page; the first `# heading` is the page title, and the "See also" links under it are set as one line
  beneath the title. Ordinary markdown links, `*italic*`, `**bold**`, `` `code` ``, `## sub-headings` and
  nested bullet lists (indent by four spaces) all work. A line `![caption](img/file.png)` shows a picture as a
  thumbnail that opens full size; keep the file in the page's own directory. A bullet ending in `<!--pills-->` becomes small
  bubbles, as on the Japan page.
- **`books.csv`** — the books online, one row a book (see below). A line `<!--books-->` in the markdown marks
  where the table goes; the section it is in becomes the books section, always on the page after the
  others with a solid "Digitized Books" button of its own at the end of the button row, like the Japan
  page's; the section keeps its own heading.
- **`config.json`** — the title, the opening paragraph(s) (`lede`), the paragraphs at the foot (`credits`),
  the search box's example text, the name of export files, and the page's colours, light and dark.
- **`version.txt`** — the build number shown at the foot of the page.

## The books

`books.csv` is shown in a searchable, sortable table — search, year range, host and language filters, tag
buttons, click a column to sort, a row to open the entry, export as CSV or BibTeX. There is no database:
the rows are written into the page when it is built.

| column | content |
|---|---|
| `author` | as it should be shown and sorted, e.g. `Gale, James Scarth`; several separated by `; ` |
| `title` | the title as given |
| `year` | as given (`1905`, `1874 / 1715`, `1944-5`); the first four-digit number is used for sorting and the year filter |
| `imprint` | place and publisher, shown in the entry |
| `language` | `English`, `German` … for the Language filter |
| `links` | one or more copies separated by ` ; `, each a URL with an optional label before it: `Vol 1 https://… ; Vol 2 https://…` |
| `tags` | separated by ` ; `. Each becomes a button above the table; date ranges (`1886-1942`, `Pre-1823`, `1945-Present`) form a row of periods, the rest a row of topics |
| `notes` | shown under the title; markdown links and `*italics*` work |

The Export CSV button gives the same columns, so an export can be pasted back into `books.csv`. The
Burma, Shanghai and Malay World lists came from the Zotero exports behind the old pages' book lists, with
only the manually assigned Zotero tags kept.

## Building

    python3 build.py                     # every page; raises each version number
    python3 build.py korea burma         # just these
    python3 build.py --no-bump           # rebuild without new version numbers

Each `index.html` is generated — never edit it by hand. What the pages share is in `site/`: `page.css`
(the look of every page) and `books.html`, `books.css`, `books.js` (the table). They are inlined when a page
is built, so each page is one self-contained file.

## Checking links

    python3 check_links.py taiwan          # about a quarter of an hour for 270 links

checks every link on a page and keeps `page/links.csv` up to date: one row a URL with its status (`ok`,
`fixed`, `broken`, `temporary`, `unchecked`), the date checked, and — for a repaired link — the old
address in `url` and the new one in `replacement`, so the old address stays on record. Decisions made by
hand are kept; only clear answers (a page that loads, a 404/410, a host name that no longer exists) change
a status. A broken link stays on the page with a small † after it that searches the Wayback Machine for
archived copies, and the footer gives the totals from the last check.

The checker is gentle with servers: one request at a time, three seconds between requests, ten between two
to the same host, and a single retry half a minute later.

## Publishing

GitHub Pages serves the repository as it is: push, and the pages update in a minute or two.
