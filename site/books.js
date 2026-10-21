// The table of books online: search, filter, sort, and an entry opened in full. Adapted from the search on
// the Modern Japanese History page (japan-bib site/app.js); the entries come from page/books.csv, written
// into the page as JSON when it is built, so there is nothing to download.
(() => {
"use strict";
const $ = id => document.getElementById(id);
const fold = s => (s || "").normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase();
const esc = s => (s || "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const EXPORT = $("books").dataset.export || "books";
let ALL = [], VIEW = [], sortKey = null, sortDir = 1, cur = -1, byMatch = false;
// a title longer than this is cut at a word near it, with "more" to show the rest in place; the full
// title is the cell's tooltip, and the entry opened in full always has it
const CUT = 120;
const expanded = new Set();          // ids of the entries whose long titles are shown in full
// tags: a date range ("1886-1942", "Pre-1823", "1945-Present", "1950-") is a period, anything else a topic.
// One of each can be chosen at a time; they narrow the list together with everything else.
const PERIOD = /^(pre-?|post-?)?-?\d{4}(\s*[-–]\s*(\d{4}|present))?-?$/i;
const sel = { period: null, topic: null };
const TAGS = { period: [], topic: [] };

// who holds a copy, by the host of its URL: the short code shown in the link column and used by the Host filter
const HOLDER = [[/web\.archive\.org\//, "WB", "Wayback Machine"], [/archive\.org\//, "IA", "Internet Archive"],
                [/indianculture\.gov\.in\//, "ICR", "Indian Culture Repository"],
                [/hathitrust\.org\/|hdl\.handle\.net\/2027\//, "H", "HathiTrust"],
                [/hdl\.handle\.net\/10079\//, "Yale", "Yale University Library"],
                [/nlb\.gov\.sg\//, "NLB", "National Library Board Singapore"], [/bl\.uk\//, "BL", "British Library"],
                [/sea\.lib\.niu\.edu\//, "NIU", "SEAsite, Northern Illinois University"],
                [/seasiavisions\.library\.cornell\.edu\//, "Cornell", "Southeast Asia Visions (Cornell)"],
                [/deutsche-digitale-bibliothek\.de\//, "DDB", "Deutsche Digitale Bibliothek"],
                [/nla\.gov\.au\//, "NLA", "National Library of Australia"], [/kb\.nl\//, "KB", "KB, National Library of the Netherlands"],
                [/books\.google\./, "GB", "Google Books"], [/nls\.uk\//, "NLS", "National Library of Scotland"],
                [/myanmar-law-library\.org\//, "MLL", "Myanmar Law Library"],
                [/gutenberg\.org\//, "PG", "Project Gutenberg"], [/dl\.ndl\.go\.jp\//, "NDL", "National Diet Library"],
                [/usask\.ca\//, "USask", "Taiwan Library (USask)"], [/doi\.org\//, "DOI", "Publisher (DOI)"]];
const holder = u => (HOLDER.find(([rx]) => rx.test(u || "")) || [null, "Web"])[1];
const holderName = code => (HOLDER.find(h => h[1] === code) || [, , "Elsewhere online"])[2];

// notes are written in markdown: links and *italics*
const md = s => esc(s).replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
  .replace(/\*([^*]+)\*/g, "<em>$1</em>");
const plain = s => (s || "").replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, "$1").replace(/\*/g, "");

function load() {
  const data = JSON.parse($("books-data").textContent);
  ALL = data.map((r, i) => {
    r.id = i + 1;
    r.nlinks = r.links.length;
    r.fa = fold(r.author); r.ft = fold(r.title); r.fn = fold(plain(r.notes));
    r.tags = r.tags || [];
    r.fall = r.fa + " \u0001 " + r.ft + " \u0001 " + r.fn + " " + fold(r.year + " " + r.language + " " + (r.imprint || "") + " " + r.tags.join(" "));
    return r;
  });
  const langCount = {};
  for (const r of ALL) if (r.language) langCount[r.language] = (langCount[r.language] || 0) + 1;
  for (const l of Object.keys(langCount).sort((a, b) => langCount[b] - langCount[a])) {
    const o = document.createElement("option"); o.value = l; o.textContent = `${l} (${langCount[l]})`; $("blang").appendChild(o);
  }
  const hosts = {};
  for (const r of ALL) for (const u of new Set(r.links.map(l => holder(l.url)))) hosts[u] = (hosts[u] || 0) + 1;
  for (const h of Object.keys(hosts).sort((a, b) => hosts[b] - hosts[a])) {
    const o = document.createElement("option"); o.value = h; o.textContent = holderName(h); $("bhost").appendChild(o);
  }
  // periods in date order ("Pre-1823" and "-1823" first), topics alphabetically
  const tagCount = {};
  for (const r of ALL) for (const t of r.tags) tagCount[t] = (tagCount[t] || 0) + 1;
  const start = t => /^(pre|-)/i.test(t) ? -1 : parseInt((t.match(/\d{4}/) || [9999])[0]) + (/^post/i.test(t) ? 0.5 : 0);
  TAGS.period = Object.keys(tagCount).filter(t => PERIOD.test(t)).sort((a, b) => start(a) - start(b));
  TAGS.topic = Object.keys(tagCount).filter(t => !PERIOD.test(t)).sort((a, b) => fold(a) < fold(b) ? -1 : 1);
  if (TAGS.period.length || TAGS.topic.length) {
    $("btags").hidden = false; $("btaghelp").hidden = false;
    $("btags").innerHTML = ["period", "topic"].filter(g => TAGS[g].length).map(g =>
      `<div class="tagrow" data-g="${g}"><span class="taglabel">${g === "period" ? "Period" : "Topic"}</span>` +
      TAGS[g].map((t, i) => `<button type="button" class="tag" data-g="${g}" data-i="${i}" aria-pressed="false">${esc(t)}<span class="n"></span></button>`).join("") +
      "</div>").join("");
  }
  apply();
}
function pickTag(g, t) { sel[g] = sel[g] === t ? null : t; apply(); }

function parseQuery(q) {
  const terms = []; const re = /(-?)(?:(author|title|notes):)?(?:"([^"]+)"|(\S+))/gi; let m;
  while ((m = re.exec(q))) { const t = fold(m[3] || m[4]); if (t) terms.push({ neg: !!m[1], field: (m[2] || "").toLowerCase(), t }); }
  return terms;
}

// How well an entry answers what was typed. The whole phrase in the title counts for most, then how
// many of the words are in the title, how close together they sit, and whether they fall on word
// boundaries; the author counts for less and the notes for little. This ordering is used only while
// the search box has something in it and no column has been clicked.
const WORDCH = /[a-z0-9]/;
const wholeWord = (s, i, w) =>
  (i === 0 || !WORDCH.test(s[i - 1])) && (i + w.length === s.length || !WORDCH.test(s[i + w.length]));
function relevance(r, words, phrase) {
  const t = r.ft, a = r.fa, o = r.fn;
  let s = 0;
  if (phrase) {
    if (t === phrase) s += 400;
    else if (t.startsWith(phrase)) s += 230;
    else if (phrase.includes(" ") && t.includes(phrase)) s += 170;
    if (phrase.includes(" ")) { if (a.includes(phrase)) s += 90; else if (o.includes(phrase)) s += 30; }
  }
  const spans = []; let inTitle = 0, elsewhere = 0;
  for (const w of words) {
    const i = t.indexOf(w);
    if (i >= 0) { inTitle++; spans.push([i, i + w.length]); s += wholeWord(t, i, w) ? 20 : 11; if (i === 0) s += 8; }
    else {
      const j = a.indexOf(w);
      if (j >= 0) { elsewhere++; s += wholeWord(a, j, w) ? 14 : 8; }
      else if (o.includes(w)) { elsewhere++; s += 4; }
    }
  }
  if (words.length) {
    if (inTitle === words.length) s += 70;
    else if (inTitle + elsewhere === words.length) s += 25;
    if (spans.length > 1) {
      const lo = Math.min(...spans.map(x => x[0])), hi = Math.max(...spans.map(x => x[1]));
      const ideal = words.reduce((n, w) => n + w.length, 0) + words.length - 1;
      s += Math.max(0, 45 - Math.round((hi - lo - ideal) / 3));
    }
  }
  s -= Math.min(25, t.length / 30);
  if (r.nlinks) s += 2;
  return s;
}
const searchPhrase = q => fold(q).replace(/(^|\s)-\S+/g, " ").replace(/\b(author|title|notes):/g, " ")
  .replace(/["']/g, " ").replace(/\s+/g, " ").trim();

function apply() {
  const terms = parseQuery($("bq").value), fld = $("bfield").value;
  const y1 = parseInt($("by1").value) || null, y2 = parseInt($("by2").value) || null;
  const shw = $("bshow").value, hst = $("bhost").value, lng = $("blang").value;
  const key = f => f === "author" ? "fa" : f === "title" ? "ft" : f === "notes" ? "fn" : "fall";
  const tagOk = (r, skip) => ["period", "topic"].every(g => g === skip || !sel[g] || r.tags.includes(sel[g]));
  const base = ALL.filter(r => {
    if (y1 || y2) { if (r.year_num == null) return false; if (y1 && r.year_num < y1) return false; if (y2 && r.year_num > y2) return false; }
    if (hst && !r.links.some(l => holder(l.url) === hst)) return false;
    if (lng && r.language !== lng) return false;
    if (shw === "ia" && !r.nlinks) return false;
    for (const t of terms) { const hit = r[key(t.field || fld)].includes(t.t); if (hit === t.neg) return false; }
    return true;
  });
  VIEW = base.filter(r => tagOk(r));
  // each tag button says how many entries it would leave, given everything else that is chosen
  for (const b of document.querySelectorAll("#btags button.tag")) {
    const g = b.dataset.g, t = TAGS[g][b.dataset.i];
    const n = base.filter(r => tagOk(r, g) && r.tags.includes(t)).length;
    b.querySelector(".n").textContent = n;
    b.setAttribute("aria-pressed", sel[g] === t ? "true" : "false");
    b.disabled = !n && sel[g] !== t;
  }
  const words = terms.filter(t => !t.neg && t.field !== "notes").map(t => t.t);
  byMatch = !sortKey && words.length > 0;
  if (byMatch) {
    const phrase = searchPhrase($("bq").value);
    for (const r of VIEW) r.rel = relevance(r, words, phrase);
    VIEW.sort((x, y) => y.rel - x.rel || (x.year_num || 9999) - (y.year_num || 9999) || x.id - y.id);
  }
  if (sortKey) {
    const k = sortKey, d = sortDir;
    VIEW.sort((a, b) => {
      let x = a[k], y = b[k];
      if (k === "author") { x = a.fa || "￿"; y = b.fa || "￿"; } else if (k === "title") { x = a.ft; y = b.ft; }
      if (x == null) return 1; if (y == null) return -1;
      return (x < y ? -1 : x > y ? 1 : a.id - b.id) * d;
    });
  }
  render(terms);
}
function titleCell(r, terms) {
  if (r.title.length <= CUT + 20) return hl(r.title, terms);   // not worth cutting a few words off
  let at = r.title.lastIndexOf(" ", CUT);
  if (at < CUT * 0.6) at = CUT;
  const short = r.title.slice(0, at).replace(/[\s,.;:]+$/, "");
  const open = expanded.has(r.id);
  return `<span class="tshort"${open ? " hidden" : ""}>${hl(short, terms)}… <button type="button" class="more" aria-expanded="false" title="Show the full title">more</button></span>` +
    `<span class="tfull"${open ? "" : " hidden"}>${hl(r.title, terms)} <button type="button" class="more" aria-expanded="true" title="Shorten the title">less</button></span>`;
}
function hl(text, terms) {
  let out = text; if (!terms.length) return esc(out);
  for (const t of terms) { if (t.neg || t.t.length < 2) continue;
    const parts = text.split(/(\s+)/); out = parts.map(w => fold(w).includes(t.t) ? "\u0002" + w + "\u0003" : w).join(""); text = out; }
  return esc(out).replace(/\u0002+/g, "<mark>").replace(/\u0003+/g, "</mark>");
}
function render(terms) {
  terms = terms || parseQuery($("bq").value);
  $("brows").innerHTML = VIEW.map((r, i) => `<tr data-i="${i}">
    <td class="au">${hl(r.author, terms) || '<span class="chip">no author</span>'}</td>
    <td class="title"${r.title.length > CUT + 20 ? ` title="${esc(r.title)}"` : ""}>${titleCell(r, terms)}${r.notes ? `<span class="note">${md(r.notes)}</span>` : ""}${coins(r)}</td>
    <td class="year">${esc(r.year)}</td>
    <td class="ia">${r.nlinks ? `<a class="pill" href="${esc(r.links[0].url)}" target="_blank" rel="noopener" title="${esc(holderName(holder(r.links[0].url)))}"><span class="host">${holder(r.links[0].url)}: </span>${esc(r.links[0].label || "read")} ↗</a>${r.nlinks > 1 ? ` <span class="chip" title="more copies or volumes - open the entry">+${r.nlinks - 1}</span>` : ""}` : ""}</td></tr>`).join("");
  $("bempty").hidden = VIEW.length > 0;
  if ($("bdlg").open) for (const el of document.querySelectorAll("#brows span.Z3988")) el.className = "Z3988off";
  zoteroLook();
  $("bcount").textContent = `${VIEW.length.toLocaleString()} of ${ALL.length.toLocaleString()} entries` + (byMatch ? " · best match first (click a column to sort instead)" : "");
  document.querySelectorAll(".books th").forEach(th => th.querySelector(".arrow").textContent = th.dataset.k === sortKey ? (sortDir > 0 ? "▲" : "▼") : "");
}
function citation(r) { return [r.author ? r.author + (/[.]$/.test(r.author) ? "" : ".") : "", r.title + (/[.?!]$/.test(r.title) ? "" : "."), [r.imprint, r.year].filter(Boolean).join(", ")].filter(Boolean).join(" ").replace(/\s+/g, " ") + (r.imprint || r.year ? "." : ""); }
function show(i) {
  if (i < 0 || i >= VIEW.length) return; cur = i; const r = VIEW[i];
  $("bdtitle").innerHTML = esc(r.title) + coins(r);
  const tags = r.tags.map(t => `<button type="button" class="chip" data-tag="${esc(t)}" title="List the entries with this tag">${esc(t)}</button>`).join(" ");
  const links = r.nlinks ? r.links.map(l => `<a href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.label || r.title)}</a> <span class="chip">${esc(holderName(holder(l.url)))}</span>`).join("<br>") : "no copy found online";
  $("bddl").innerHTML = [["Author", esc(r.author) || "—"], ["Year", esc(r.year)], ["Imprint", esc(r.imprint)], ["Language", esc(r.language)], ["Tags", tags], ["Notes", md(r.notes)], ["Online copy", links]]
    .filter(([, v]) => v).map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("");
  $("bdsearch").href = "https://archive.org/search?query=" + encodeURIComponent(`title:(${r.title.split(/[.;:]/)[0]})` + (r.author ? ` AND creator:(${r.author.split(",")[0]})` : ""));
  $("bdprev").disabled = i === 0; $("bdnext").disabled = i === VIEW.length - 1;
  if (!$("bdlg").open) $("bdlg").showModal();
  coinsMode(true);
}

// half a second after the last keystroke, so that typing a phrase does not re-filter on every letter; Enter searches at once
let tmr; const debounced = () => { clearTimeout(tmr); tmr = setTimeout(apply, 500); };
$("bq").addEventListener("input", debounced);
$("bq").addEventListener("keydown", e => { if (e.key === "Enter") { clearTimeout(tmr); apply(); } });
for (const id of ["bfield", "by1", "by2", "bhost", "blang", "bshow"]) $(id).addEventListener("input", apply);
$("btags").addEventListener("click", e => { const b = e.target.closest("button.tag"); if (b) pickTag(b.dataset.g, TAGS[b.dataset.g][b.dataset.i]); });
// a tag in an open entry lists everything else with that tag
$("bddl").addEventListener("click", e => {
  const b = e.target.closest("button[data-tag]"); if (!b) return;
  const t = b.dataset.tag, g = PERIOD.test(t) ? "period" : "topic";
  sel[g] = t; $("bdlg").close(); apply(); $("books").scrollIntoView({ behavior: "smooth", block: "start" });
});
$("breset").onclick = () => {
  $("bq").value = ""; $("bfield").value = "all"; $("by1").value = $("by2").value = ""; $("bhost").value = "";
  $("blang").value = ""; $("bshow").value = "all"; sel.period = sel.topic = null; sortKey = null; sortDir = 1; apply(); $("bq").focus();
};
document.querySelectorAll(".books th").forEach(th => th.onclick = () => { const k = th.dataset.k; if (sortKey === k) { if (sortDir === 1) sortDir = -1; else { sortKey = null; sortDir = 1; } } else { sortKey = k; sortDir = 1; } apply(); });
$("brows").addEventListener("click", e => {
  const more = e.target.closest("button.more");
  if (more) {                        // more / less: the title opens or closes where it is, the entry stays shut
    const td = more.closest("td"), id = VIEW[parseInt(td.parentElement.dataset.i)].id;
    if (expanded.has(id)) expanded.delete(id); else expanded.add(id);
    td.querySelector(".tshort").hidden = expanded.has(id); td.querySelector(".tfull").hidden = !expanded.has(id);
    return;
  }
  if (e.target.closest("a")) return; const tr = e.target.closest("tr"); if (tr) show(parseInt(tr.dataset.i)); });
$("bdclose").onclick = () => $("bdlg").close();
$("bdlg").addEventListener("close", () => coinsMode(false));
$("bdlg").addEventListener("click", e => { if (e.target === $("bdlg")) $("bdlg").close(); });
$("bdprev").onclick = () => show(cur - 1); $("bdnext").onclick = () => show(cur + 1);
document.addEventListener("keydown", e => { if ($("bdlg").open) { if (e.key === "ArrowLeft") show(cur - 1); if (e.key === "ArrowRight") show(cur + 1); } });
const copy = (t, b) => navigator.clipboard.writeText(t).then(() => { const o = b.textContent; b.textContent = "Copied ✓"; setTimeout(() => b.textContent = o, 1200); });
$("bdcopy").onclick = e => copy(citation(VIEW[cur]), e.target);
const save = (text, type, name) => {
  const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([text], { type })); a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 2000);
};
// the same columns as page/books.csv, so an export can be pasted back into it
$("bcsv").onclick = () => {
  const cols = ["author", "title", "year", "imprint", "language", "links", "tags", "notes"];
  const val = (r, c) => c === "links" ? r.links.map(l => (l.label ? l.label + " " : "") + l.url).join(" ; ") : c === "tags" ? r.tags.join(" ; ") : r[c];
  const q = v => '"' + String(v == null ? "" : v).replace(/"/g, '""').replace(/\n/g, " ") + '"';
  save("﻿" + cols.join(",") + "\n" + VIEW.map(r => cols.map(c => q(val(r, c))).join(",")).join("\n"), "text/csv", EXPORT + "-results.csv");
};

// COinS (the Z3988 span) so that Zotero's connector can take an entry straight off the page: one in
// every row of the table and one in the open entry. While an entry is open the spans in the rows are
// set aside (their class changed), so that Zotero offers that one record rather than the whole list.
function coinsMode(single) {
  const off = single ? "Z3988" : "Z3988off", on = single ? "Z3988off" : "Z3988";
  for (const el of document.querySelectorAll("#brows span." + off)) el.className = on;
  zoteroLook();
}
function coins(r) {
  const f = [["ctx_ver", "Z39.88-2004"], ["rft_val_fmt", "info:ofi/fmt:kev:mtx:book"], ["rft.genre", "book"],
             ["rft.btitle", r.title], ["rft.title", r.title], ["rft.au", r.author], ["rft.date", r.year],
             ["rft.language", r.language], ["rft_id", r.nlinks ? r.links[0].url : ""]];
  const q = f.filter(([, v]) => v).map(([k, v]) => k + "=" + encodeURIComponent(v)).join("&");
  return `<span class="Z3988" title="${esc(q)}"></span>`;
}
let zoteroAt = 0, zoteroTmr;
function zoteroLook() {
  clearTimeout(zoteroTmr);
  const wait = Math.max(0, 3000 - (Date.now() - zoteroAt));
  zoteroTmr = setTimeout(() => { zoteroAt = Date.now(); document.dispatchEvent(new Event("ZoteroItemUpdated", { bubbles: true, cancelable: true })); }, wait);
}

// BibTeX for whatever the filters have left, so a result list can go straight into a reference manager
const bibEsc = s => String(s == null ? "" : s).replace(/[{}]/g, "").replace(/\\/g, "").replace(/\s+/g, " ").trim();
function bibKey(r, used) {
  const sur = (r.author || "").split(",")[0].split(/\s+/).filter(Boolean).pop() || "anon";
  const word = (r.title || "").split(/\s+/).find(w => w.length > 3 && /^[A-Za-z]/.test(w)) || "";
  let k = (fold(sur) + (r.year_num || "nd") + fold(word)).replace(/[^a-z0-9]/g, "");
  if (used.has(k)) { let n = 2; while (used.has(k + n)) n++; k += n; }
  used.add(k);
  return k;
}
function bibEntry(r, used) {
  const f = [["author", r.author], ["title", r.title], ["year", r.year], ["publisher", r.imprint], ["language", r.language], ["keywords", r.tags.join(", ")],
             ["url", r.nlinks ? r.links[0].url : ""], ["note", plain(r.notes)]];
  const lines = f.filter(([, v]) => bibEsc(v)).map(([k, v]) => `  ${k} = {${bibEsc(v)}}`);
  return `@book{${bibKey(r, used)},\n${lines.join(",\n")}\n}`;
}
$("bbib").onclick = () => {
  const used = new Set();
  save("% " + VIEW.length + " entries from " + location.origin + location.pathname + " (" + new Date().toISOString().slice(0, 10) + ")\n\n" +
    VIEW.map(r => bibEntry(r, used)).join("\n\n") + "\n", "application/x-bibtex", EXPORT + "-results.bib");
};

load();
})();
