from pathlib import Path
import re

p=Path('public/ballard-locks/tour/index.html')
s=p.read_text()

# 1) Turn the AIS widget into the full map underlay and keep Fish/Camera in the interactive dock.
old_map='''<div class="map-layout"><div class="map-wrap"><div id="tour-map" class="map" role="application" aria-label="Interactive map of Ballard Locks tour stops"></div><div class="map-live-dock" id="map-live-dock" aria-label="Live Ballard data on the tour map"><div class="map-live-tabs"><button class="map-live-tab" data-live-panel="fish" type="button">Fish</button><button class="map-live-tab is-on" data-live-panel="ais" type="button"><span class="live-map-dot"></span>AIS ships</button><button class="map-live-tab" data-live-panel="camera" type="button">Camera</button><button class="map-live-toggle" id="map-live-toggle" type="button" aria-expanded="true">Hide</button></div><div class="map-live-body"><section class="map-live-panel" id="map-live-panel-fish" hidden><div class="map-live-title">Latest published WDFW Ballard Locks counts</div><div class="map-fish-grid" id="map-fish-grid"><div class="map-live-note">Loading Sockeye, Chinook and Coho counts…</div></div><div class="map-live-note" id="map-fish-note">Counts are preliminary; the source date is shown.</div></section><section class="map-live-panel" id="map-live-panel-ais"><div class="map-live-frame"><iframe id="tour-ais-map" title="Live AIS vessel traffic at Ballard Locks" loading="eager" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen src="https://embed.myshiptracking.com/embed?myst&amp;zoom=15&amp;lat=47.66556&amp;lng=-122.39722&amp;show_names=1&amp;scroll_wheel=0&amp;show_menu=0&amp;map_style=simple&amp;ref=https%3A%2F%2Fchrisizworski.com%2Fballard-locks%2Ftour%2F"></iframe></div><div class="map-live-note">Live AIS around Salmon Bay and the lock approaches. Small recreational boats without AIS will not appear.</div></section><section class="map-live-panel" id="map-live-panel-camera" hidden><div class="map-live-frame"><iframe title="Live Ballard Ship Canal Camera 3" loading="lazy" allowfullscreen src="https://g1.ipcamlive.com/player/player.php?alias=5ababb8154afe"></iframe></div><div class="map-live-note">Live Salmon Bay Marine Center Camera #3, upstream of the Ballard Locks.</div></section></div></div><div class="fallback"><strong>Interactive map unavailable.</strong><p>The stop list remains available. Reload the page to try the map again.</p></div><div class="map-legend"><span><i class="dot core"></i>Locks</span><span><i class="dot nature"></i>Nature</span><span><i class="dot story"></i>History &amp; art</span></div></div>'''
new_map='''<div class="map-layout"><div class="map-wrap"><iframe id="tour-ais-underlay" class="ais-underlay" title="Live AIS vessel traffic at Ballard Locks" loading="eager" referrerpolicy="strict-origin-when-cross-origin" src="https://embed.myshiptracking.com/embed?myst&amp;zoom=16&amp;lat=47.66555&amp;lng=-122.39720&amp;show_names=1&amp;scroll_wheel=0&amp;show_menu=0&amp;map_style=simple&amp;ref=https%3A%2F%2Fchrisizworski.com%2Fballard-locks%2Ftour%2F"></iframe><div id="tour-map" class="map map-overlay" role="application" aria-label="Ballard Locks walking routes over live AIS vessel traffic"></div><div class="map-live-dock is-collapsed" id="map-live-dock" aria-label="Fish and camera information on the tour map"><div class="map-live-tabs"><button class="map-live-tab" data-live-panel="fish" type="button">Fish</button><button class="map-live-tab" data-live-panel="camera" type="button">Camera</button><button class="map-live-toggle" id="map-live-toggle" type="button" aria-expanded="false">Show</button></div><div class="map-live-body"><section class="map-live-panel" id="map-live-panel-fish"><div class="map-live-title">Latest published WDFW Ballard Locks counts</div><div class="map-fish-grid" id="map-fish-grid"><div class="map-live-note">Loading Sockeye, Chinook and Coho counts…</div></div><div class="map-live-note" id="map-fish-note">Counts are preliminary; the source date is shown.</div></section><section class="map-live-panel" id="map-live-panel-camera" hidden><div class="map-live-frame"><iframe title="Live Ballard Ship Canal Camera 3" loading="lazy" allowfullscreen src="https://g1.ipcamlive.com/player/player.php?alias=5ababb8154afe"></iframe></div><div class="map-live-note">Live Salmon Bay Marine Center Camera #3, upstream of the Ballard Locks.</div></section></div></div><div class="fallback"><strong>Interactive route overlay unavailable.</strong><p>The live AIS map and stop list remain available. Reload the page to try the route overlay again.</p></div><div class="map-legend"><span><i class="dot ais"></i>Live AIS vessels</span><span><i class="dot core"></i>Locks</span><span><i class="dot nature"></i>Nature</span><span><i class="dot story"></i>History &amp; art</span></div></div>'''
if old_map not in s:
    raise SystemExit('map dock block not found')
