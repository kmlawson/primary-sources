# Link check of the Korea page, October 2026

Every link on the Modern Korean History page (`korea/`) was checked on 21 October 2026, broken links were
traced to where their pages had moved, and the page was repaired, following the same rules as the
[Taiwan check](link-check-taiwan-2026-10.md): fix only with high confidence, keep every old address, mark
the rest. The outcome for every link is in [`korea/page/links.csv`](../korea/page/links.csv); the evidence
is in [`link-check-korea-2026-10/`](link-check-korea-2026-10/).

## Result

Of the 795 links now on the page:

| | links |
|---|---|
| work | 771 |
| … of which updated to where their pages moved | 48 |
| down for maintenance | 1 |
| broken, marked † | 20 |
| could not be checked | 3 |

The 383 National Diet Library and 233 Internet Archive links were not fetched: the owner confirmed those
sites are fine (`check_links.py korea --skip dl.ndl.go.jp archive.org`), and five NDL links chosen at random
were then opened and their catalogue records read (title, publisher, year): all five were the right books,
public domain and open to read. They are recorded as working, with a note that they were not fetched.

## What moved

| what | old home | new home |
|---|---|---|
| 7 *Foreign Relations of the United States* volumes | retired `digicoll.library.wisc.edu` addresses | the State Department's Office of the Historian, `history.state.gov`; each volume's heading checked |
| the list of all FRUS volumes | the old UW browse page | the UW FRUS collection's permanent address, `digital.library.wisc.edu/1711.dl/FRUS` |
| the Wilson Center Digital Archive and its 34 Korea collections | `digitalarchive.wilsoncenter.org` | the University of Maryland, `digitalarchive.umd.edu/topics/…`: 32 matched by exact name (and document count) in the site's own A–Z topic list, the other 2 opened and their titles checked |
| NDSU Korean War propaganda leaflets | `http://www.digitalhorizonsonline.org/…` (404) | the same collection over https, 133 leaflets |
| Columbia's *Korean Independence Outbreak Movement* exhibit | `exhibitions.cul.columbia.edu` (404) | `exhibitions.library.columbia.edu`, same exhibit |
| Oregon Digital's e-Asia Digital Library, and *Occidental Literature on Korea* | the old Oregon Digital platform | the same collection and record on the new platform |
| the Independence Hall of Korea's 한국독립운동정보시스템 | a deep page that now gives 404 | the system's front page (the link's text is the institution's name) |

## Still broken (marked †)

| link | why | possible new home, not confirmed |
|---|---|---|
| UCLA Online Archive of Korean Christianity (5 links) | the whole site answers 502 Bad Gateway; may be temporary or permanent | — |
| 5.18 Archives, "Cherokee Documents" e-books (5) | the site was rebuilt and the date-range e-books are gone | the US declassified documents collection (미국해제문서, 1,256 items) on the new site: one link could replace all five |
| History Net (우리역사넷) photo collection | 404 | — |
| 한국역사정보통합시스템 and its newspaper section (2) | the domain is gone | 한국사데이터베이스 (db.history.go.kr) for the first; the National Library's 대한민국 신문아카이브 for newspapers |
| BigKinds post-1960s newspaper archive | redirects to the front page; no such archive now | — |
| LTI Korea e-book search | the library was rebuilt; the old search gives 400 | its e-book list, unfiltered |
| Oregon Digital e-Asia, Korea (North) and Korea (South) | the new platform ignores the old filter, showing the whole collection | rebuilt filter addresses on the new platform |
| USC Korean American Digital Archive | the old catalogue page is gone | its page on USC's new digital library |
| Harvard-Yenching "Minsokwon" project page | Harvard retired its projects.iq sites | Harvard's "Korean Rare Books @ Harvard-Yenching Library" page |
| University of Hawaii, *Korean History: A Bibliography* | 404; not carried over to the new Center for Korean Studies site | — |

## Could not be checked, or down

The Korean Digital National Library (dlibrary.go.kr: the checking machine's network refused it, but the
National Library of Korea still links to it), e-coreana (never answers), and the CIA reading room's
*Baptism by Fire* collection (every deep reading-room address landed on its front page, which looks like
anti-bot behaviour). Duke's *African-American Soldier's Korean War Photograph Album* redirects correctly but
was showing a maintenance page.

## Notes for the owner

1. Whether to accept any of the "possible new home" suggestions above.
2. The Wilson Center section still begins "The Wilson Center hosts the world's best online archive on the
   Cold War"; the link now goes to the University of Maryland, but the wording was left alone.
3. The search tip in *US Government Documents* (`site:http://dl.nanet.go.kr/law/ "KRDB" …`) refers to a
   section of the National Assembly Library's site that no longer exists; the documents themselves are now
   at `dl.nanet.go.kr/SearchDetailView.do?cn=KRDB…` (the two sample links there still work).
4. The 22 Yale handle links for the Presbyterian mission reports still resolve to the right records on
   Yale's new collections site, so they were left as they are.

## The files in `link-check-korea-2026-10/`

| file | what it is |
|---|---|
| `1-check.json` | the check: every link checked, where it is used, every attempt and the verdict |
| `2-frus-history-state-gov.json` | the FRUS volumes at the Office of the Historian, with headings checked |
| `3-umd-digital-archive-topics.json`, `3-wilson-to-umd-matches.json` | the University of Maryland Digital Archive's A–Z topic list, and the Wilson Center collections matched to it |
| `4-research-brief.md` | the brief the research followed |
| `5-research-*.json` | the two research groups' proposals, with evidence and confidence |
