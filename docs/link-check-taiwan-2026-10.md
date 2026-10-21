# Link check of the Taiwan page, October 2026

Every link on the History of Taiwan page (`taiwan/`) was checked on 21 October 2026, broken links were
traced to where their pages had moved, and the page was repaired. The outcome for every link, with the old
address of each repaired one, is in [`taiwan/page/links.csv`](../taiwan/page/links.csv); the evidence
behind each decision is in [`link-check-taiwan-2026-10/`](link-check-taiwan-2026-10/).

## Result

Of the 268 links now on the page:

| | links |
|---|---|
| work | 241 |
| … of which updated to where their pages moved | 66 |
| down for maintenance | 1 |
| broken, marked † | 17 |
| could not be checked | 10 |

The page footer gives the same totals. Each broken link stays where it was, followed by a small † that
opens a Wayback Machine search for archived copies of that exact address; the mark appears in the book
table and in the open entry too.

## The rules

- **Fix only with high confidence.** A link was given a new address only when the new page was fetched
  and was unmistakably the same resource: same title, record number or collection, from the same
  institution or its official successor. A site's front page was never used in place of a deep link.
- **Keep the old addresses.** Every repaired link's old address is in `links.csv` (column `url`, with the
  new one in `replacement`).
- **Otherwise, mark it.** Where no confident new home was found, the link stays and gets the † mark. Likely
  new homes that could not be confirmed are recorded in the link's note for the owner to decide.
- **Change addresses, not words.** Only link addresses changed; the page's wording is untouched.
- **Be gentle with servers** (from the owner, during the work): one request at a time, spaced out.

## How it was checked

1. **First pass.** Every link was fetched as a browser would, following redirects, with retries. Pages that
   answered with a "not found" page, or that dropped a deep link onto the site's front page ("soft 404s"),
   were counted as broken even though they returned success.
