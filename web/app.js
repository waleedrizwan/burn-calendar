// Burning Activity Calendar front end. Plain JavaScript, no build step. API contract: docs/api.md.

// Sequential ramp: cividis (colour-vision-deficiency safe, perceptually uniform, readable in greyscale).
const CIVIDIS = ["#00224e", "#123570", "#3b496c", "#575d6d", "#707173", "#8a8678", "#a59c74", "#c3b369", "#e1cc55", "#fee838"];
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const MONTHS_LONG = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
// Anomaly classes: blue to orange diverging palette (safe for red-green colour blindness) plus a symbol,
// so colour is never the only signal.
const CATS = {
  record_high: { label: "Record high", color: "#7f3b08", sym: "★" },
  well_above: { label: "Well above normal", color: "#e66101", sym: "▲▲" },
  above: { label: "Above normal", color: "#fdb863", sym: "▲" },
  near_normal: { label: "Near normal", color: "#eeeeee", sym: "·" },
  below: { label: "Below normal", color: "#92c5de", sym: "▼" },
  well_below: { label: "Well below normal", color: "#2166ac", sym: "▼▼" },
  low_activity: { label: "Too little activity to compare", color: "#ffffff", sym: "" },
  partial: { label: "Month not complete", color: "#ffffff", sym: "" },
  no_baseline: { label: "No baseline", color: "#ffffff", sym: "" },
};
const fmt = new Intl.NumberFormat("en", { maximumFractionDigits: 0 });
const fmt1 = new Intl.NumberFormat("en", { maximumFractionDigits: 1 });
const $ = id => document.getElementById(id);
const state = { regions: [], data: null, view: "activity", query: "" };

function hexToRgb(h) { return [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16)); }
function ramp(t) {
  const x = Math.max(0, Math.min(1, t)) * (CIVIDIS.length - 1);
  const i = Math.min(CIVIDIS.length - 2, Math.floor(x)), f = x - i;
  const a = hexToRgb(CIVIDIS[i]), b = hexToRgb(CIVIDIS[i + 1]);
  return a.map((v, k) => Math.round(v + (b[k] - v) * f));
}
function textOn([r, g, b]) { return (0.299 * r + 0.587 * g + 0.114 * b) > 140 ? "#111111" : "#ffffff"; }
function ordinal(n) { const s = ["th", "st", "nd", "rd"], v = n % 100; return n + (s[(v - 20) % 10] || s[v] || s[0]); }
function esc(s) { return String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }

async function getJSON(url) {
  const r = await fetch(url);
  const body = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(typeof body.detail === "string" ? body.detail : (r.statusText || "request failed"));
  return body;
}

// ---------- area selection ----------
let map, shape, drawStart = null;

function mode() { return document.querySelector('input[name="mode"]:checked').value; }
function region() { return state.regions.find(r => r.id === $("region").value); }

function areaParams() {
  const p = new URLSearchParams({ region: $("region").value });
  const num = id => { const v = parseFloat($(id).value); if (Number.isNaN(v)) throw new Error(`Enter a number for ${$(id).labels[0].textContent.toLowerCase()}.`); return v; };
  if (mode() === "bbox") p.set("bbox", [num("west"), num("south"), num("east"), num("north")].join(","));
  if (mode() === "circle") { p.set("lat", num("lat")); p.set("lon", num("lon")); p.set("radius_km", num("radius")); }
  return p;
}

function drawShape() {
  if (!map) return;
  if (shape) { shape.remove(); shape = null; }
  const style = { color: "#c2410c", weight: 2, fillOpacity: 0.12 };
  const v = id => parseFloat($(id).value);
  if (mode() === "bbox" && ![v("west"), v("south"), v("east"), v("north")].some(Number.isNaN)) {
    shape = L.rectangle([[v("south"), v("west")], [v("north"), v("east")]], style).addTo(map);
  } else if (mode() === "circle" && ![v("lat"), v("lon"), v("radius")].some(Number.isNaN)) {
    shape = L.circle([v("lat"), v("lon")], { ...style, radius: v("radius") * 1000 }).addTo(map);
  } else if (mode() === "region" && region()) {
    const [w, s, e, n] = region().bbox;
    shape = L.rectangle([[s, w], [n, e]], { ...style, fillOpacity: 0.04, dashArray: "6 6" }).addTo(map);
  }
}

