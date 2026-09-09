const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');

const tour=fs.readFileSync(path.join(__dirname,'..','public','ballard-locks','tour','index.html'),'utf8');
const main=fs.readFileSync(path.join(__dirname,'..','public','ballard-locks','index.html'),'utf8');

test('interactive tour has canonical route, one H1 and no paid map key dependency',()=>{
  assert.equal((tour.match(/<h1\b/g)||[]).length,1);
  assert.match(tour,/https:\/\/chrisizworski\.com\/ballard-locks\/tour\//);
  assert.ok(tour.includes('https://tiles.openfreemap.org/styles/liberty'));
  assert.ok(tour.includes('maplibre-gl@5'));
  assert.doesNotMatch(tour,/mapbox.*access[_-]?token/i);
  assert.doesNotMatch(tour,/api[_-]?key=/i);
});

test('tour preserves original eight hidden stops and adds core infrastructure',()=>{
  for(const phrase of ['Railroad bridge viewpoint','Great Blue Heron Colony','Fish Ladder Viewing Room','Salmon Waves','Small Lock','Historic Cavanaugh House','A Salish Welcome','National Nordic Museum & Frankie Feetsplinters','Large Lock','Spillway & water control','Carl S. English Jr. Botanical Garden']){
    assert.ok(tour.includes(phrase),`missing ${phrase}`);
  }
  for(const n of [1,2,3,4,5,6,7,8]) assert.ok(tour.includes(`legacy:${n}`),`missing original stop ${n}`);
});

test('tour is decision-oriented and connected to live Ballard data',()=>{
  for(const phrase of ['20 min · Essentials','45 min · Full Locks','75 min · + Ballard','Locate me','/api/ballard-locks','Start at the fish ladder','Ship Canal elevation']) assert.ok(tour.includes(phrase),`missing ${phrase}`);
});

test('main Ballard page exposes the interactive tour',()=>{
  assert.ok(main.includes('https://chrisizworski.com/ballard-locks/tour/'));
  assert.ok(main.includes('Explore the Locks stop by stop'));
});

test('tour puts fish AIS and the live camera directly on the map',()=>{
  assert.ok(!tour.includes('What this map adds'));
  assert.ok(tour.includes('id="map-live-dock"'));
  assert.ok(tour.includes('data-live-panel="fish"'));
  assert.ok(tour.includes('data-live-panel="ais"'));
  assert.ok(tour.includes('data-live-panel="camera"'));
  assert.ok(tour.includes('https://embed.myshiptracking.com/embed?myst'));
  assert.ok(tour.includes('https://g1.ipcamlive.com/player/player.php?alias=5ababb8154afe'));
  for(const species of ['Sockeye','Chinook','Coho']) assert.ok(tour.includes(species));
  assert.ok(tour.includes('latest published daily counts, not a live fish counter'));
  assert.ok(!tour.includes("function setRoute(key){current=key;document.querySelectorAll('.map-live-tab')"));
  assert.equal((tour.match(/map-live-tab'\)\.forEach\(b=>b\.addEventListener/g)||[]).length,1);
});
