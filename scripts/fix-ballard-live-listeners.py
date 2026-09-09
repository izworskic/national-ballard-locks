from pathlib import Path

p=Path('public/ballard-locks/tour/index.html')
s=p.read_text()

misplaced="function setRoute(key){current=key;document.querySelectorAll('.map-live-tab').forEach(b=>b.addEventListener('click',()=>setLivePanel(b.dataset.livePanel)));$('map-live-toggle').addEventListener('click',()=>{const dock=$('map-live-dock');const collapsed=dock.classList.toggle('is-collapsed');$('map-live-toggle').textContent=collapsed?'Show':'Hide';$('map-live-toggle').setAttribute('aria-expanded',String(!collapsed))});\ndocument.querySelectorAll('.route-btn').forEach"
fixed="function setRoute(key){current=key;document.querySelectorAll('.route-btn').forEach"
if misplaced not in s:
    raise SystemExit('misplaced live listeners not found')
s=s.replace(misplaced,fixed,1)

bottom="document.querySelectorAll('.route-btn').forEach(b=>b.addEventListener('click',()=>{setRoute(b.dataset.route);gtag?.('event','tour_route_change',{route:b.dataset.route})}));"
live="document.querySelectorAll('.map-live-tab').forEach(b=>b.addEventListener('click',()=>setLivePanel(b.dataset.livePanel)));$('map-live-toggle').addEventListener('click',()=>{const dock=$('map-live-dock');const collapsed=dock.classList.toggle('is-collapsed');$('map-live-toggle').textContent=collapsed?'Show':'Hide';$('map-live-toggle').setAttribute('aria-expanded',String(!collapsed))});\n"
if bottom not in s:
    raise SystemExit('bottom route listener anchor not found')
s=s.replace(bottom,live+bottom,1)

# Remove dead CSS for the explainer block that was removed from the page.
for dead in [
    ".quick-facts{background:#eaf2ef;border:1px solid #cadbd5;border-radius:14px;padding:18px}",
    ".quick-facts strong{display:block;font:800 .78rem Arial,sans-serif;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px}",
    ".quick-facts ul{margin:0;padding-left:19px;font-size:.9rem}",
    ".quick-facts{margin-top:14px}",
]:
    s=s.replace(dead,'')

p.write_text(s)

# Add a regression assertion for handler placement.
t=Path('tests/ballard-tour.test.js')
ts=t.read_text()
needle="  assert.ok(tour.includes('latest published daily counts, not a live fish counter'));\n"
extra="  assert.ok(!tour.includes(\"function setRoute(key){current=key;document.querySelectorAll('.map-live-tab')\"));\n  assert.equal((tour.match(/map-live-tab'\\)\\.forEach\\(b=>b\\.addEventListener/g)||[]).length,1);\n"
if extra.strip() not in ts:
    if needle not in ts:
        raise SystemExit('tour live test anchor missing')
    ts=ts.replace(needle,needle+extra,1)
    t.write_text(ts)
