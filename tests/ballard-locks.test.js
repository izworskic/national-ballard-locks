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
  for (const phrase of ['Go-now visitor score','Live marine traffic','Ballard Locks salmon activity','Ballard Locks camera','National Weather Service','USACE']) {
    assert.ok(page.includes(phrase), `missing ${phrase}`);
  }
  assert.ok(page.includes('NOAA Tides &amp; Currents'), 'missing NOAA Tides & Currents source label');
  assert.match(page, /AIS map does not represent every pleasure boat/i);
  assert.match(page, /not an official lockage count/i);
});

test('fish parser binds to standalone WDFW headings, not prose mentions', () => {
  const fixture = `
Preliminary daily Chinook counts are typically available from late July through September and daily coho counts are typically available from early September into October.
Daily
 coho counts
2026 daily counts
Date | Daily Count | Running Total
9/1 | 13 | 433
9/2 | 76 | 509
9/3 | 463 | 972
9/4 |  | 972
Ballard Locks coho counts
Daily sockeye counts
2026 daily counts
Date | Daily Count | Running Total
9/1 | 0 | 31,302
9/2 | 0 | 31,302
9/3 | 0 | 31,302
Ballard Locks sockeye counts
Daily   Chinook counts
2026 daily counts
Date | Daily Count | Running Total
9/1 | 177 | 11,210
9/2 | 28 | 11,238
9/3 | 131 | 11,369
9/4 |  | 
Annual sockeye counts
`;
  const now = {year:2026,month:9,day:8};
  const coho = api.parseSpecies(fixture, 'Coho', now);
  const sockeye = api.parseSpecies(fixture, 'Sockeye', now);
  const chinook = api.parseSpecies(fixture, 'Chinook', now);

  assert.deepEqual(coho.latest, {date:'9/3',daily:463,total:972});
  assert.deepEqual(sockeye.latest, {date:'9/3',daily:0,total:31302});
  assert.deepEqual(chinook.latest, {date:'9/3',daily:131,total:11369});
  assert.equal(coho.ageDays, 5);
  assert.equal(sockeye.ageDays, 5);
  assert.equal(chinook.ageDays, 5);
});

test('parser fails closed instead of borrowing another species table', () => {
  const fixture = `Ballard Locks sockeye counts\n2026 daily counts\n9/3 | 0 | 31,302\nDaily Chinook counts\n2026 daily counts\n9/3 | 131 | 11,369`;
  assert.equal(api.parseSpecies(fixture, 'Sockeye', {year:2026,month:9,day:8}), null);
});

test('USACE Access to Water parser selects the live LWSC elevation series', () => {
  const parsed = api.parseA2wLatest([{
    provider:'NWS',
    code:'LWSC',
    timeseries:[
      {tsid:'LWSC.Flow.Ave.~1Day.1Day.CENWS-COMPUTED-RAW',label:'Outflow',unit:'cfs',latest_time:'2026-09-08T07:00:00Z',latest_value:249.57},
      {tsid:'LWSC.Elev-Lake.Ave.1Hour.1Hour.IRIDIUM-REV',label:'Elevation',unit:'ft',latest_time:'2026-09-08T22:00:00Z',latest_value:20.25,delta24hr:-0.03},
    ],
  }]);
  assert.equal(parsed.valueFt, 20.25);
  assert.equal(parsed.observedAt, '2026-09-08T22:00:00.000Z');
  assert.equal(parsed.delta24hr, -0.03);
  assert.equal(parsed.tsid, 'LWSC.Elev-Lake.Ave.1Hour.1Hour.IRIDIUM-REV');
  assert.equal(api.parseA2wLatest([{timeseries:[{label:'Elevation',unit:'ft',latest_time:null,latest_value:null}]}]), null);
});

test('visitor access uses Pacific-time published hours', () => {
  assert.equal(api.access({hour:8,minute:0}).groundsOpen, true);
  assert.equal(api.access({hour:8,minute:0}).fishLadderOpen, true);
  assert.equal(api.access({hour:21,minute:0}).groundsOpen, false);
  assert.equal(api.access({hour:20,minute:50}).fishLadderOpen, false);
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
