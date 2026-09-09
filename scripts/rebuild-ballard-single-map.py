from pathlib import Path
import re

p=Path('public/ballard-locks/tour/index.html')
s=p.read_text()

# Remove the separate cross-origin AIS iframe entirely.
s, n = re.subn(r'<div class="ais-clip"><iframe id="tour-ais-underlay"[\s\S]*?</iframe></div>', '', s, count=1)
if n != 1:
    raise SystemExit('AIS iframe wrapper not found')

# Replace composite-map CSS with one real MapLibre surface.
s, n = re.subn(r'\.ais-clip\{[^}]*\}\.ais-underlay\{[^}]*\}', '', s, count=1)
if n != 1:
    raise SystemExit('AIS clip CSS not found')
s=s.replace('.map{position:absolute;inset:0;z-index:2;background:transparent;pointer-events:auto}', '.map{position:absolute;inset:0;z-index:2;background:#dbe4df;pointer-events:auto}', 1)
s=s.replace('.map .maplibregl-canvas{background:transparent!important;pointer-events:auto;cursor:grab}.map .maplibregl-canvas:active{cursor:grabbing}', '.map .maplibregl-canvas{pointer-events:auto;cursor:grab}.map .maplibregl-canvas:active{cursor:grabbing}', 1)

# Update source disclosure and fallback wording.
s=s.replace('Live vessel layer: MyShipTracking AIS. Ballard walking routes and stops are aligned above it.', 'Live vessel layer: Open Waters AIS. Ships, walking routes and stops share the same MapLibre map.', 1)
s=s.replace('The live AIS map and stop list remain available. Reload the page to try the route overlay again.', 'The stop list and live Ballard data remain available. Reload the page to try the interactive map again.', 1)

# Replace old iframe-sync functions with live GeoJSON loading on the same map.
start=s.find('function aisSrcForView(')
end=s.find('function setRoute(key)', start)
if start < 0 or end < 0:
    raise SystemExit('old AIS sync functions not found')
new_funcs="""function emptyAis(){return {type:'FeatureCollection',features:[]}}
function vesselPopupHtml(p){const name=escapeHtml(p?.name||'AIS vessel');const mmsi=escapeHtml(p?.mmsi||'—');const sog=Number.isFinite(Number(p?.sog))?`${Number(p.sog).toFixed(1)} kn`:'speed unavailable';const cog=Number.isFinite(Number(p?.cog))?`${Math.round(Number(p.cog))}°`:'course unavailable';return `<div class=\"pop\"><div class=\"pop-kicker\">Live AIS vessel</div><h3>${name}</h3><p>MMSI ${mmsi} · ${sog} · ${cog}</p><div class=\"pop-live\">Open Waters AIS · positions refresh automatically</div></div>`}
async function loadAis(){const status=document.querySelector('.ais-live-status');try{const r=await fetch(`/api/ballard-ais?ts=${Date.now()}`,{headers:{accept:'application/json'}});const data=await r.json();if(!r.ok||!data?.ok||data?.featureCollection?.type!=='FeatureCollection')throw new Error(data?.error||`HTTP ${r.status}`);const source=map?.getSource('ais-vessels');if(source)source.setData(data.featureCollection);if(status)status.innerHTML=`<span class=\"pulse\" aria-hidden=\"true\"></span>LIVE AIS · ${Number(data.count||0).toLocaleString()} vessel${Number(data.count||0)===1?'':'s'} · updates automatically`;return data}catch(e){if(status)status.innerHTML='<span class=\"pulse\" aria-hidden=\"true\"></span>LIVE AIS · temporarily unavailable';return null}}
function startAis(){loadAis();setInterval(loadAis,15000);document.addEventListener('visibilitychange',()=>{if(!document.hidden)loadAis()})}
"""
s=s[:start]+new_funcs+s[end:]

# Route changes now move one map; no second map to synchronize.
s=s.replace("map.jumpTo({center:v.center,zoom:v.zoom});setAisView(key)", "map.jumpTo({center:v.center,zoom:v.zoom})", 1)

# Replace empty transparent MapLibre style with OpenFreeMap and remove iframe move-sync listener.
s=s.replace("map=new maplibregl.Map({container:'tour-map',style:{version:8,sources:{},layers:[]},center:v.center,zoom:v.zoom,interactive:true,attributionControl:false});map.on('moveend',syncAisToMap);", "map=new maplibregl.Map({container:'tour-map',style:'https://tiles.openfreemap.org/styles/liberty',center:v.center,zoom:v.zoom,interactive:true,attributionControl:true});", 1)

