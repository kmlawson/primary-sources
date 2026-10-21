# Primary Sources: History of Taiwan

A list of open access primary sources for the study of the history of Taiwan, published as a single static page.
It follows the design of the [Modern Japanese History](https://froginawell.net/reference/modern-japan/) page
([kmlawson/japan-bib](https://github.com/kmlawson/japan-bib)), with its book list in the same searchable table.

## Editing

The list lives in `page/history-taiwan.md`. Each `# heading` becomes a section with a button of its own at the top
of the page; the first `# heading` is the page title, and the "See also" links under it are set as one
line beneath the title. Ordinary markdown links, `*italic*`, `**bold**`, ``code``, `## sub-headings` and
nested bullet lists (indent by four spaces) all work. A bullet ending in `<!--pills-->` becomes small
bubbles, as on the Japan page.

The lede, the contributors and the rest of the foot of the page are set at the top of `build_page.py`.

## The books

The books online are kept apart from the rest of the list, in `page/books.csv` (one row a book), and are
shown in the same searchable, sortable table as the Japan page's bibliography — search, year range, host
and language filters, click a column to sort, a row to open the entry, export as CSV or BibTeX. There is no
database: the rows are written into the page when it is built, where a line of the markdown reads
`<!--books-->`.

| column | content |
|---|---|
| `author` | as it should be shown and sorted, e.g. `Gale, James Scarth` |
| `title` | the title as given |
| `year` | as given (`1905`, `1874 / 1715`, `1944-5`); the first four-digit number is used for sorting and the year filter |
| `language` | `English`, `German` … for the Language filter |
| `links` | one or more copies separated by ` ; `, each a URL with an optional label before it: `Vol 1 https://… ; Vol 2 https://…` |
| `notes` | shown under the title; markdown links and `*italics*` work |

The table itself is `site/books.html`, `site/books.css` and `site/books.js`; an export from the page's
Export CSV button has the same columns, so it can be pasted back into `books.csv`.

## Building

    python3 build_page.py                # writes index.html and raises the version number
    python3 build_page.py --no-bump      # rebuild without a new version number

`index.html` is generated — never edit it by hand. Its styles and scripts come from `site/` and are inlined,
so the page is one self-contained file.

## Publishing

Copy `index.html` to wherever the page is served. Nothing else is needed.
