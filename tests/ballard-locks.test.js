const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const api = require('../api/ballard-locks')._test;

const page = fs.readFileSync(path.join(__dirname, '..', 'public', 'ballard-locks', 'index.html'), 'utf8');

test('page has one canonical H1 and the branded canonical URL', () => {
  assert.equal((page.match(/<h1\b/g) || []).length, 1);
  assert.match(page, /<link rel="canonical" href="https:\/\/chrisizworski\.com\/ballard-locks\/">/);
  assert.match(page, /Ballard Locks Live: Ships, Salmon &amp; Tides/);
});

test('page contains all core live layers and explicit AIS caveat', () => {
  for (const phrase of ['Go-now visitor score','Live marine traffic','Ballard Locks salmon activity','Ballard Locks camera','NOAA Tides &amp; Currents','National Weather Service','USACE']) assert.match(page, new RegExp(phrase.replace('&','&amp;?')));
  assert.match(page, /AIS map does not represent every pleasure boat/i);
  assert.match(page, /not an official lockage count/i);
});

test('fish parser extracts a current species table and ignores blank rows', () => {
  const fixture = `Daily Coho Counts\n2026 daily counts\nDate | Daily Count | Running Total\n9/1 | 13 | 433\n9/2 | 76 | 509\n9/3 | 463 | 972\n9/4 |  | 972\n2025 daily counts`;
  const parsed = api.parseSpecies(fixture, 'Coho', {year:2026,month:9,day:8});
  assert.equal(parsed.latest.date, '9/3');
  assert.equal(parsed.latest.daily, 463);
  assert.equal(parsed.latest.total, 972);
  assert.equal(parsed.ageDays, 5);
});

test('visitor access uses Pacific-time published hours', () => {
  assert.deepEqual(api.access({hour:8,minute:0}).groundsOpen, true);
  assert.deepEqual(api.access({hour:8,minute:0}).fishLadderOpen, true);
  assert.deepEqual(api.access({hour:21,minute:0}).groundsOpen, false);
  assert.deepEqual(api.access({hour:20,minute:50}).fishLadderOpen, false);
});

test('published maintenance windows affect only the scheduled chamber', () => {
  const normal = api.locks(new Date('2026-09-08T20:00:00Z'));
  assert.equal(normal.largeOpen, true);
  assert.equal(normal.smallOpen, true);
  const largeClosure = api.locks(new Date('2026-11-10T20:00:00Z'));
  assert.equal(largeClosure.largeOpen, false);
  assert.equal(largeClosure.smallOpen, true);
});

test('visit score is bounded and does not depend on invented vessel counts', () => {
  const result = api.score({
    f:{ok:true,species:[{species:'Coho',ageDays:1,latest:{daily:300,date:'9/8'}}]},
    t:{ok:true,predictions:[{type:'High',at:'2026-09-08T21:00:00Z'}]},
    w:{ok:true,temperatureF:65,precipitationProbability:10,windSpeed:'6 mph'},
    a:{groundsOpen:true,fishLadderOpen:true},
    l:{largeOpen:true,smallOpen:true},
    now:new Date('2026-09-08T20:00:00Z')
  });
  assert.ok(result.score >= 0 && result.score <= 100);
  assert.equal(result.salmon.label, 'HIGH');
});