# Insert the live AIS GeoJSON source/layers into the same map before stop markers.
anchor="map.addLayer({id:'route-line',type:'line',source:'route',paint:{'line-color':'#125c68','line-width':4,'line-opacity':.9,'line-dasharray':[1.2,1.1]}});stops.forEach"
insert="""map.addLayer({id:'route-line',type:'line',source:'route',paint:{'line-color':'#125c68','line-width':4,'line-opacity':.9,'line-dasharray':[1.2,1.1]}});map.addSource('ais-vessels',{type:'geojson',data:emptyAis()});map.addLayer({id:'ais-vessels-halo',type:'circle',source:'ais-vessels',paint:{'circle-radius':8,'circle-color':'#ffffff','circle-opacity':.92}});map.addLayer({id:'ais-vessels',type:'circle',source:'ais-vessels',paint:{'circle-radius':5.5,'circle-color':'#0b7180','circle-stroke-color':'#0b3942','circle-stroke-width':1.2}});map.addLayer({id:'ais-vessel-labels',type:'symbol',source:'ais-vessels',minzoom:14,layout:{'text-field':['coalesce',['get','name'],''],'text-size':10,'text-offset':[0,1.2],'text-anchor':'top','text-allow-overlap':false},paint:{'text-color':'#123744','text-halo-color':'#ffffff','text-halo-width':1.5}});map.on('click','ais-vessels',e=>{const f=e.features?.[0];if(!f)return;new maplibregl.Popup({offset:10,maxWidth:'280px'}).setLngLat(f.geometry.coordinates).setHTML(vesselPopupHtml(f.properties||{})).addTo(map);gtag?.('event','tour_ais_vessel_open',{mmsi:f.properties?.mmsi||''})});map.on('mouseenter','ais-vessels',()=>{map.getCanvas().style.cursor='pointer'});map.on('mouseleave','ais-vessels',()=>{map.getCanvas().style.cursor='grab'});stops.forEach"""
if anchor not in s:
    raise SystemExit('route layer anchor not found')
s=s.replace(anchor,insert,1)

# Start AIS only after the map is ready.
s=s.replace('stops.forEach((s,i)=>{', 'stops.forEach((s,i)=>{', 1)
s=s.replace('markers.set(s.id,marker)});setRoute(current)});', 'markers.set(s.id,marker)});setRoute(current);startAis()});', 1)

p.write_text(s)

# Replace the tour regression tests with single-map expectations.
t=Path('tests/ballard-tour.test.js')
ts=t.read_text()
ts=ts.replace("  assert.ok(tour.includes('id=\"tour-ais-underlay\"'));\n  assert.ok(tour.includes('style:{version:8,sources:{},layers:[]}'));", "  assert.ok(!tour.includes('id=\"tour-ais-underlay\"'));\n  assert.ok(tour.includes('https://tiles.openfreemap.org/styles/liberty'));\n  assert.ok(tour.includes('/api/ballard-ais'));", 1)
start=ts.find("test('tour combines AIS vessels with walking routes while Fish and Camera stay in the bar'")
if start < 0:
    raise SystemExit('tour combined AIS test start missing')
replacement="""test('tour renders AIS vessels, walking routes and stops in one MapLibre map',()=>{
  assert.ok(!tour.includes('What this map adds'));
  assert.ok(!tour.includes('id=\"tour-ais-underlay\"'));
  assert.ok(!tour.includes('embed.myshiptracking.com'));
  assert.ok(!tour.includes('syncAisToMap'));
  assert.ok(tour.includes('id=\"tour-map\" class=\"map map-overlay\"'));
  assert.ok(tour.includes('https://tiles.openfreemap.org/styles/liberty'));
  assert.ok(tour.includes("map.addSource('ais-vessels'"));
  assert.ok(tour.includes("id:'ais-vessels'"));
  assert.ok(tour.includes('/api/ballard-ais'));
  assert.ok(tour.includes('setInterval(loadAis,15000)'));
  assert.ok(tour.includes('LIVE AIS'));
  assert.ok(tour.includes('data-live-panel=\"fish\"'));
  assert.ok(tour.includes('data-live-panel=\"camera\"'));
  assert.ok(!tour.includes('data-live-panel=\"ais\"'));
  assert.ok(tour.includes('https://g1.ipcamlive.com/player/player.php?alias=5ababb8154afe'));
  assert.ok(tour.includes("map.jumpTo({center:v.center,zoom:v.zoom})"));
  assert.ok(tour.includes('interactive:true'));
  assert.ok(tour.includes("closeOnClick:false"));
  assert.ok(tour.includes("map.panBy([shiftX,shiftY]"));
  for(const species of ['Sockeye','Chinook','Coho']) assert.ok(tour.includes(species));
  assert.ok(tour.includes('latest published daily counts, not a live fish counter'));
  assert.equal((tour.match(/map-live-tab'\\)\\.forEach\\(b=>b\\.addEventListener/g)||[]).length,1);
});
"""
ts=ts[:start]+replacement
t.write_text(ts)
