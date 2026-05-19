# Geodetic Knife

> Ghana Geodetic Transformation Tool - WGS 84, GNG, GMG

A mobile-first PWA for precise coordinate transformations between Ghana's geodetic datums. Built with a Flask backend powered by pyproj and a zero-build-step vanilla frontend.

**Live:** https://geodetic-knife.vercel.app

---

## Features

- **Single-point transform** - WGS 84, GNG, GMG in one tap
- **Batch transform** - paste hundreds of coordinates, transform all at once
- **Local calibration** - derive your own 7-Parameter Helmert transformation from known control points via least-squares
- **GPS integration** - use device location as input directly
- **Reverse geocoding** - displays place name under every result
- **Dark / Light theme** - dark mode default, persisted to localStorage
- **PWA** - installable, offline-capable, no browser chrome
- **Mobile-first** - bottom tab nav, 48px touch targets, safe area support
- **Responsive** - sidebar layout on desktop (768px+)

---

## Coordinate Systems

| CRS | Full Name | Unit | EPSG |
|-----|-----------|------|------|
| WGS 84 | World Geodetic System 1984 | degrees | 4326 |
| GNG | Ghana National Grid | Gold Coast Foot (~0.3048 m) | 2136 (GCF) |
| GMG | Ghana Metre Grid | metres | 2136 (metres) |

The Gold Coast Foot conversion factor is 0.304799710181509 m/ft - the historical survey foot used in Ghana, distinct from both the International Foot (0.3048) and the US Survey Foot (0.3048006096).

---

## Architecture

```
geodetic-knife/
  api/
    index.py              # Flask backend (pyproj, numpy)
    requirements.txt      # flask, pyproj, numpy
  public/
    index.html            # Frontend SPA (vanilla JS, zero build)
    manifest.json         # PWA manifest + icons
  vercel.json             # Vercel deployment config
  README.md
```

**Backend:** Python 3.11 + Flask + pyproj 3.7 + numpy 1.26

**Frontend:** Single HTML file - no bundler, no framework, no node_modules. Pure CSS custom properties + vanilla JS with fetch().

---

## API Reference

All endpoints relative to /api/. Flask server on Vercel Python runtime.

### POST /api/convert - Single Transform

**Request:**

```json
{ "mode": "WGS84_TO_GRID", "lat": 5.5560, "lon": -0.1850, "calibration": { "towgs84": [-199, 32, 322, 0, 0, 0, 0] } }
```

**Response:**

```json
{ "gng": { "easting": 274319.74, "northing": 615007.53 }, "gmg": { "easting": 83606.28, "northing": 187465.52 }, "wgs84": { "lat": 5.5560, "lon": -0.1850 }, "accuracy": { "horizontal_accuracy_meters": "6", "method": "EPSG:6896", "active_method": "EPSG:6896" } }
```

**Modes:**

| Mode | Input Fields | Description |
|------|-------------|-------------|
| WGS84_TO_GRID | lat, lon | Geographic to projected grid |
| GRID_TO_WGS84 | easting, northing, from_crs | Grid to geographic |
| GNG_GMG | easting, northing, from_crs | Inter-grid conversion |

Every response includes all three CRS values regardless of input mode.

### POST /api/convert_batch - Batch Transform

```json
{ "points": [ { "mode": "WGS84_TO_GRID", "lat": 5.5560, "lon": -0.1850 }, { "mode": "WGS84_TO_GRID", "lat": 6.6884, "lon": -1.6244 } ] }
```

Returns results[] and errors[]. Each result has the same shape as single convert.

### POST /api/calibrate - 7-Param Helmert Calibration

```json
{ "points": [ { "wgs84": { "lat": 5.6037, "lon": -0.1870 }, "gmg": { "easting": 274319.74, "northing": 615007.53 } } ] }
```

Requires minimum 3 control points (max 50). The solver:

1. Converts WGS 84 lat/lon to ECEF (X, Y, Z) via Clarke 1880 ellipsoid
2. Converts GNG grid to GMG metres, then to ECEF via Accra datum ellipsoid
3. Computes ECEF differences for each point pair
4. Builds the 7-column design matrix (3 translation, 3 rotation, 1 scale)
5. Solves normal equations via numpy for the 7 unknowns
6. Returns towgs84: [dX, dY, dZ, rX, rY, rZ, ppm] auto-applied to all subsequent conversions

### GET /api/calibration_status

Returns active method, parameters, and accuracy estimate. No params.

### GET /api/geocode?lat=5.6&lon=-0.2 - Reverse Geocode

Proxies to Nominatim OSM. Returns display_name, region, district.

### GET /api/elevation?lat=5.6&lon=-0.2 - Elevation

SRTM elevation in metres.

### POST /api/azimuth_distance - Azimuth and Distance

Vincenty inverse on WGS 84 ellipsoid. Returns metres and Gold Coast Feet.

### GET /api/method and POST /api/method - List or Switch Methods

---

## Transformation Methods

| Method ID | Name | Accuracy | Params |
|-----------|------|----------|--------|
| EPSG:6896 | NGA Geocentric (default) | ~6 m | 3-param Molodensky |
| EPSG:1569 | OS Military | ~25 m | 3-param Molodensky |
| CUSTOM | User-calibrated | varies | 7-param Helmert |

Default towgs84: [-170, 33, 326, 0, 0, 0, 0]. After calibration, your derived 7 parameters replace these - typically sub-metre within the calibration area.

---

## Calibration - How It Works

The 7-Parameter Helmert is a similarity transformation between two 3D reference frames:

- 3 translations (dX, dY, dZ) - origin shift
- 3 rotations (rX, rY, rZ) - axis misalignment (arc-seconds)
- 1 scale factor (ppm) - ellipsoid size difference

```
X_wgs = dX + s * (X_local - rZ*Y_local + rY*Z_local)
Y_wgs = dY + s * (rZ*X_local + Y_local - rX*Z_local)
Z_wgs = dZ + s * (-rY*X_local + rX*Y_local + Z_local)
```

Requires 3+ known control points. 7+ recommended for robust network adjustment. Per-point residuals let you identify outliers.

---

## Test Coordinates

| Location | Lat | Lon |
|----------|-----|-----|
| Accra, Osu Castle | 5.5560 | -0.1850 |
| Kumasi, Kejetia | 6.6884 | -1.6244 |
| Tamale | 9.4034 | -0.8393 |
| Takoradi Harbour | 4.8983 | -1.7607 |
| Cape Coast Castle | 5.1036 | -1.2466 |
| Tema Port | 5.6696 | 0.0166 |
| Ho | 6.6100 | 0.4700 |
| Sunyani | 7.3349 | -2.3266 |
| Bolgatanga | 10.7874 | -0.8714 |
| Wa | 10.0601 | -2.5096 |

---

## Deployment

Vercel - push to GitHub, auto-deploys.

Local development:

```bash
cd api && pip install -r requirements.txt && flask run --port 5000
cd public && python -m http.server 3000
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask 3.1, pyproj 3.7, numpy 1.26 |
| Frontend | Vanilla HTML/CSS/JS (no framework) |
| Fonts | Inter, JetBrains Mono (Google Fonts) |
| Hosting | Vercel Python runtime + static |
| Geocoding | Nominatim OSM (proxied) |
| Elevation | Open-Elevation SRTM |

---

## License

MIT