s=s.replace(old_map,new_map,1)

# 2) CSS: AIS fills the geographic surface; MapLibre is a transparent, non-moving overlay.
old_css='.map{position:absolute;inset:0}.map-live-dock{'
new_css='.ais-underlay{position:absolute;inset:0;width:100%;height:100%;border:0;z-index:1;background:#dbe4df;pointer-events:none}.map{position:absolute;inset:0;z-index:2;background:transparent;pointer-events:none}.map .maplibregl-canvas{background:transparent!important;pointer-events:none}.map .maplibregl-marker,.map .maplibregl-popup,.map .maplibregl-popup-close-button{pointer-events:auto}.map-live-dock{'
if old_css not in s:
    raise SystemExit('map CSS anchor not found')
s=s.replace(old_css,new_css,1)
s=s.replace('.dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:5px}.dot.core{', '.dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:5px}.dot.ais{background:#45b886;box-shadow:0 0 0 3px rgba(69,184,134,.16)}.dot.core{',1)

# 3) Source note now reflects the actual combined map.
s=s.replace('Map base: OpenFreeMap / OpenStreetMap. Route lines are simplified orientation paths.', 'Live vessel layer: MyShipTracking AIS. Ballard walking routes and stops are aligned above it. Route lines are simplified orientation paths.',1)

# 4) Route views are explicit so AIS and route layers move together.
anchor="let current='essential',map,markers=new Map(),liveData=null,userMarker=null,activePopup=null;\n"
insert="""let current='essential',map,markers=new Map(),liveData=null,userMarker=null,activePopup=null;
const routeViews={
  essential:{center:[-122.39720,47.66555],zoom:16},
  full:{center:[-122.39820,47.66575],zoom:16},
  extended:{center:[-122.39640,47.66640],zoom:15}
};
"""
if anchor not in s:
    raise SystemExit('state anchor not found')
s=s.replace(anchor,insert,1)

# 5) Only Fish and Camera are dock panels now.
s=s.replace("for(const name of ['fish','ais','camera'])", "for(const name of ['fish','camera'])",1)

# 6) Stop selection no longer changes geographic view independently of AIS.
old_select="function selectStop(id,fly=true){document.querySelectorAll('.stop-card').forEach(x=>x.classList.toggle('is-on',x.dataset.id===id));const s=stops.find(x=>x.id===id);if(!s)return;if(map&&fly){map.flyTo({center:[s.lng,s.lat],zoom:id==='nordic'?16.3:17.2,essential:true});markers.get(id)?.togglePopup()}}"
new_select="function selectStop(id,fly=true){document.querySelectorAll('.stop-card').forEach(x=>x.classList.toggle('is-on',x.dataset.id===id));const s=stops.find(x=>x.id===id);if(!s)return;if(map&&fly)markers.get(id)?.togglePopup()}"
if old_select not in s:
    raise SystemExit('selectStop anchor not found')
s=s.replace(old_select,new_select,1)

# 7) Keep both maps synchronized whenever the user switches route presets.
old_setroute="function setRoute(key){current=key;document.querySelectorAll('.route-btn').forEach(b=>b.classList.toggle('is-on',b.dataset.route===key));renderList();if(map?.getSource('route'))map.getSource('route').setData(routeFeatures(key));if(map){const coords=routes[key].ids.map(id=>{const s=stops.find(x=>x.id===id);return [s.lng,s.lat]});const bounds=coords.reduce((b,c)=>b.extend(c),new maplibregl.LngLatBounds(coords[0],coords[0]));map.fitBounds(bounds,{padding:{top:70,bottom:70,left:60,right:60},maxZoom:17,duration:700})}}"
new_setroute="function aisSrcFor(key){const v=routeViews[key]||routeViews.essential;return `https://embed.myshiptracking.com/embed?myst&zoom=${v.zoom}&lat=${v.center[1].toFixed(5)}&lng=${v.center[0].toFixed(5)}&show_names=1&scroll_wheel=0&show_menu=0&map_style=simple&ref=https%3A%2F%2Fchrisizworski.com%2Fballard-locks%2Ftour%2F`}\nfunction setAisView(key){const frame=$('tour-ais-underlay');const next=aisSrcFor(key);if(frame&&frame.src!==next)frame.src=next}\nfunction setRoute(key){current=key;document.querySelectorAll('.route-btn').forEach(b=>b.classList.toggle('is-on',b.dataset.route===key));renderList();if(map?.getSource('route'))map.getSource('route').setData(routeFeatures(key));const v=routeViews[key]||routeViews.essential;if(map)map.jumpTo({center:v.center,zoom:v.zoom});setAisView(key)}"
if old_setroute not in s:
    raise SystemExit('setRoute anchor not found')
s=s.replace(old_setroute,new_setroute,1)

