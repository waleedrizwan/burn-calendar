// Colour ramp: cividis (colour-vision-deficiency safe, perceptually uniform, readable in greyscale).
const CIVIDIS = ["#00224e", "#123570", "#3b496c", "#575d6d", "#707173", "#8a8678", "#a59c74", "#c3b369", "#e1cc55", "#fee838"];
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const fmt = new Intl.NumberFormat("en");

function hexToRgb(h) { return [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16)); }
function ramp(t) {
  const x = Math.max(0, Math.min(1, t)) * (CIVIDIS.length - 1);
  const i = Math.min(CIVIDIS.length - 2, Math.floor(x)), f = x - i;
  const a = hexToRgb(CIVIDIS[i]), b = hexToRgb(CIVIDIS[i + 1]);
  return a.map((v, k) => Math.round(v + (b[k] - v) * f));
}
function textOn([r, g, b]) { return (0.299 * r + 0.587 * g + 0.114 * b) > 140 ? "#111" : "#fff"; }

async function getJSON(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || r.statusText);
  return r.json();
}

function render(data) {
  document.getElementById("cal-title").textContent = `${data.area.name}: ${data.unit.label}`;
  document.getElementById("cal-desc").textContent =
    `${data.unit.description} ${data.period.start} to ${data.period.end}; data through ${data.period.last_data_date}.`;
  const notice = document.getElementById("notice");
  notice.hidden = data.harmonized;
  notice.textContent = "Unharmonized preview. These are raw counts from one sensor family (MODIS) only. " +
    "They are not yet combined with VIIRS, so they should not be used to compare with VIIRS-era products.";

  const byYear = new Map();
  for (const c of data.cells) {
    if (!byYear.has(c.year)) byYear.set(c.year, new Array(12).fill(null));
    byYear.get(c.year)[c.month - 1] = c;
  }
  const max = Math.max(1, ...data.cells.map(c => c.value));
  const scale = v => Math.sqrt(v / max);  // square-root scale: counts are strongly skewed

  const table = document.getElementById("calendar");
  table.innerHTML = "";
  const cap = table.createCaption();
  cap.className = "desc"; cap.style.captionSide = "bottom"; cap.style.textAlign = "left"; cap.style.padding = "6px";
  cap.textContent = "Rows are years, columns are months. Darker blue is fewer detections, brighter yellow is more. Dashed outline: month not complete.";
  const head = table.createTHead().insertRow();
  head.insertAdjacentHTML("beforeend", `<th scope="col">Year</th>` +
    MONTHS.map(m => `<th scope="col">${m}</th>`).join("") + `<th scope="col">Year total</th>`);
  const body = table.createTBody();
  for (const [year, cells] of [...byYear.entries()].sort((a, b) => b[0] - a[0])) {
    const tr = body.insertRow();
    tr.insertAdjacentHTML("beforeend", `<th scope="row">${year}</th>`);
    let total = 0;
    cells.forEach((c, i) => {
      const td = tr.insertCell();
      if (!c) { td.className = "none"; td.textContent = "–"; td.title = `${MONTHS[i]} ${year}: no data`; return; }
      total += c.value;
      const rgb = ramp(scale(c.value));
      td.className = "cell" + (c.partial ? " partial" : "");
      td.style.background = `rgb(${rgb})`; td.style.color = textOn(rgb);
      td.textContent = fmt.format(c.value);
      td.title = `${MONTHS[i]} ${year}: ${fmt.format(c.value)} detections` +
        (c.partial ? " (month not complete)" : "") + (c.provisional ? " (includes near real-time data)" : "");
    });
    const tt = tr.insertCell(); tt.className = "total"; tt.textContent = fmt.format(total);
  }
  document.getElementById("legend").innerHTML =
    `<span>0</span><span class="ramp" style="background:linear-gradient(90deg,${CIVIDIS.join(",")})"></span>` +
    `<span>${fmt.format(max)} detections in a month (square-root scale)</span>`;
}

async function load() {
  const status = document.getElementById("status");
  const region = document.getElementById("region").value;
  status.textContent = "Loading…";
  try { render(await getJSON(`/api/calendar?region=${encodeURIComponent(region)}&series=modis_raw`)); status.textContent = ""; }
  catch (e) { status.textContent = `Could not load the calendar: ${e.message}`; }
}

(async () => {
  const sel = document.getElementById("region");
  const { regions } = await getJSON("/api/regions");
  sel.innerHTML = regions.map(r => `<option value="${r.id}">${r.name} (${r.regime})</option>`).join("");
  sel.addEventListener("change", load);
  load();
})();
