#!/usr/bin/env python3
"""Offline kanban view over the task files in this folder.

Run:  python3 tasks/board.py [port]     then open http://127.0.0.1:8765
Standard library only. The markdown files are the source of truth; the board edits them in place.
"""
import json
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

TASKS = Path(__file__).resolve().parent
STATUSES = ["todo", "in-progress", "done"]
FRONT = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)
CHECK = re.compile(r"^(- \[)([ xX])(\])", re.M)


def parse(path):
    m = FRONT.match(path.read_text(encoding="utf-8"))
    if not m:
        return None
    task = {}
    for line in m.group(1).splitlines():
        key, _, value = line.partition(":")
        task[key.strip()] = value.strip()
    task["depends"] = [d.strip() for d in task.get("depends", "").split(",") if d.strip()]
    task["body"] = m.group(2).strip()
    return task


def find(task_id):
    matches = list(TASKS.glob(task_id + "-*.md"))
    return matches[0] if matches else None


def set_status(path, status):
    head, body = FRONT.match(path.read_text(encoding="utf-8")).groups()
    head = re.sub(r"^status:.*$", "status: " + status, head, flags=re.M)
    path.write_text(f"---\n{head}\n---\n{body}", encoding="utf-8")


def toggle(path, index):
    head, body = FRONT.match(path.read_text(encoding="utf-8")).groups()
    seen = -1

    def flip(m):
        nonlocal seen
        seen += 1
        if seen != index:
            return m.group(0)
        return m.group(1) + ("x" if m.group(2) == " " else " ") + m.group(3)

    path.write_text(f"---\n{head}\n---\n{CHECK.sub(flip, body)}", encoding="utf-8")


class Handler(BaseHTTPRequestHandler):
    def reply(self, code, body, ctype="application/json"):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            self.reply(200, PAGE, "text/html")
        elif self.path == "/api/tasks":
            tasks = [t for t in (parse(p) for p in sorted(TASKS.glob("BURN-*.md"))) if t]
            self.reply(200, json.dumps({"statuses": STATUSES, "tasks": tasks}))
        else:
            self.reply(404, '{"error":"not found"}')

    def do_POST(self):
        m = re.match(r"^/api/tasks/(BURN-\d{3})$", self.path)
        path = find(m.group(1)) if m else None
        if not path:
            return self.reply(404, '{"error":"unknown task"}')
        try:
            change = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            if "status" in change:
                if change["status"] not in STATUSES:
                    return self.reply(400, '{"error":"bad status"}')
                set_status(path, change["status"])
            if "toggle" in change:
                toggle(path, int(change["toggle"]))
        except (ValueError, AttributeError, TypeError):
            return self.reply(400, '{"error":"bad request"}')
        self.reply(200, json.dumps(parse(path)))

    def log_message(self, *args):
        pass


PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Burn Calendar Board</title>
<style>
:root{--bg:#f4f2ee;--panel:#e9e6df;--card:#fff;--text:#1f2328;--muted:#667085;--line:#d6d2c9;--accent:#c2410c;
--research:#1d6fa5;--brainstorm:#7c3aed;--decision:#b45309;--build:#15803d;--blocked:#b91c1c}
@media (prefers-color-scheme:dark){:root{--bg:#17181a;--panel:#1f2123;--card:#2a2c2f;--text:#e8e6e1;--muted:#9aa0a8;
--line:#3a3d41;--accent:#fb923c;--research:#60a5fa;--brainstorm:#a78bfa;--decision:#fbbf24;--build:#4ade80;--blocked:#f87171}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
header{padding:16px 20px 12px;border-bottom:1px solid var(--line)}
.epic{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);font-weight:700}
h1{margin:2px 0 8px;font-size:20px}
.progress{display:flex;align-items:center;gap:10px;color:var(--muted);font-size:12px}
.bar{flex:0 0 220px;height:6px;background:var(--line);border-radius:3px;overflow:hidden}
.bar i{display:block;height:100%;background:var(--accent)}
.filters{display:flex;flex-wrap:wrap;gap:6px 16px;margin-top:12px}
.group{display:flex;gap:4px;align-items:center;flex-wrap:wrap}
.group span{color:var(--muted);font-size:12px}
.chip{border:1px solid var(--line);background:transparent;color:var(--text);border-radius:999px;padding:2px 10px;font:inherit;font-size:12px;cursor:pointer}
.chip[aria-pressed=true]{background:var(--text);color:var(--bg);border-color:var(--text)}
main{display:grid;grid-template-columns:repeat(3,minmax(260px,1fr));gap:12px;padding:16px 20px;align-items:start;overflow-x:auto}
.col{background:var(--panel);border-radius:8px;padding:8px;min-height:240px}
.col.over{outline:2px dashed var(--accent)}
.col h2{font-size:12px;text-transform:uppercase;letter-spacing:.06em;margin:4px 6px 8px;color:var(--muted);display:flex;justify-content:space-between}
.card{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--muted);border-radius:6px;padding:8px 10px;margin-bottom:8px;cursor:pointer}
.card:focus-visible{outline:2px solid var(--accent)}
.card.is-blocked{opacity:.62}
.card.research{border-left-color:var(--research)}.card.brainstorm{border-left-color:var(--brainstorm)}
.card.decision{border-left-color:var(--decision)}.card.build{border-left-color:var(--build)}
.id{font-size:11px;color:var(--muted);display:flex;justify-content:space-between}
.title{margin:2px 0 6px;font-weight:600}
.meta{display:flex;flex-wrap:wrap;gap:4px;font-size:11px;color:var(--muted)}
.tag{border:1px solid var(--line);border-radius:4px;padding:0 5px;text-decoration:none;color:inherit}
.tag.blocked{color:var(--blocked);border-color:var(--blocked)}
dialog{border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--text);width:min(720px,94vw);max-height:88vh;padding:0}
dialog::backdrop{background:rgba(0,0,0,.45)}
.dlg{padding:18px 22px 22px}
.dlg h3{margin:2px 0 10px;font-size:18px}
.dlg h4{margin:16px 0 6px;font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}
.dlg ul{padding:0;margin:0;list-style:none}
.dlg li{padding:3px 0;display:flex;gap:8px;align-items:flex-start}
.dlg li.plain{display:list-item;list-style:disc;margin-left:20px}
.dlg code{background:var(--panel);padding:0 4px;border-radius:3px;font-size:12.5px}
.dlg a{color:var(--accent);overflow-wrap:anywhere}
.row{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:8px 0 4px;font-size:13px;color:var(--muted)}
select{font:inherit;background:var(--bg);color:var(--text);border:1px solid var(--line);border-radius:5px;padding:3px 6px}
.close{float:right;border:0;background:none;color:var(--muted);font-size:20px;cursor:pointer}
</style></head><body>
<header><div class="epic">Epic</div><h1>Harmonized Burning Activity Calendar</h1>
<div class="progress"><div class="bar"><i id="bar"></i></div><span id="count"></span></div>
<div class="filters" id="filters"></div></header>
<main id="board"></main>
<dialog id="dlg"><div class="dlg" id="dlgBody"></div></dialog>
<script>
let data={statuses:[],tasks:[]};
const filter={type:null,priority:null,ready:null};
const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const inline=s=>esc(s).replace(/`([^`]+)`/g,"<code>$1</code>").replace(/(https?:\/\/[^\s<]+)/g,'<a href="$1" target="_blank" rel="noopener">$1</a>');
const byId=id=>data.tasks.find(t=>t.id===id);
const blockers=t=>t.depends.filter(d=>{const x=byId(d);return x&&x.status!=="done"});
const RANK={must:0,should:1,stretch:2};

async function load(){data=await(await fetch("/api/tasks")).json();render()}
async function patch(id,change){
  const res=await fetch("/api/tasks/"+id,{method:"POST",body:JSON.stringify(change)});
  if(!res.ok)return;
  data.tasks[data.tasks.findIndex(t=>t.id===id)]=await res.json();render();
}
function chips(label,key,values){
  return `<div class="group"><span>${label}</span>`+values.map(v=>
    `<button class="chip" data-key="${key}" data-val="${v}" aria-pressed="${filter[key]===v}">${v}</button>`).join("")+"</div>";
}
function render(){
  const done=data.tasks.filter(t=>t.status==="done").length;
  $("bar").style.width=(data.tasks.length?100*done/data.tasks.length:0)+"%";
  $("count").textContent=`${done} of ${data.tasks.length} tasks done`;
  $("filters").innerHTML=chips("Type","type",["research","brainstorm","decision","build"])+
    chips("Priority","priority",["must","should","stretch"])+chips("Show","ready",["ready only"]);
  const shown=data.tasks.filter(t=>(!filter.type||t.type===filter.type)&&(!filter.priority||t.priority===filter.priority)&&
    (!filter.ready||t.status!=="todo"||!blockers(t).length));
  $("board").innerHTML=data.statuses.map(s=>{
    const cards=shown.filter(t=>t.status===s).sort((a,b)=>
      (blockers(a).length>0)-(blockers(b).length>0)||RANK[a.priority]-RANK[b.priority]||a.id.localeCompare(b.id));
    return `<section class="col" data-status="${s}"><h2><span>${s}</span><span>${cards.length}</span></h2>`+cards.map(t=>{
      const b=s==="done"?[]:blockers(t);
      const checks=t.body.match(/^- \[[ xX]\]/gm)||[];
      const ticked=checks.filter(c=>c!=="- [ ]").length;
      return `<article class="card ${esc(t.type)} ${b.length?"is-blocked":""}" draggable="true" tabindex="0" data-id="${t.id}">
        <div class="id"><span>${t.id}</span><span>${esc(t.priority||"")}</span></div>
        <div class="title">${esc(t.title)}</div>
        <div class="meta"><span class="tag">${esc(t.type)}</span><span class="tag">criteria ${ticked}/${checks.length}</span>
        ${t.timebox?`<span class="tag">${esc(t.timebox)}</span>`:""}
        ${b.length?`<span class="tag blocked">blocked by ${b.map(x=>x.replace("BURN-","")).join(", ")}</span>`:""}</div></article>`;
    }).join("")+"</section>";
  }).join("");
}
function renderBody(t){
  let html="",inList=false,check=-1;
  for(const line of t.body.split("\n")){
    const item=line.match(/^- (\[([ xX])\] )?(.*)$/);
    if(item){
      if(!inList){html+="<ul>";inList=true}
      if(item[1]){check++;html+=`<li><input type="checkbox" data-check="${check}" ${item[2]!==" "?"checked":""}><span>${inline(item[3])}</span></li>`}
      else html+=`<li class="plain">${inline(item[3])}</li>`;
      continue;
    }
    if(inList){html+="</ul>";inList=false}
    if(line.startsWith("## "))html+=`<h4>${inline(line.slice(3))}</h4>`;
    else if(line.trim())html+=`<p>${inline(line)}</p>`;
  }
  return html+(inList?"</ul>":"");
}
function openTask(id){
  const t=byId(id);if(!t)return;
  $("dlgBody").innerHTML=`<button class="close" aria-label="Close" data-close>&times;</button>
    <div class="epic">${t.id} · ${esc(t.type)} · ${esc(t.priority||"")}${t.timebox?" · "+esc(t.timebox):""}</div><h3>${esc(t.title)}</h3>
    <div class="row"><label>Status <select id="fStatus">${data.statuses.map(s=>`<option ${s===t.status?"selected":""}>${s}</option>`).join("")}</select></label>
    ${t.depends.length?`<span class="meta">Depends on ${t.depends.map(d=>{const x=byId(d);
      return `<a href="#" data-open="${d}" class="tag ${x&&x.status!=="done"?"blocked":""}">${d}${x?" · "+x.status:""}</a>`}).join(" ")}</span>`:""}</div>
    <div class="row">${esc(t.requirement||"")}</div>${renderBody(t)}`;
  $("dlg").dataset.id=id;
  if(!$("dlg").open)$("dlg").showModal();
}
document.addEventListener("click",e=>{
  const chip=e.target.closest(".chip");
  if(chip){const{key,val}=chip.dataset;filter[key]=filter[key]===val?null:val;return render()}
  if(e.target.closest("[data-close]")||e.target===$("dlg"))return $("dlg").close();
  const link=e.target.closest("[data-open]");
  if(link){e.preventDefault();return openTask(link.dataset.open)}
  const card=e.target.closest(".card");
  if(card)openTask(card.dataset.id);
});
document.addEventListener("keydown",e=>{if(e.key==="Enter"&&e.target.classList.contains("card"))openTask(e.target.dataset.id)});
document.addEventListener("change",async e=>{
  const id=$("dlg").dataset.id;
  if(e.target.id==="fStatus")await patch(id,{status:e.target.value});
  else if(e.target.dataset.check!==undefined)await patch(id,{toggle:Number(e.target.dataset.check)});
  else return;
  openTask(id);
});
document.addEventListener("dragstart",e=>{const c=e.target.closest(".card");if(c)e.dataTransfer.setData("text/plain",c.dataset.id)});
document.addEventListener("dragover",e=>{const c=e.target.closest(".col");if(c){e.preventDefault();c.classList.add("over")}});
document.addEventListener("dragleave",e=>{const c=e.target.closest(".col");if(c&&!c.contains(e.relatedTarget))c.classList.remove("over")});
document.addEventListener("drop",e=>{const c=e.target.closest(".col");if(!c)return;e.preventDefault();c.classList.remove("over");
  patch(e.dataTransfer.getData("text/plain"),{status:c.dataset.status})});
window.addEventListener("focus",()=>{if(!$("dlg").open)load()});
load();
</script></body></html>
"""

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print(f"Board running at http://127.0.0.1:{port}  (Ctrl+C to stop)")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