function setMode() {
  $("bbox-fields").hidden = mode() !== "bbox";
  $("circle-fields").hidden = mode() !== "circle";
  if (map) { if (mode() === "bbox") map.dragging.disable(); else map.dragging.enable(); }
  if (map) map.getContainer().style.cursor = mode() === "region" ? "" : "crosshair";
  drawShape();
}

function fitRegion() {
  if (!map || !region()) return;
  const [w, s, e, n] = region().bbox;
  map.fitBounds([[s, w], [Math.min(n, 72), e]]);
}

function initMap() {
  if (!window.L) { $("map").textContent = "The map could not be loaded. Type the area in the form instead."; return; }
  map = L.map("map", { worldCopyJump: true });
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 12, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);
  const r4 = x => Math.round(x * 1e4) / 1e4;
  map.on("click", e => {
    if (mode() !== "circle") return;
    $("lat").value = r4(e.latlng.lat); $("lon").value = r4(e.latlng.lng); drawShape();
  });
  map.on("mousedown", e => { if (mode() === "bbox") drawStart = e.latlng; });
  map.on("mousemove", e => {
    if (!drawStart) return;
    $("west").value = r4(Math.min(drawStart.lng, e.latlng.lng)); $("east").value = r4(Math.max(drawStart.lng, e.latlng.lng));
    $("south").value = r4(Math.min(drawStart.lat, e.latlng.lat)); $("north").value = r4(Math.max(drawStart.lat, e.latlng.lat));
    drawShape();
  });
  map.on("mouseup", () => { drawStart = null; });
}

// ---------- rendering ----------
function renderNow(d) {
  const c = d.current, cat = CATS[c.category] || CATS.no_baseline;
  const when = `${MONTHS_LONG[c.month - 1]} ${c.year}` + (c.complete ? "" : `, days 1 to ${c.through_day}`);
  const rgb = hexToRgb(cat.color);
  $("now-headline").innerHTML = `${esc(when)}: <strong>${fmt.format(c.value)}</strong> ${esc(d.unit.short)} ` +
    `<span class="tag" style="background:${cat.color};color:${textOn(rgb)}">${cat.sym ? cat.sym + " " : ""}${esc(cat.label)}</span>`;
  const span = `${c.baseline_years[0]} to ${c.baseline_years[1]}`;
  const same = c.complete ? `${MONTHS_LONG[c.month - 1]}` : `the same days of ${MONTHS_LONG[c.month - 1]}`;
  let t = `The median for ${same} over ${span} is ${fmt.format(c.baseline_median_to_date)} ` +
    `(middle half of years: ${fmt.format(c.baseline_p25_to_date)} to ${fmt.format(c.baseline_p75_to_date)}; highest: ${fmt.format(c.baseline_max_to_date)}). `;
  if (c.ratio_to_median !== null) t += `This year is ${fmt1.format(c.ratio_to_median)} times the median and ranks ${ordinal(c.rank)} highest of ${c.of} years. `;
  else if (c.category === "low_activity") t += "There is too little burning here in this month for a meaningful comparison. ";
  if (c.provisional) t += "Recent days use near real-time data and may change. ";
  t += `Data through ${d.period.last_data_date} (UTC).`;
  $("now-detail").textContent = t;
  $("now").hidden = false;
}

