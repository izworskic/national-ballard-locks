const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.join(__dirname, '..');
const main = fs.readFileSync(path.join(root, 'public/ballard-locks-v2/index.html'), 'utf8');
const tour = fs.readFileSync(path.join(root, 'public/ballard-locks-v2/tour/index.html'), 'utf8');

const banned = /\b(fascinating|amazing|be sure to|visitors can enjoy|whether you(?:'|’)re|nestled in|engineering marvel|iconic destination|rich history)\b/i;

test('main page explains one connected Ballard system instead of adding generic destination copy', () => {
  assert.match(main, /one working system doing three jobs at once/i);
  assert.match(main, /Move boats/i);
  assert.match(main, /Manage freshwater/i);
  assert.match(main, /Pass salmon/i);
  assert.match(main, /The Locks are working even when no boat moves/i);
});

test('main page repeatedly directs attention from screen to the real place', () => {
  assert.match(main, /Pick a mark on the lock wall and watch the waterline/i);
  assert.match(main, /Look beyond the chambers toward the spillway/i);
  assert.match(main, /watch a fish hold in the current, push forward, then settle again/i);
  assert.ok((main.match(/Look up from your phone/g) || []).length >= 3);
});

test('main live data is interpreted rather than merely displayed', () => {
  assert.match(main, /activity-story/);
  assert.match(main, /That is a real position report, not a promised lockage/i);
  assert.match(main, /level-story/);
  assert.match(main, /fish-story/);
  assert.match(main, /does not guarantee a fish will be in the window when you arrive/i);
});

test('tour stop popups use the ambassador interpretation anatomy', () => {
  for (const phrase of ['See this', 'What’s happening', 'Watch for', 'Why it matters', 'RIGHT NOW']) {
    assert.ok(tour.includes(phrase), `missing ${phrase}`);
  }
  for (const key of ["see:'", "happening:'", "watch:'", "why:'"]) {
    assert.ok(tour.includes(key), `missing stop field ${key}`);
  }
  assert.match(tour, /(Pick|Choose) one fixed mark on the concrete wall and watch the waterline move against it/i);
  assert.match(tour, /The stop that proves the Locks are doing more than moving boats/i);
});

test('tour preserves live decision value while adding interpretation', () => {
  assert.match(tour, /Best first stop/);
  assert.match(tour, /LIVE AIS/);
  assert.match(tour, /\/api\/ballard-locks/);
  assert.match(tour, /\/api\/ballard-ais/);
  assert.match(tour, /not a guaranteed lock transit/i);
});

test('ambassador copy avoids generic tourism filler', () => {
  assert.doesNotMatch(main, banned);
  assert.doesNotMatch(tour, banned);
});

test('current BallardLocks.org domain is still excluded as a linked authority', () => {
  assert.doesNotMatch(main, /href=["'][^"']*ballardlocks\.org/i);
  assert.doesNotMatch(tour, /href=["'][^"']*ballardlocks\.org/i);
});
