from pathlib import Path

p=Path('public/ballard-locks/tour/index.html')
s=p.read_text()

old='<div class="map-layout"><div class="map-wrap"><iframe id="tour-ais-underlay" class="ais-underlay" title="Live AIS vessel traffic at Ballard Locks"'
new='<div class="map-layout"><div class="map-wrap"><div class="ais-clip"><iframe id="tour-ais-underlay" class="ais-underlay" title="Live AIS vessel traffic at Ballard Locks"'
if old not in s: raise SystemExit('map iframe open anchor missing')
s=s.replace(old,new,1)
old='ref=https%3A%2F%2Fchrisizworski.com%2Fballard-locks%2Ftour%2F"></iframe><div class="ais-live-status"'
new='ref=https%3A%2F%2Fchrisizworski.com%2Fballard-locks%2Ftour%2F"></iframe></div><div class="ais-live-status"'
if old not in s: raise SystemExit('map iframe close anchor missing')
s=s.replace(old,new,1)

repls={
'.map-wrap{position:relative;min-height:650px;background:#dbe4df}':'.map-wrap{position:relative;min-height:650px;background:#dbe4df;isolation:isolate}',
'.ais-underlay{position:absolute;inset:0;width:100%;height:100%;border:0;z-index:1;background:#dbe4df;pointer-events:none}':'.ais-clip{position:absolute;inset:0;z-index:1;overflow:hidden;background:#dbe4df}.ais-underlay{position:absolute;left:-42px;top:0;width:calc(100% + 84px);height:100%;border:0;background:#dbe4df;pointer-events:none}',
'.map{position:absolute;inset:0;z-index:2;background:transparent;pointer-events:none}':'.map{position:absolute;inset:0;z-index:2;background:transparent;pointer-events:auto}',
'.map .maplibregl-canvas{background:transparent!important;pointer-events:none}':'.map .maplibregl-canvas{background:transparent!important;pointer-events:auto;cursor:grab}.map .maplibregl-canvas:active{cursor:grabbing}',
'.maplibregl-popup-content{font-family:Arial,sans-serif;border-radius:12px!important;padding:0!important;overflow:hidden;min-width:230px;box-shadow:0 8px 30px rgba(0,0,0,.18)!important}':'.maplibregl-popup{z-index:20!important}.maplibregl-popup-content{font-family:Arial,sans-serif;border-radius:12px!important;padding:0!important;overflow:hidden;min-width:230px;max-width:min(300px,calc(100vw - 56px));box-shadow:0 8px 30px rgba(0,0,0,.18)!important}'
}
for a,b in repls.items():
    if a not in s: raise SystemExit(f'CSS anchor missing: {a[:50]}')
    s=s.replace(a,b,1)

old="function aisSrcFor(key){const v=routeViews[key]||routeViews.essential;return `https://embed.myshiptracking.com/embed?myst&zoom=${v.zoom}&lat=${v.center[1].toFixed(5)}&lng=${v.center[0].toFixed(5)}&show_names=1&scroll_wheel=0&show_menu=0&map_style=simple&ref=https%3A%2F%2Fchrisizworski.com%2Fballard-locks%2Ftour%2F`}\nfunction setAisView(key){const frame=$('tour-ais-underlay');const next=aisSrcFor(key);if(frame&&frame.src!==next)frame.src=next}"
new="function aisSrcForView(center,zoom){return `https://embed.myshiptracking.com/embed?myst&zoom=${Math.max(3,Math.min(18,Math.round(zoom)))}&lat=${center[1].toFixed(5)}&lng=${center[0].toFixed(5)}&show_names=1&scroll_wheel=0&show_menu=0&map_style=simple&ref=https%3A%2F%2Fchrisizworski.com%2Fballard-locks%2Ftour%2F`}\nfunction aisSrcFor(key){const v=routeViews[key]||routeViews.essential;return aisSrcForView(v.center,v.zoom)}\nfunction setAisView(key){const frame=$('tour-ais-underlay');const next=aisSrcFor(key);if(frame&&frame.src!==next)frame.src=next}\nfunction syncAisToMap(){if(!map)return;const c=map.getCenter();const frame=$('tour-ais-underlay');const next=aisSrcForView([c.lng,c.lat],map.getZoom());if(frame&&frame.src!==next)frame.src=next}"
if old not in s: raise SystemExit('AIS functions anchor missing')
s=s.replace(old,new,1)

old="map=new maplibregl.Map({container:'tour-map',style:{version:8,sources:{},layers:[]},center:v.center,zoom:v.zoom,interactive:false,attributionControl:false});"
new="map=new maplibregl.Map({container:'tour-map',style:{version:8,sources:{},layers:[]},center:v.center,zoom:v.zoom,interactive:true,attributionControl:false});map.on('moveend',syncAisToMap);"
if old not in s: raise SystemExit('MapLibre init anchor missing')
s=s.replace(old,new,1)

old="const popup=new maplibregl.Popup({offset:25,maxWidth:'320px'}).setHTML(popupHtml(s));popup.on('open',()=>{if(activePopup&&activePopup!==popup)activePopup.remove();activePopup=popup});"
new="const popup=new maplibregl.Popup({offset:25,maxWidth:'300px',closeOnClick:false,focusAfterOpen:false}).setHTML(popupHtml(s));popup.on('open',()=>{if(activePopup&&activePopup!==popup)activePopup.remove();activePopup=popup;const dock=$('map-live-dock');if(dock&&!dock.classList.contains('is-collapsed'))dock.classList.add('is-collapsed');if(map){const rect=$('tour-map').getBoundingClientRect();const pt=map.project([s.lng,s.lat]);const shiftX=pt.x>rect.width*.68?-Math.min(150,rect.width*.18):pt.x<rect.width*.22?Math.min(120,rect.width*.14):0;const shiftY=pt.y<150?100:pt.y>rect.height-120?-90:0;if(shiftX||shiftY)map.panBy([shiftX,shiftY],{duration:260})}});"
if old not in s: raise SystemExit('popup anchor missing')
s=s.replace(old,new,1)

p.write_text(s)

t=Path('tests/ballard-tour.test.js')
ts=t.read_text()
old="  assert.ok(tour.includes('function setAisView(key)'));\n  assert.ok(tour.includes(\"map.jumpTo({center:v.center,zoom:v.zoom})\"));\n"
new="  assert.ok(tour.includes('function setAisView(key)'));\n  assert.ok(tour.includes('function syncAisToMap()'));\n  assert.ok(tour.includes(\"map.on('moveend',syncAisToMap)\"));\n  assert.ok(tour.includes('interactive:true'));\n  assert.ok(tour.includes('class=\"ais-clip\"'));\n  assert.ok(tour.includes('left:-42px'));\n  assert.ok(tour.includes('width:calc(100% + 84px)'));\n  assert.ok(tour.includes(\"map.jumpTo({center:v.center,zoom:v.zoom})\"));\n"
if old not in ts: raise SystemExit('test anchor missing')
ts=ts.replace(old,new,1)
old="  assert.ok(tour.includes('pointer-events:none'));\n"
new="  assert.ok(tour.includes('pointer-events:auto'));\n  assert.ok(tour.includes(\"closeOnClick:false\"));\n  assert.ok(tour.includes(\"map.panBy([shiftX,shiftY]\"));\n"
if old not in ts: raise SystemExit('pointer test anchor missing')
ts=ts.replace(old,new,1)
t.write_text(ts)