# 8) MapLibre becomes a transparent overlay only; no independent navigation controls.
old_init="function initMap(){try{map=new maplibregl.Map({container:'tour-map',style:'https://tiles.openfreemap.org/styles/liberty',center:[-122.3973,47.6658],zoom:16.6,attributionControl:true});map.addControl(new maplibregl.NavigationControl({showCompass:false}),'top-right');map.on('load',()=>{"
new_init="function initMap(){try{const v=routeViews[current];map=new maplibregl.Map({container:'tour-map',style:{version:8,sources:{},layers:[]},center:v.center,zoom:v.zoom,interactive:false,attributionControl:false});map.on('load',()=>{"
if old_init not in s:
    raise SystemExit('initMap anchor not found')
s=s.replace(old_init,new_init,1)

# 9) Geolocation adds an aligned marker but never recenters only one layer.
old_loc="const d=Math.hypot((here[0]+122.3972)*54,(here[1]-47.6656)*69);if(d<3)map.fitBounds(new maplibregl.LngLatBounds(here,[-122.3972,47.6656]),{padding:80,maxZoom:17});else map.flyTo({center:[-122.3972,47.6656],zoom:16.3});$('locate').textContent=d<3?'You are on the map':'Show Locks';"
new_loc="const d=Math.hypot((here[0]+122.3972)*54,(here[1]-47.6656)*69);$('locate').textContent=d<1?'You are on the map':'Location added';"
if old_loc not in s:
    raise SystemExit('locate recenter anchor not found')
s=s.replace(old_loc,new_loc,1)

# 10) Tests: update the contract to the combined AIS + route map.
t=Path('tests/ballard-tour.test.js')
ts=t.read_text()
ts=ts.replace("  assert.ok(tour.includes('https://tiles.openfreemap.org/styles/liberty'));\n", "  assert.ok(tour.includes('id=\"tour-ais-underlay\"'));\n  assert.ok(tour.includes('style:{version:8,sources:{},layers:[]}'));\n")
old_test="""test('tour puts fish AIS and the live camera directly on the map',()=>{
  assert.ok(!tour.includes('What this map adds'));
  assert.ok(tour.includes('id=\"map-live-dock\"'));
  assert.ok(tour.includes('data-live-panel=\"fish\"'));
  assert.ok(tour.includes('data-live-panel=\"ais\"'));
  assert.ok(tour.includes('data-live-panel=\"camera\"'));
  assert.ok(tour.includes('https://embed.myshiptracking.com/embed?myst'));
  assert.ok(tour.includes('https://g1.ipcamlive.com/player/player.php?alias=5ababb8154afe'));
  for(const species of ['Sockeye','Chinook','Coho']) assert.ok(tour.includes(species));
  assert.ok(tour.includes('latest published daily counts, not a live fish counter'));
  assert.ok(!tour.includes(\"function setRoute(key){current=key;document.querySelectorAll('.map-live-tab')\"));
  assert.equal((tour.match(/map-live-tab'\\)\\.forEach\\(b=>b\\.addEventListener/g)||[]).length,1);
});
"""
new_test="""test('tour combines AIS vessels with walking routes while Fish and Camera stay in the bar',()=>{
  assert.ok(!tour.includes('What this map adds'));
  assert.ok(tour.includes('id=\"tour-ais-underlay\"'));
  assert.ok(tour.includes('id=\"tour-map\" class=\"map map-overlay\"'));
  assert.ok(tour.indexOf('id=\"tour-ais-underlay\"') < tour.indexOf('id=\"tour-map\"'));
  assert.ok(tour.includes('data-live-panel=\"fish\"'));
  assert.ok(tour.includes('data-live-panel=\"camera\"'));
  assert.ok(!tour.includes('data-live-panel=\"ais\"'));
  assert.ok(!tour.includes('id=\"map-live-panel-ais\"'));
  assert.ok(tour.includes('https://embed.myshiptracking.com/embed?myst'));
  assert.ok(tour.includes('https://g1.ipcamlive.com/player/player.php?alias=5ababb8154afe'));
  assert.ok(tour.includes('const routeViews='));
  assert.ok(tour.includes('function setAisView(key)'));
  assert.ok(tour.includes("map.jumpTo({center:v.center,zoom:v.zoom})"));
  assert.ok(!tour.includes('map.fitBounds(bounds'));
  assert.ok(!tour.includes("map.flyTo({center:[s.lng,s.lat]"));
  assert.ok(tour.includes('pointer-events:none'));
  for(const species of ['Sockeye','Chinook','Coho']) assert.ok(tour.includes(species));
  assert.ok(tour.includes('latest published daily counts, not a live fish counter'));
  assert.equal((tour.match(/map-live-tab'\\)\\.forEach\\(b=>b\\.addEventListener/g)||[]).length,1);
});
"""
if old_test not in ts:
    raise SystemExit('old AIS tour test not found')
ts=ts.replace(old_test,new_test,1)
t.write_text(ts)

p.write_text(s)
