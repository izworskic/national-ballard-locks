from pathlib import Path

p=Path('public/ballard-locks/tour/index.html')
s=p.read_text()

css_anchor='.dot.ais{background:#45b886;box-shadow:0 0 0 3px rgba(69,184,134,.16)}'
css_add='.ais-live-status{position:absolute;left:12px;top:12px;z-index:5;display:inline-flex;align-items:center;gap:7px;background:rgba(16,47,57,.92);color:#eef8f7;border:1px solid rgba(255,255,255,.24);border-radius:999px;padding:8px 11px;box-shadow:0 5px 16px rgba(0,0,0,.16);font:800 .66rem Arial,sans-serif;letter-spacing:.03em;text-transform:uppercase}.ais-live-status .pulse{width:8px;height:8px;border-radius:50%;background:#45b886;box-shadow:0 0 0 4px rgba(69,184,134,.18)}'
if css_add not in s:
    if css_anchor not in s: raise SystemExit('AIS CSS anchor missing')
    s=s.replace(css_anchor,css_anchor+css_add,1)

map_anchor='<iframe id="tour-ais-underlay" class="ais-underlay" title="Live AIS vessel traffic at Ballard Locks"'
status='<div class="ais-live-status" aria-label="Live AIS positions update automatically"><span class="pulse" aria-hidden="true"></span>LIVE AIS · positions update automatically</div>'
if status not in s:
    idx=s.find(map_anchor)
    if idx<0: raise SystemExit('AIS iframe anchor missing')
    end=s.find('</iframe>',idx)
    if end<0: raise SystemExit('AIS iframe close missing')
    end += len('</iframe>')
    s=s[:end]+status+s[end:]

p.write_text(s)

t=Path('tests/ballard-tour.test.js')
ts=t.read_text()
anchor="  assert.ok(tour.includes('https://embed.myshiptracking.com/embed?myst'));\n"
check="  assert.ok(tour.includes('LIVE AIS · positions update automatically'));\n"
if check not in ts:
    if anchor not in ts: raise SystemExit('test AIS anchor missing')
    ts=ts.replace(anchor,anchor+check,1)
t.write_text(ts)
