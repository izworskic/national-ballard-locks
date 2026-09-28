const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const api = require('../api/ballard-live-v2')._test;

test('season context distinguishes September species', () => {
  assert.equal(api.seasonFor('Sockeye', 9).status, 'OFFSEASON');
  assert.equal(api.seasonFor('Chinook', 9).status, 'IN SEASON');
  assert.equal(api.seasonFor('Coho', 9).status, 'IN SEASON');
});

test('vessel sanitization exposes visitor-useful movement context', () => {
  const v = api.sanitizeVessel({
    type:'Feature', geometry:{type:'Point',coordinates:[-122.402,47.666]},
    properties:{name:'TEST VESSEL',mmsi:'123456789',sog:6.2,cog:88}
  });
  assert.equal(v.name, 'TEST VESSEL');
  assert.equal(v.direction, 'eastbound');
  assert.ok(v.distanceMiles < 1);
  assert.equal(v.moving, true);
});

test('go-now score is driven by activity, salmon, access and weather rather than tide', () => {
  const base = {
    f:{ok:true,species:[{species:'Coho',ageDays:1,latest:{daily:90,date:'9/28'},season:{status:'IN SEASON'}}]},
    w:{ok:true,precipitationProbability:10,windSpeed:'5 mph',temperatureF:62},
    a:{groundsOpen:true,fishLadderOpen:true},
    l:{largeOpen:true,smallOpen:true},
    v:{ok:true,signal:'ACTIVE'}
  };
  const s = api.score(base);
  assert.ok(s.score >= 70);
  assert.equal(s.vessel.label, 'ACTIVE');
});

test('fish-ladder recommendation uses salmon points, fixing prior score-key mismatch', () => {
  const visit = {salmon:{points:20,detail:'Coho: 100 on 9/28'}};
  const rec = api.bestFirstStop({visit,a:{fishLadderOpen:true,groundsOpen:true,vesselTraffic:'24/7'},l:{largeOpen:true,smallOpen:true},v:{ok:true,signal:'QUIET',namedCount:0}});
  assert.equal(rec.name, 'Fish Ladder Viewing Room');
});

test('parking rate self-expires instead of becoming stale permanent copy', () => {
  assert.equal(api.parking(new Date('2026-10-15T12:00:00Z')).rate, '$2/hour');
  assert.equal(api.parking(new Date('2027-02-01T12:00:00Z')).rate, null);
});

test('new pages do not link to current BallardLocks.org domain as an authority', () => {
  for (const rel of ['public/ballard-locks-v2/index.html','public/ballard-locks-v2/tour/index.html','public/ballard-locks-v2/salmon-counts/index.html']) {
    const html = fs.readFileSync(path.join(__dirname,'..',rel),'utf8');
    assert.doesNotMatch(html, /href=["'][^"']*ballardlocks\.org/i);
  }
});

test('main page exposes decision-first vessel and tide semantics', () => {
  const html = fs.readFileSync(path.join(__dirname,'..','public/ballard-locks-v2/index.html'),'utf8');
  assert.match(html, /Best first stop now/i);
  assert.match(html, /What might you actually see/i);
  assert.match(html, /context only/i);
});