function renderCalendar(d) {
  const byYear = new Map();
  for (const c of d.cells) {
    if (!byYear.has(c.year)) byYear.set(c.year, new Array(12).fill(null));
    byYear.get(c.year)[c.month - 1] = c;
  }
  const max = Math.max(1, ...d.cells.map(c => c.value));
  const anomaly = state.view === "anomaly";
  $("cal-desc").textContent = anomaly
    ? "Each month compared with the same calendar month in every other complete year since 2001."
    : `${d.unit.label}. One unit is one 0.1 degree grid cell (about 11 km) with at least one hotspot detection on one day.`;
  const table = $("calendar");
  table.innerHTML = "";
  table.createCaption().textContent = "Rows are years, newest first. Columns are months. " +
    (anomaly ? "Colour and symbol show the difference from normal; the number is the burning activity."
             : "Darker blue is less burning, brighter yellow is more.");
  table.createTHead().insertRow().innerHTML = `<th scope="col">Year</th>` +
    MONTHS.map(m => `<th scope="col">${m}</th>`).join("") + `<th scope="col">Year total</th>`;
  const body = table.createTBody();
  let anyProv = false;
  for (const [year, cells] of [...byYear.entries()].sort((a, b) => b[0] - a[0])) {
    const tr = body.insertRow();
    tr.innerHTML = `<th scope="row">${year}</th>`;
    let total = 0;
    cells.forEach((c, i) => {
      const td = tr.insertCell();
      if (!c) { td.className = "none"; td.textContent = "–"; td.title = `${MONTHS[i]} ${year}: outside the record or the selected years`; return; }
      total += c.value;
      const cat = CATS[c.category] || CATS.no_baseline;
      const rgb = anomaly ? hexToRgb(cat.color) : ramp(Math.sqrt(c.value / max));
      td.className = "cell" + (c.partial ? " partial" : "");
      td.style.background = `rgb(${rgb})`; td.style.color = textOn(rgb);
      const marks = (c.lower_confidence ? "†" : "") + (c.gap_days ? "‡" : "");
      td.textContent = (anomaly && cat.sym ? cat.sym + " " : "") + fmt.format(c.value) + marks;
      anyProv = anyProv || c.provisional;
      td.title = `${MONTHS_LONG[i]} ${year}: ${fmt1.format(c.value)} ${d.unit.short}. ${cat.label}` +
        (c.ratio_to_median !== null ? ` (${fmt1.format(c.ratio_to_median)} times the median, ${ordinal(Math.round(c.percentile))} percentile).` : ".") +
        ` Source: ${c.sources.map(s => d.source_labels[s]).join(", ") || "no data"}.` +
        (c.gap_days ? ` ${c.gap_days} day(s) without satellite data.` : "") +
        (c.provisional ? " Includes near real-time data." : "");
    });
    const tt = tr.insertCell(); tt.className = "total"; tt.textContent = fmt.format(total);
  }
  $("prov-note").textContent = anyProv ? "The most recent months include near real-time data that NASA later replaces with standard-quality data." : "";
  $("legend").innerHTML = anomaly
    ? ["well_below", "below", "near_normal", "above", "well_above", "record_high", "low_activity"].map(k =>
        `<span><span class="sw" style="background:${CATS[k].color}"></span>${CATS[k].sym} ${CATS[k].label}</span>`).join("")
    : `<span>0</span><span class="ramp" style="background:linear-gradient(90deg,${CIVIDIS.join(",")})"></span>` +
      `<span>${fmt.format(max)} ${esc(d.unit.short)} in a month (square-root colour scale)</span>`;
  $("cal").hidden = false;
}

function svgEl(w, h, title, desc) {
  return [`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(title)}">`,
          `<title>${esc(title)}</title><desc>${esc(desc)}</desc>`];
}
function niceMax(v) { const p = Math.pow(10, Math.floor(Math.log10(Math.max(v, 1)))); return Math.ceil(v / p * 2) / 2 * p; }

