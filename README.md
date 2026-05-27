# Geodetic Knife

**Ghana Geodetic Transformation Tool**

[Live Demo](https://geodetic-knife.netlify.app)

A web-based coordinate transformation tool supporting conversion between WGS84 and Ghana's two primary grid systems: the Ghana National Grid (GNG) and the Ghana Metre Grid (GMG). Built with Flask (pyproj) backend and a responsive dark-theme UI.

---

## Features

- **WGS84 to Grid** - Convert geographic coordinates (lat/lon) to GNG or GMG
- **Grid to Grid** - Convert directly between GNG and GMG via WGS84 intermediate
- **Grid to WGS84** - Reverse conversion from grid coordinates back to lat/lon
- **Calibration** - 4-parameter Helmert affine transformation using known control points, with residual analysis and RMS reporting
- **CSV Export/Import** - Export conversion results and calibration data, import control points from CSV
- **CRS Settings** - Configurable projection parameters (false easting, datum shift, scale factor, etc.)
- **REST API** - Full JSON API for programmatic access (`/api/convert`, `/api/batch`, `/api/calibrate`)

---

## Quick Start

### 1. Install Dependencies

```bash
pip install flask pyproj
```

### 2. Run the Server

```bash
python app.py
```

### 3. Open in Browser

Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Project Structure

```
geodetic-knife/
  app.py            Flask backend with pyproj conversion API
  index.html        Frontend (all CSS, HTML, and JavaScript inline)
  requirements.txt  Python dependencies
  README.md         This file
```

---

## Configuration

### Default CRS Parameters

Both GNG and GMG share the same underlying projection but differ in their false easting values:

| Parameter | GNG | GMG |
|---|---|---|
| Projection | Transverse Mercator | Transverse Mercator |
| Ellipsoid | Clarke 1880 (RGS) | Clarke 1880 (RGS) |
| Datum | Leigon | Leigon |
| False Easting | 274,319.514 m | 1,000,000 m |
| False Northing | 0 m | 0 m |
| Central Meridian | 1° W (-1.0) | 1° W (-1.0) |
| Origin Latitude | 4° 40' N (4.6667°) | 4° 40' N (4.6667°) |
| Scale Factor | 0.99975 | 0.99975 |
| Datum Shift (dx, dy, dz) | -130, 29, 364 | -130, 29, 364 |

### Changing CRS Parameters in the UI

1. Open the app and click the **Settings** tab
2. Edit any parameter (false easting, datum shift, scale factor, etc.)
3. Click **Apply Settings** to reload the projections with new values
4. Click **Reset to Defaults** to restore the standard parameters

### Changing CRS Parameters in app.py

To change the defaults in code, edit the relevant variables at the top of `app.py`:

```python
# GNG definition
GNG_DEF = (
    "+proj=tmerc +lat_0=4.6666666667 +lon_0=-1 +k=0.99975 "
    "+x_0=274319.514 +y_0=0 +ellps=clrk80 +towgs84=-130,29,364 "
    "+units=m +no_defs"
)

# GMG definition
GMG_DEF = (
    "+proj=tmerc +lat_0=4.6666666667 +lon_0=-1 +k=0.99975 "
    "+x_0=1000000 +y_0=0 +ellps=clrk80 +towgs84=-130,29,364 "
    "+units=m +no_defs"
)

# Datum shift to WGS84
TOWGS84 = -130, 29, 364  # dx, dy, dz in metres
```

---

## API Reference

All API endpoints accept and return JSON.

### POST /api/convert

Single coordinate conversion.

**WGS84 to Grid:**
```json
{
  "type": "wgs84_to_grid",
  "lat": 5.6037,
  "lon": -0.1870,
  "tgt_grid": "GNG"
}
```

**Grid to WGS84:**
```json
{
  "type": "grid_to_wgs84",
  "easting": 752468.5,
  "northing": 620457.3,
  "src_grid": "GNG"
}
```

**Grid to Grid:**
```json
{
  "type": "grid_to_grid",
  "easting": 752468.5,
  "northing": 620457.3,
  "src_grid": "GNG",
  "tgt_grid": "GMG"
}
```

### POST /api/batch

Batch conversion of multiple points.

```json
{
  "type": "wgs84_to_grid",
  "grid": "GNG",
  "points": [
    {"lat": 5.6037, "lon": -0.1870},
    {"lat": 5.5510, "lon": -0.2250}
  ]
}
```

### POST /api/calibrate

Compute 4-parameter Helmert transformation from control points.

```json
{
  "points": [
    {"lat": 5.6037, "lon": -0.1870, "easting": 752468.5, "northing": 620457.3, "grid": "GNG"},
    {"lat": 5.5510, "lon": -0.2250, "easting": 748230.1, "northing": 615890.7, "grid": "GNG"}
  ]
}
```

Returns transformation parameters (a, b, c, d), scale factor, rotation angle, and per-point residuals.

### GET /api/crs

Returns the full CRS definitions for both GNG and GMG.

### GET /api/health

Health check. Returns `{"status": "ok"}`.

---

## CSV Import/Export

### Exporting Results

After performing any conversion, click **Export CSV** to download the result as a `.csv` file.

### Exporting Calibration Points

On the Calibrate tab, click **Export CSV** to save all control points as a CSV file.

### Importing Control Points

On the Calibrate tab, click **Import CSV** and select a file with this format:

```csv
Latitude,Longitude,Easting,Northing,GridType
5.6037,-0.1870,752468.5,620457.3,GNG
5.5510,-0.2250,748230.1,615890.7,GNG
5.6120,-0.1580,754100.2,621880.4,GMG
```

- First row is treated as a header if it contains letters
- Grid type defaults to GNG if omitted or unrecognised
- Invalid rows are silently skipped

---

## Calibration

The calibration tool computes a **4-parameter Helmert (similarity) transformation** using least-squares estimation:

```
E' = a * E - b * N + c
N' = b * E + a * N + d
```

Where:
- `a, b` encode rotation and scale
- `c, d` are translation offsets
- Scale = sqrt(a² + b²)
- Rotation = atan2(b, a)

**Steps:**
1. Click **Calibrate** tab
2. Enter at least 2 known control points (both WGS84 and grid coordinates)
3. Click **Run Calibration**
4. Review the parameters, residuals table, and RMS value

Lower RMS indicates a better fit. Points with unusually high residuals may be errors or outliers.

---

## Technologies

| Component | Technology |
|---|---|
| Backend | Python 3, Flask 3, pyproj |
| Frontend | Vanilla HTML/CSS/JavaScript |
| Projection Library (client) | proj4js 2.11 (CDN) |
| Projection Library (server) | pyproj 3 |
| Ellipsoid | Clarke 1880 (RGS) |
| Datum | Leigon (3-parameter Helmert to WGS84) |
