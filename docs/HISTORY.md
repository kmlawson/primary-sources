# Project history

How these pages came to be what they are: what was done, why, and what was decided along the way. For how
to edit, build and publish, see the [README](../README.md). The October 2026 link check of the Taiwan page has
its own report: [link-check-taiwan-2026-10.md](link-check-taiwan-2026-10.md).

All of the work below was done on 21 October 2026, with Anthropic's Claude working at Konrad M. Lawson's
direction, on the branch `new-static-pages`, which GitHub Pages serves at
<https://kmlawson.github.io/primary-sources/>.

## Where it started

In 2020 this repository held two files, `modern-korea.html` and `history-taiwan.html`: plain copies of
the WordPress source of two Frog in a Well pages, kept so that others could suggest edits and fork the
lists. By 2026 they had drifted from the live pages.

1. **Synced with the live pages.** Both files were brought back in line with froginawell.net, link for
   link. The Korea page had grown a large section of Japanese-language sources (several hundred National
   Diet Library and National Library of Korea links), the RASKB links had moved, and the Taiwan page had
   gained national library, 2.28 archive, Buddhist archive and indigenous-archive entries. These two files
   remain at the root of the repository as the record of the WordPress versions.

2. **WordPress retired.** The pages were to leave WordPress, so new versions were built as static pages
   in the design of the Modern Japanese History page (<https://froginawell.net/reference/modern-japan/>,
   source at [kmlawson/japan-bib](https://github.com/kmlawson/japan-bib)): the list kept as markdown, one
   button per section at the top, sections hidden until opened, Open All / Close All, a back-to-top
   button, light and dark themes, built into one self-contained `index.html` by a Python script.

## The pages

| page | colour | from |
|---|---|---|
| `korea/` Modern Korean History | red | `modern-korea.html` (the synced WordPress source) |
| `taiwan/` History of Taiwan | light green | `history-taiwan.html` |
| `shanghai/` History of Modern Shanghai | purple | froginawell.net/frog/primary-sources-history-of-modern-shanghai/ |
| `missionaries/` Missionary Perspectives on China | sepia brown | froginawell.net/frog/sources/primary-sources-missionary-perspectives-on-china/ |
| `burma/` History of Burma | saffron | froginawell.net/frog/sources/primary-sources-history-of-burma/ |
| `malay-world/` The Malay World | teal | froginawell.net/frog/primary-sources-the-malay-world/ |

`index.html` at the root is a hand-written home page with a card for each, in its colour, and one for the
Japan page.

### Rules followed in the conversions

- **The wording is the owner's.** Text was carried over verbatim; nothing was rephrased or summarised. The
  opening paragraphs of each page are its original ones (an early rewrite of the Korea and Taiwan intros
  was reverted at the owner's request). WordPress's typographic quotes and dashes were turned back into
  plain ones, as in the original sources.
- **Every link carried over.** After each conversion every `href` of the original was checked against the
  new page. The exceptions are listed under "Changes to the text" below.
- **Section names** come from each page's own Contents list or headings. Where a page had a dozen or more
  small sections, some were grouped so that the row of buttons stays usable, with every original heading
  kept as a sub-heading:
  - Missionaries: the 14 periodical headings under one section, *Missionary Periodicals*.
  - Malay World: the four "Publications from/by …" people under *Publications from Select Individuals*,
    and the six National Archives of Singapore parts under *National Archives of Singapore* (the
    *Microfilms* block moved down from between *Maps* and *Malaya Medical Reports* to join them).
- **The footers** carry each page's own contributors, contact and last-updated lines, plus a note that the
  code and design were made with Anthropic Claude, the version number and build date, and (on the Taiwan
  page) the totals of the last link check.

## The book tables

Every page's list of books online was moved out of the markdown into its own file, `page/books.csv`, and is
shown in the same kind of searchable, sortable table as the Japan page's bibliography, but with no
database behind it: the rows are written into the page as JSON when it is built.

- **Where they came from.** Korea (118 books), Taiwan (67) and Missionaries (34) had their books written
  inline as bullets; these were parsed into rows (author, title, year, language, links, notes), keeping
  the notes verbatim. Burma (1,178), Malay World (921) and Shanghai (138) had them in Zotero exports shown
  by a small widget called Bookie; these were converted from the Zotero data. Only the tags assigned by
  hand in Zotero were kept (Bookie showed only those too): 85 automatic library-catalogue tags such as
  "0143 zzz" or "bub_upload" were left out, and so was the catch-all "All Texts by Author".
- **Always on the page.** The section holding the table is always open, comes after all the others, and
  has a solid button labelled *Digitized Books* at the end of the row on every page (the section keeps its
  own heading, which is the button's tooltip), as on the Japan page.
- **What the table does.** Search with quoted phrases, `author:`, `title:`, `notes:` and `-word`; best
  matches first; year range; host, language and online-only filters; tag buttons; sorting by any column;
  a row opens the full entry (all copies, imprint, tags, notes, copy citation, search archive.org);
  export as CSV (same columns as books.csv, so it can be pasted back) or BibTeX; Zotero can take entries
  straight off the page.
- **Tags.** Tags that are date ranges (`1886-1942`, `Pre-1823`, `1945-Present`, `1950-`) make a row of
  period buttons in date order; the rest a row of topic buttons. One period and one topic can be chosen at
  once, together with any search; each button shows how many entries it would leave, and greys out at
  zero. A tag in an open entry lists everything with that tag.
- **Long entries.** Titles over about 140 characters are cut near 120 with "…" and *more* / *less* to
  open them in place (the full title is the tooltip, and the open entry always shows it); three or more
  authors show as the first and "et al.", the same way.
- **Pages.** 200 entries at a time by default, with 100 / 200 / 500 / All, and Prev / Next at the top and
  bottom of the table.
- **Hosts.** The host filter and the link pills name the library holding each copy: Internet Archive,
  HathiTrust, the Indian Culture Repository, British Library, NLB Singapore, Google Books and others.

## How it is built

At first each page had its own copy of the build script; with six pages that became one shared
`build.py`, with the shared look in `site/` (`page.css`, and `books.html`/`.css`/`.js` for the table). Each
page's directory keeps only its own content in `page/`: the markdown, `books.csv`, `config.json` (title,
opening paragraphs, credits, search-box example, colours), `version.txt`, and, for the Taiwan page,
`links.csv`. The build also handles pictures (`![caption](img/file.png)`, used for the 1931 map of Burma).
Each built page was checked in a real browser, in light and dark, at desktop and phone widths, for errors
and sideways scrolling.

## Changes to the text

Made at the owner's request after the conversions, in visible text only, never in link addresses:

- **Wording about the old widget.** Burma's "The button below will display a list of over 200 …" became
  "The table below lists over 1,100 …"; Shanghai's "The buttons below will offer a list …" became "The
  table below offers a list …"; Malay World's sentence telling readers to click the "All Texts by Author"
  button was removed, and so was Burma's "Click the button to display the latest version of the list of
  sources:".
- **Misspellings.** Muncipal → Municipal (a Shanghai heading), Digititized → Digitized (the Malay World
  books heading), diretly, Researech, Correspondance, reccomended, Boldeian → Bodleian, Presyterian, Port
  Aurthur, Univeristy, Berkely, Taiawn, Academica Historica → Academia Historica, Misssion, Eyewitnes,
  "United Sates", Horsefield → Horsfield, and "Strait Settlements" → "Straits Settlements" in two
  descriptive sentences (where it is part of a catalogue title it was left as printed).
- **A broken link repaired.** On the Missionaries page, Johnstoun's *China and Formosa* had its own title
  pasted in as its address; it now links to its archive.org copy (the one the Taiwan page uses).
- **A picture restored.** The Burma page's 1931 district map, shown beside the gazetteer volumes on the
  old page, is back as a thumbnail, with the image kept in `burma/img/` rather than in WordPress uploads.
- **A link dropped in conversion:** the image link to that map's WordPress upload, now replaced by the copy
  in the repository.

## Link checking

`check_links.py` checks every link on a page and keeps `page/links.csv`, and the build marks broken links
with a small † that searches the Wayback Machine for archived copies, with the totals in the footer. At the
owner's instruction it is gentle with servers: one request at a time, three seconds apart, ten seconds
between two requests to the same host, and a single retry half a minute later. The first run (before that
instruction) fetched eight at a time; nothing since has.

The Taiwan and Korea pages have been checked and repaired; see the [Taiwan report](link-check-taiwan-2026-10.md)
and the [Korea report](link-check-korea-2026-10.md). The other four pages have not been checked yet. The
checker can leave out hosts known to be fine (`--skip`), and a URL inside a `code` example (a search tip) is
not counted as a link.

## Still to do

- **Taiwan:** the owner's decisions listed at the end of the [link-check report](link-check-taiwan-2026-10.md).
- **Korea:** the owner's decisions listed at the end of the [Korea report](link-check-korea-2026-10.md).
- **Shanghai, Missionaries, Burma, Malay World:** not yet link-checked.
- **"See also" links** on the new pages still point at the old WordPress addresses of the Korea, Taiwan and
  Missionaries pages, and the "Source on GitHub" footer links point at `master`: both should change once
  the pages' permanent home is settled and `new-static-pages` is merged.