function renderSeason(d) {
  const W = 760, H = 300, L = 64, R = 16, T = 16, B = 44;
  const base = new Map(d.baseline.map(b => [b.month, b]));
  const cy = d.current.year;
  const cur = d.allCells.filter(c => c.year === cy);
  const ymax = niceMax(Math.max(...d.baseline.map(b => b.p90), ...cur.map(c => c.value), 1));
  const x = m => L + (m - 0.5) * (W - L - R) / 12, y = v => T + (1 - v / ymax) * (H - T - B);
  const band = (lo, hi) => { const ms = [...base.keys()].sort((a, b) => a - b);
    return ms.map((m, i) => `${i ? "L" : "M"}${x(m)},${y(base.get(m)[hi])}`).join("") +
           ms.reverse().map(m => `L${x(m)},${y(base.get(m)[lo])}`).join("") + "Z"; };
  const line = pts => pts.map((p, i) => `${i ? "L" : "M"}${x(p[0])},${y(p[1])}`).join("");
  const s = svgEl(W, H, `Burning activity by month in ${cy} against the historical range`,
    `Monthly ${d.unit.short}. Bands show the 10th to 90th and 25th to 75th percentiles and the line the median over ${d.current.baseline_years.join(" to ")}.`);
  for (let i = 0; i <= 4; i++) { const v = ymax * i / 4;
    s.push(`<line class="axis" x1="${L}" x2="${W - R}" y1="${y(v)}" y2="${y(v)}"/><text class="muted" x="${L - 8}" y="${y(v) + 4}" text-anchor="end">${fmt.format(v)}</text>`); }
  MONTHS.forEach((m, i) => s.push(`<text class="muted" x="${x(i + 1)}" y="${H - B + 18}" text-anchor="middle">${m}</text>`));
  s.push(`<path d="${band("p10", "p90")}" fill="var(--band2, #e3e8f2)"/><path d="${band("p25", "p75")}" fill="var(--band1, #c9d3e6)"/>`);
  s.push(`<path d="${line(d.baseline.map(b => [b.month, b.median]))}" fill="none" stroke="var(--series, #00224e)" stroke-width="2" stroke-dasharray="6 4"/>`);
  const done = cur.filter(c => !c.partial);
  s.push(`<path d="${line(done.map(c => [c.month, c.value]))}" fill="none" stroke="var(--now, #c2410c)" stroke-width="2.5"/>`);
  cur.forEach(c => s.push(`<circle cx="${x(c.month)}" cy="${y(Math.min(c.value, ymax))}" r="4" fill="${c.partial ? "none" : "var(--now, #c2410c)"}" stroke="var(--now, #c2410c)" stroke-width="2"><title>${MONTHS_LONG[c.month - 1]} ${cy}: ${fmt.format(c.value)}${c.partial ? " (month not complete)" : ""}</title></circle>`));
  const ly = H - 8;
  s.push(`<rect x="${L}" y="${ly - 10}" width="14" height="10" fill="var(--band2, #e3e8f2)"/><text x="${L + 20}" y="${ly}">10th to 90th percentile</text>`,
         `<rect x="${L + 180}" y="${ly - 10}" width="14" height="10" fill="var(--band1, #c9d3e6)"/><text x="${L + 200}" y="${ly}">25th to 75th</text>`,
         `<line x1="${L + 300}" x2="${L + 324}" y1="${ly - 5}" y2="${ly - 5}" stroke="var(--series, #00224e)" stroke-width="2" stroke-dasharray="6 4"/><text x="${L + 330}" y="${ly}">median</text>`,
         `<line x1="${L + 400}" x2="${L + 424}" y1="${ly - 5}" y2="${ly - 5}" stroke="var(--now, #c2410c)" stroke-width="2.5"/><text x="${L + 430}" y="${ly}">${cy} (open circle: month not complete)</text>`, "</svg>");
  $("season-chart").innerHTML = s.join("");
  $("season-title").textContent = `Season: ${cy} against the historical range`;
  $("season").hidden = false;
}

