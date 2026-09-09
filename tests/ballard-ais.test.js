const test=require('node:test');
const assert=require('node:assert/strict');
const ais=require('../api/ballard-ais.js');

test('Ballard AIS bbox covers the Locks and nearby approaches',()=>{
  const [minLat,minLon,maxLat,maxLon]=ais._test.BBOX.split(',').map(Number);
  assert.ok(minLat < 47.66556 && maxLat > 47.66556);
  assert.ok(minLon < -122.39722 && maxLon > -122.39722);
});

test('AIS proxy sanitizes GeoJSON vessel features',()=>{
  const f=ais._test.sanitizeFeature({type:'Feature',id:'367123456',geometry:{type:'Point',coordinates:[-122.397,47.666]},properties:{name:'TEST BOAT',sog:5.2,cog:180,heading:181,source:'station'}});
  assert.equal(f.geometry.type,'Point');
  assert.deepEqual(f.geometry.coordinates,[-122.397,47.666]);
  assert.equal(f.properties.mmsi,'367123456');
  assert.equal(f.properties.name,'TEST BOAT');
  assert.equal(f.properties.sog,5.2);
});

test('AIS proxy rejects malformed coordinates',()=>{
  assert.equal(ais._test.sanitizeFeature({type:'Feature',geometry:{type:'Point',coordinates:[999,47]}}),null);
  assert.equal(ais._test.sanitizeFeature({type:'Feature',geometry:{type:'LineString',coordinates:[]}}),null);
});
