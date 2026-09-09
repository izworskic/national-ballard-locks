import fs from 'node:fs';

const file='public/ballard-locks/index.html';
let html=fs.readFileSync(file,'utf8');
const href='https://chrisizworski.com/ballard-locks/tour/';
if(!html.includes(href)){
  const anchor='<div class="callout"><strong>Traffic caveat:</strong>';
  const start=html.indexOf(anchor);
  if(start<0) throw new Error('Interactive tour injector: callout anchor missing');
  const end=html.indexOf('</div>',start);
  if(end<0) throw new Error('Interactive tour injector: callout end missing');
  const insert=end+'</div>'.length;
  const card='\n<section class="section" id="tour"><div class="panel" style="padding:22px;background:linear-gradient(135deg,#e7f1ee,#fffaf0)"><div class="section-kicker">New interactive walking map</div><h2 style="margin:5px 0 9px">Explore the Locks stop by stop</h2><p style="max-width:820px;margin:0 0 14px;color:#607579">Choose a 20-, 45- or 75-minute self-guided route through the lock chambers, fish ladder, Salmon Waves, gardens, heron colony, historic buildings and nearby Ballard landmarks. The map carries the live salmon, chamber and water-level signals with you.</p><a class="btn dark" href="'+href+'">Open the interactive tour map &rarr;</a></div></section>';
  html=html.slice(0,insert)+card+html.slice(insert);
  fs.writeFileSync(file,html);
  console.log('Interactive tour discovery added.');
}else console.log('Interactive tour discovery already present.');