function renderYears(d) {
  const W = 760, H = 260, L = 64, R = 16, T = 12, B = 30;
  const ys = d.years.filter(yr => yr.year >= 2001);
  const ymax = niceMax(Math.max(...ys.map(yr => yr.total), 1));
  const bw = (W - L - R) / ys.length;
  const y = v => T + (1 - v / ymax) * (H - T - B);
  const s = svgEl(W, H, "Burning activity per year", `Yearly total of ${d.unit.short}, ${ys[0].year} to ${ys[ys.length - 1].year}.`);
  for (let i = 0; i <= 4; i++) { const v = ymax * i / 4;
    s.push(`<line class="axis" x1="${L}" x2="${W - R}" y1="${y(v)}" y2="${y(v)}"/><text class="muted" x="${L - 8}" y="${y(v) + 4}" text-anchor="end">${fmt.format(v)}</text>`); }
  ys.forEach((yr, i) => {
    const x = L + i * bw + 2;
    s.push(`<rect x="${x}" y="${y(yr.total)}" width="${bw - 4}" height="${Math.max(0, y(0) - y(yr.total))}" fill="${yr.partial ? "none" : "var(--series, #00224e)"}" stroke="var(--series, #00224e)" ${yr.partial ? 'stroke-dasharray="4 3"' : ""}><title>${yr.year}: ${fmt.format(yr.total)}${yr.partial ? " (year not complete)" : ""}</title></rect>`);
    if (yr.year % 5 === 0 || (i === ys.length - 1 && yr.year % 5 > 1)) s.push(`<text class="muted" x="${x + bw / 2 - 2}" y="${H - B + 16}" text-anchor="middle">${yr.year}</text>`);
  });
  const x2012 = L + ys.findIndex(yr => yr.year === 2012) * bw;
  if (x2012 > L) s.push(`<line x1="${x2012}" x2="${x2012}" y1="${T}" y2="${H - B}" stroke="currentColor" stroke-dasharray="2 4" opacity="0.6"/><text class="muted" x="${x2012 - 6}" y="${T + 10}" text-anchor="end">converted from MODIS</text><text class="muted" x="${x2012 + 6}" y="${T + 10}">VIIRS</text>`);
  s.push("</svg>");
  $("years-chart").innerHTML = s.join("");
  const t = d.trend;
  $("trend").textContent = !t.available ? "" :
    t.direction === "none"
      ? `No clear trend from ${t.start_year} to ${t.end_year} (Mann-Kendall test, p = ${t.p_value}). Dashed bar: year not complete.`
      : `Burning activity has trended ${t.direction} from ${t.start_year} to ${t.end_year}` +
        (t.percent_per_decade !== null ? `, by about ${fmt1.format(Math.abs(t.percent_per_decade))} percent of a typical year per decade` : "") +
        ` (Theil-Sen slope, Mann-Kendall p = ${t.p_value}). Dashed bar: year not complete.`;
  $("years").hidden = false;
}

function render(d) {
  $("warnings").innerHTML = d.warnings.map(w => `<p class="notice" role="note">${esc(w)}</p>`).join("");
  renderNow(d); renderCalendar(d); renderSeason(d); renderYears(d);
  $("dl-monthly").href = `/api/calendar.csv?${state.query}`;
  $("downloads").hidden = false;
}