2. **Separating the checking machine's problems from the sites'.** The checks ran in a cloud sandbox whose
   network gets in the way in ways a reader's browser would not, and none of these was counted against a
   site:
   - its proxy refused a few hosts outright (502 to the connection);
   - it cannot complete some certificate chains that desktop browsers accept (Princeton, the 2.28
     archive, NTU's new digital collections);
   - the Wayback Machine and archive.org's APIs reset or rate-limited it;
   - several Taiwanese government and Academia Sinica sites refused plain `http://` but answered normally
     over `https://`.
   Every "host not found" was confirmed against Google's public DNS before being called dead.
3. **A browser pass.** Doubtful links were opened in Chromium, which gets past "are you human" checks and
   shows what a reader actually sees (HathiTrust's check page, the Taiwan Memory maintenance notice, NTU's
   own "We couldn't find it" page).
4. **Research.** The remaining broken links were split into three groups and researched by separate
   agents working from a common brief ([4-research-brief.md](link-check-taiwan-2026-10/4-research-brief.md)),
   each proposing a replacement with its evidence and a confidence level. Proposals were spot-checked
   independently before being applied (by fetching the new page, or through web search where the
   sandbox could not reach the site).

## What moved

| what | old home | new home |
|---|---|---|
| 15 *Foreign Relations of the United States* volumes | UW Digital Collections' retired `digicoll.library.wisc.edu` addresses, which now land on a general collection page | the State Department's Office of the Historian, `history.state.gov/historicaldocuments/frus…`; each volume's heading checked against the old identifier |
| the University of Wisconsin FRUS collection (2 links) | `uwdc.library.wisc.edu/collections/FRUS/` (now a general search page) | its permanent address, `digital.library.wisc.edu/1711.dl/FRUS` |
| 27 Princeton scanned maps of Taiwan | MIT GeoData, `geodata.mit.edu/catalog/princeton-…` ("410 Gone") | Princeton's own portal, `maps.princeton.edu/catalog/princeton-…`, same record ids |
| 2 Princeton catalogue records | old record numbers | the new numbers they redirect to |
| the Wilson Center Digital Archive (6 links) | `digitalarchive.wilsoncenter.org/collection/…` | the University of Maryland, `digitalarchive.umd.edu/topics/…`: the Cold War International History Project and its archive moved to the UMD School of Public Policy (<https://dgi.umd.edu/research-impact/projects/cold-war-international-history-project>) |
| NTU's historical photo archive | `photo.lib.ntu.edu.tw` (gone) | `dl.lib.ntu.edu.tw/s/photo/` |
| the V. S. Beausset collection (狄寶賽文庫) | DTRAP (`dtrap.lib.ntu.edu.tw`, gone) | `dl.lib.ntu.edu.tw/s/deBeausset/` |
| NTU's DTRAP project page and introduction | DTRAP | NTU Library's page for the project, `speccoll.lib.ntu.edu.tw/node/58` |
| the NTU institutional repository | `ntur.lib.ntu.edu.tw` | NTU Scholars, `scholars.lib.ntu.edu.tw`, into which it was merged |
| Taiwan Historica (國史館臺灣文獻館), 2 links | `www.th.gov.tw/new_site/…` (404) | its new site and its 檔案查詢系統 page |
| the Transitional Justice database | `twtjcdb.tjc.gov.tw` (the commission was dissolved in 2022) | the National Human Rights Museum, `twtjdb.nhrm.gov.tw` |
| the National Central Library in English | `enwww.ncl.edu.tw` | `www.ncl.edu.tw/en` |
| SOAS's guide to the English Presbyterian Mission archives | an old `soas.ac.uk/library/…` address | the same PDF at its new address |
| six Academia Sinica and government sites | `http://` | the same pages over `https://`, the only way they now answer |

## Still broken (marked †)

| link | why | possible new home, not confirmed |
|---|---|---|
| Lafayette East Asia Image Collection, Taiwan search | the old digital collections site is retired | the collection on ldr.lafayette.edu (whole collection, not a Taiwan search) |
| Lafayette Truku–Japanese War postcards | same | its collection on ldr.lafayette.edu |
| Yale search for "Department of Education, Taiwan" and Yale search for Taiwan | Yale's old search site is retired | the same searches on collections.library.yale.edu |
| NTU DTRAP English project page | host gone; no English page on the new sites | a Wayback copy |
| NTU web exhibition, English version | NTU's server returns its error page (the Chinese version still works) | — |
| NTU open-access ebooks | host gone; nothing replaced it | — |
| Taiwan Library (homepage.usask.ca): Kerr, *Formosa Betrayed* (page and PDF), Peng, *A Taste of Freedom*, Shackleton, *Formosa Calling* | host gone | romanization.com for Kerr and Peng (very likely the same texts: the Peng page credits the old site's proofreader); Shackleton is now in print from Camphor Press. The page's own Wayback copies remain |
| 國史館 蔣中正總統文物 (National Archives cross-archive link) | redirects to the portal's front page | Academia Historica's own archive system, ahonline.drnh.gov.tw |
| Taiwan Historica application form (ds3.th.gov.tw) | host gone | its 文獻檔案查詢系統 (onlinearchives.th.gov.tw) |
| Taiwan Historica "introduction" to its holdings | 404; no equivalent page | — |
| Transitional Justice database manual | the old host is gone | the museum's revised 資料庫介紹 page |
| Taiwan indigenous peoples archive (dore.tacp.gov.tw) | host gone | the Council of Indigenous Peoples' digital archives portal |
| Taiwan National Treasure (nationaltreasure.tw) | the site appears defunct | — |

## Could not be checked

From the checking machine, not necessarily broken for readers; worth opening in an ordinary browser:
five Wayback Machine copies (the Wayback Machine refused the connection); SOAS's new image platform; the
Academia Sinica rare-books site (now on port 8443) and its 臺灣總督府公文類纂 site (a "service temporarily
interrupted" page); NTU's National Repository of Cultural Heritage prototype; and Academia Historica's
postwar archive portal. The Taiwan Memory "Old Pictures" page showed a maintenance notice.

## For the owner to decide

1. Whether to accept any of the "possible new home" suggestions above.
2. Peng's "Archive.org Saved URL" in `books.csv` is a `web.archive.org/save/…` address, which asks the
   Wayback Machine to make a new copy of the dead page rather than opening an old one; it should be a
   snapshot address.
3. In the book table, Kerr's *Formosa Betrayed* shows the dead Taiwan Library copy first; listing its
   working Wayback copy first would make the "read" button work.
4. Keep, replace with a Wayback copy, or drop the links with no successor (Taiwan National Treasure, the
   Taiwan Historica introduction, the NTU English exhibition and ebooks).

## The files in `link-check-taiwan-2026-10/`

| file | what it is |
|---|---|
| `1-first-check.json` | the first pass: every link, where it is used, every attempt and the verdict |
| `2-browser-recheck.json` | the doubtful links opened in Chromium |
| `3-https-retry.json` | the failing `http://` links tried over `https://` |
| `4-research-brief.md` | the brief the research followed |
| `5-research-*.json` | the three groups' proposals: for each link, whether broken, the replacement, its confidence and the evidence |
| `6-frus-uw-permalinks.json`, `6-frus-history-state-gov.json` | the FRUS volumes, resolved at UW Digital Collections and then at the Office of the Historian, with the titles checked |
