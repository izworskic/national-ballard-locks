const test=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const page=fs.readFileSync(path.join(__dirname,'..','public','ballard-locks','salmon-counts','index.html'),'utf8');
const parent=fs.readFileSync(path.join(__dirname,'..','public','ballard-locks','index.html'),'utf8');
test('salmon counts page is canonical and indexable',()=>{assert.match(page,/https:\/\/chrisizworski\.com\/ballard-locks\/salmon-counts\//);assert.match(page,/name="robots" content="index,follow/);assert.match(page,/FAQPage/)});
test('salmon counts page uses authoritative live API and preserves freshness semantics',()=>{assert.match(page,/fetch\('\/api\/ballard-locks'/);assert.match(page,/latest published/i);assert.match(page,/does not silently turn an older observation into a same-day count/i)});

test('main Ballard page explicitly hands salmon-count intent to the dedicated page',()=>{assert.match(parent,/href="\/ballard-locks\/salmon-counts\/"/);assert.match(parent,/latest Ballard Locks salmon counts/i)});
