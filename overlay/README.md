# Thermocline Heatmap Data — globe overlay pack

Reusable climate layers for ≤2.5°C-approach dry coolers. Drop the overlay PNGs
onto any sphere, or use the GeoTIFFs to recolor / reproject yourself.

## Files

**Overlay textures (transparent ocean — paint straight onto a globe)**
- `heat_adiabatic_overlay.png`     — adiabatic-assist demand (blue→red)
- `freeze_antifreeze_overlay.png`  — anti-freeze-mode frequency (light→deep purple)

**Raw georeferenced data (GeoTIFF, EPSG:4326, nodata = -9999)**
- `design_peak_degC.tif`         — approx annual design dry-bulb (°C) = WorldClim BIO5 + 6 °C
- `adiabatic_index_0to1.tif`     — normalized heat index (0 = pure dry … 1 = adiabatic essential)
- `freeze_months_per_year.tif`   — months/yr with mean daily-min < 0 °C (0–12)
- `antifreeze_index_0to1.tif`    — normalized freeze index (0 = never … 1 = year-round)

## Grid / projection (all files)
- Equirectangular (plate carrée), 2048 × 1024, 2:1.
- Longitude −180 → +180 across width (x=0 is −180°). Latitude +90 → −90 down height (y=0 is +90°).
- This is exactly what three.js SphereGeometry expects as a UV texture map.

## Calibration (physics)
- Heat: pure-dry feasible while ambient dry-bulb < ~42.5 °C (≤2.5 °C approach on a 45 °C loop).
  index = clamp((design_peak − 30) / (50 − 30), 0, 1).
- Freeze: index = (freeze_months / 12) ^ 0.62  (low-end lift: any freeze ⇒ glycol year-round).
- Notes: dry-bulb driven (understates humid-hot coasts); +6 °C uplift is illustrative,
  not site ASHRAE. Antarctica/poles absent (WorldClim 10m coverage). Source: WorldClim 2.1.

## Colormaps (gradient stops, position → hex)
HEAT:   0.00 #19c3e6 · 0.18 #22d3ee · 0.34 #38bdf8 · 0.50 #a3e635 · 0.66 #facc15 · 0.82 #f59e0b · 1.00 #ef4444
FREEZE: 0.00 #1a2433 · 0.06 #cdbce8 · 0.22 #b794f4 · 0.42 #9b6ef0 · 0.62 #7c3aed · 0.82 #5b21b6 · 1.00 #3b0a78

## Drop-in three.js overlay (r128+)
```js
const tex = new THREE.TextureLoader().load('heat_adiabatic_overlay.png');
tex.encoding = THREE.sRGBEncoding;
const overlay = new THREE.Mesh(
  new THREE.SphereGeometry(EARTH_RADIUS * 1.001, 96, 96),  // just above your base globe
  new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false })
);
yourGlobeGroup.add(overlay);   // rotates with the globe; ocean is transparent
```
Swap to `freeze_antifreeze_overlay.png` for the cold-end layer, or crossfade material.opacity between two overlay meshes.

## lat/lon → sphere (matches the texture UVs)
```js
function llToVec(lat, lon, r){
  const u=(lon+180)/360, v=(90-lat)/180, phi=u*2*Math.PI, th=v*Math.PI;
  return new THREE.Vector3(-r*Math.cos(phi)*Math.sin(th), r*Math.cos(th), r*Math.sin(phi)*Math.sin(th));
}
```