async function load(focus) {
  const err = $("error"); err.hidden = true;
  let p;
  try { p = areaParams(); } catch (e) { err.textContent = e.message; err.hidden = false; return; }
  const all = new URLSearchParams(p);
  const y0 = +$("from-year").value, y1 = +$("to-year").value;
  if (y0 > y1) { err.textContent = "The first year must not be after the last year."; err.hidden = false; return; }
  p.set("start", `${y0}-01`); p.set("end", `${y1}-12`);
  $("status").textContent = "Loading…";
  try {
    // The full record is always needed for the season chart; the calendar shows the selected years.
    const full = await getJSON(`/api/calendar?${all}`);
    const d = { ...full, allCells: full.cells, cells: full.cells.filter(c => c.year >= y0 && c.year <= y1) };
    state.data = d; state.query = p.toString(); state.area = all.toString();
    render(d);
    const a = d.area;
    $("status").textContent = `Showing ${region().name}, ` + (a.type === "region" ? "whole region" :
      a.type === "bbox" ? `rectangle ${a.bbox.join(", ")} (west, south, east, north)` :
      `${a.radius_km} km around ${a.lat}, ${a.lon}`) + `, ${y0} to ${y1}.`;
    if (focus) $("results").focus();
  } catch (e) {
    err.textContent = `Could not load the calendar: ${e.message}`; err.hidden = false; $("status").textContent = "";
  }
}

function downloadSvg(id, name) {
  const svg = $(id).querySelector("svg"); if (!svg) return;
  const cs = getComputedStyle(document.documentElement);
  let text = new XMLSerializer().serializeToString(svg)
    .replace(/var\((--[a-z0-9]+), ([^)]+)\)/g, (_, v, fb) => cs.getPropertyValue(v).trim() || fb);
  text = text.replace(/<svg /, `<svg font-family="sans-serif" font-size="12" `);
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([text], { type: "image/svg+xml" }));
  a.download = `burning_activity_${name}_${$("region").value}.svg`; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

async function downloadHotspots(e) {
  e.preventDefault();
  const err = $("dl-error"); err.hidden = true;
  const url = `/api/hotspots.csv?${state.area}&start=${$("hs-start").value}&end=${$("hs-end").value}`;
  try {
    const r = await fetch(url);
    if (!r.ok) { const b = await r.json().catch(() => ({})); throw new Error(typeof b.detail === "string" ? b.detail : "the download failed"); }
    const blob = await r.blob();
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = (r.headers.get("Content-Disposition") || "").match(/filename="([^"]+)"/)?.[1] || "hotspots.csv";
    a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  } catch (ex) { err.textContent = `Could not download: ${ex.message}`; err.hidden = false; }
}

(async () => {
  try { initMap(); } catch (e) { $("map").textContent = "The map could not be loaded. Type the area in the form instead."; map = null; }
  try { state.regions = (await getJSON("/api/regions")).regions; }
  catch (e) { $("status").textContent = `Could not reach the data service: ${e.message}`; return; }
  $("region").innerHTML = state.regions.map(r => `<option value="${r.id}">${esc(r.name)} (${esc(r.regime)})</option>`).join("");
  const thisYear = new Date().getUTCFullYear();
  const opts = []; for (let y = 2000; y <= thisYear; y++) opts.push(`<option>${y}</option>`);
  $("from-year").innerHTML = opts.join(""); $("to-year").innerHTML = opts.join("");
  $("from-year").value = 2000; $("to-year").value = thisYear;
  const d = new Date(), iso = x => x.toISOString().slice(0, 10);
  $("hs-end").value = iso(d); d.setUTCDate(d.getUTCDate() - 30); $("hs-start").value = iso(d);

  $("region").addEventListener("change", () => { fitRegion(); drawShape(); if (mode() === "region") load(false); });
  document.querySelectorAll('input[name="mode"]').forEach(el => el.addEventListener("change", setMode));
  ["west", "south", "east", "north", "lat", "lon", "radius"].forEach(id => $(id).addEventListener("input", drawShape));
  document.querySelectorAll('input[name="view"]').forEach(el => el.addEventListener("change", () => {
    state.view = el.value; if (state.data) renderCalendar(state.data); }));
  $("controls").addEventListener("submit", e => { e.preventDefault(); load(true); });
  $("dl-hotspots").addEventListener("submit", downloadHotspots);
  document.querySelectorAll("button[data-svg]").forEach(b => b.addEventListener("click", () => downloadSvg(b.dataset.svg, b.dataset.name)));
  fitRegion(); setMode(); load(false);
})();
