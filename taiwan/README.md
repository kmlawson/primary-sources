# Primary Sources: History of Taiwan

A list of open access primary sources for the study of the history of Taiwan, published as a single static page.
It follows the design of the [Modern Japanese History](https://froginawell.net/reference/modern-japan/) page
([kmlawson/japan-bib](https://github.com/kmlawson/japan-bib)), without that page's bibliography search.

## Editing

The list lives in `page/history-taiwan.md`. Each `# heading` becomes a section with a button of its own at the top
of the page; the first `# heading` is the page title, and the "See also" links under it are set as one
line beneath the title. Ordinary markdown links, `*italic*`, `**bold**`, ``code``, `## sub-headings` and
nested bullet lists (indent by four spaces) all work. A bullet ending in `<!--pills-->` becomes small
bubbles, as on the Japan page.

The lede, the contributors and the rest of the foot of the page are set at the top of `build_page.py`.

## Building

    python3 build_page.py                # writes index.html and raises the version number
    python3 build_page.py --no-bump      # rebuild without a new version number

`index.html` is generated — never edit it by hand. Its styles come from `site/page.css` and are inlined,
so the page is one self-contained file.

## Publishing

Copy `index.html` to wherever the page is served. Nothing else is needed.
