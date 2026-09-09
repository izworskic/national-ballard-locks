const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const tour = fs.readFileSync(path.join(__dirname, '..', 'public', 'ballard-locks', 'tour', 'index.html'), 'utf8');

test('tour map allows only one stop popup at a time', () => {
  assert.ok(tour.includes('activePopup=null'), 'tour should track one active popup');
  assert.ok(tour.includes("popup.on('open'"), 'tour popup should handle open lifecycle');
  assert.ok(tour.includes('if(activePopup&&activePopup!==popup)activePopup.remove()'), 'opening a stop should close the previously active popup');
  assert.ok(tour.includes("popup.on('close'"), 'tour popup should clear active state when closed');
});
