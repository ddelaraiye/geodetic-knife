# Geodetic Knife - User Manual

**Ghana Geodetic Transformation Tool v2.0**

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Architecture](#2-system-architecture)
3. [Panel-by-Panel Guide](#3-panel-by-panel-guide)
   - 3.1 [WGS84 to Grid](#31-wgs84-to-grid)
   - 3.2 [Grid Convert](#32-grid-convert)
   - 3.3 [Grid to WGS84](#33-grid-to-wgs84)
   - 3.4 [Calibrate](#34-calibrate)
   - 3.5 [Settings](#35-settings)
4. [Mathematical Reference](#4-mathematical-reference)
   - 4.1 [Reference Ellipsoid](#41-reference-ellipsoid)
   - 4.2 [Transverse Mercator Projection](#42-transverse-mercator-projection)
   - 4.3 [Datum Transformation (3-Parameter Helmert)](#43-datum-transformation-3-parameter-helmert)
   - 4.4 [4-Parameter Helmert Calibration (Affine Similarity)](#44-4-parameter-helmert-calibration-affine-similarity)
5. [Default Parameters Reference](#5-default-parameters-reference)
6. [CSV Data Format](#6-csv-data-format)
7. [REST API Reference](#7-rest-api-reference)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Introduction

Geodetic Knife is a professional-grade coordinate transformation tool designed specifically for Ghana's geodetic systems. It provides seamless conversion between the World Geodetic System 1984 (WGS84) and Ghana's two national grid systems: the Ghana National Grid (GNG) and the Ghana Metre Grid (GMG). The tool is built as a web application with a Python (Flask + pyproj) backend and a responsive dark-theme frontend powered by proj4js for client-side transformations.

The primary use cases include surveying, cartography, GIS data migration, land administration, and any workflow requiring accurate conversion between geographic (latitude/longitude) and projected (easting/northing) coordinates within Ghana. The calibration feature allows surveyors to compute localised transformation parameters from known control points, enabling residual analysis and quality assessment of coordinate data.

---

## 2. System Architecture

The application follows a client-server architecture with dual transformation engines:

**Backend (Python/Flask):** Serves the static HTML frontend and exposes REST API endpoints at `/api/convert`, `/api/batch`, `/api/calibrate`, `/api/crs`, and `/api/health`. All server-side coordinate math is handled by pyproj, which implements the full PROJ coordinate transformation library. The Flask server listens on `127.0.0.1:5000` and must be running for the web interface to load.

**Frontend (Browser/JavaScript):** The entire UI is contained in a single `index.html` file with inline CSS and JavaScript. Coordinate transformations are performed directly in the browser using proj4js loaded from a CDN, meaning the conversion panels work entirely on the client side without needing to call the backend API. This provides instant results and works even if the server is temporarily unreachable after the page has loaded.

**PWA Support:** The application includes a `manifest.json` and can be installed as a Progressive Web App on mobile devices and desktop browsers.

---

## 3. Panel-by-Panel Guide

The interface consists of five tabs arranged horizontally at the top of the page. Each tab reveals a dedicated panel for a specific task. The following sections describe each panel in detail.

### 3.1 WGS84 to Grid

**Purpose:** Convert geographic coordinates (WGS84 latitude and longitude) into projected grid coordinates (Easting and Northing) in either GNG or GMG.

**Input Fields:**
- **Latitude** - The geographic latitude in decimal degrees. Positive values for north of the equator. Example: `5.6037` for a location near Accra.
- **Longitude** - The geographic longitude in decimal degrees. Negative values for west of the prime meridian. Example: `-0.1870` for a location west of Greenwich.
- **Target Grid** - A dropdown selector to choose between "Ghana National Grid (GNG)" and "Ghana Metre Grid (GMG)".

**Buttons:**
- **Convert** - Executes the transformation and displays the result below the form.
- **Clear** - Resets all input fields and hides the result card.
- **Export CSV** - Downloads the conversion result as a CSV file named `geodetic_WGS84_to_Grid.csv`.

**Output:** A result card appears below the form showing the input latitude/longitude (to 8 decimal places) and the computed Easting and Northing (to 3 decimal places, in metres).

**How it works internally:** The input latitude and longitude are passed to proj4js as an `[lon, lat]` array in EPSG:4326. The proj4 library first applies the 3-parameter datum shift (towgs84) to convert from the WGS84 datum to the Leigon datum (Clarke 1880 ellipsoid), then applies the Transverse Mercator projection equations with the selected grid's parameters (false easting, central meridian, scale factor, etc.) to produce the final Easting and Northing.

---

### 3.2 Grid Convert

**Purpose:** Convert projected coordinates from one Ghana grid system to the other (GNG to GMG or GMG to GNG).

**Input Fields:**
- **Easting** - The source grid easting in metres.
- **Northing** - The source grid northing in metres.
- **Source Grid** - Dropdown to select the input grid system (GNG or GMG).
- **Target Grid** - Dropdown to select the output grid system (GNG or GMG). Defaults to the opposite of the source.

**Buttons:**
- **Convert** - Executes the two-step conversion.
- **Clear** - Resets all input fields and hides results.
- **Export CSV** - Downloads the result as `geodetic_Grid_Convert.csv`.

**Output:** Displays the source Easting/Northing, intermediate WGS84 latitude/longitude (to 8 decimal places), and the computed target Easting/Northing (to 3 decimal places).

**How it works internally:** This is a two-step process. First, the source grid coordinates are reverse-projected through the Transverse Mercator inverse equations to obtain WGS84 latitude and longitude. Then, these geographic coordinates are forward-projected using the target grid's projection parameters. The intermediate WGS84 values are shown in the output so the user can verify the intermediate result independently.

---

### 3.3 Grid to WGS84

**Purpose:** Convert projected grid coordinates (Easting and Northing) back to geographic coordinates (latitude and longitude).

**Input Fields:**
- **Easting** - The grid easting in metres.
- **Northing** - The grid northing in metres.
- **Source Grid** - Dropdown to select the grid system (GNG or GMG).

**Buttons:**
- **Convert** - Executes the inverse transformation.
- **Clear** - Resets all fields and hides results.
- **Export CSV** - Downloads as `geodetic_Grid_to_WGS84.csv`.

**Output:** Displays the input Easting/Northing and the computed latitude/longitude (to 8 decimal places).

**How it works internally:** proj4js applies the inverse Transverse Mercator projection equations to convert the grid coordinates back to latitude/longitude on the Clarke 1880 ellipsoid, then applies the reverse 3-parameter datum shift (from Leigon to WGS84) to produce the final WGS84 geographic coordinates.

---

### 3.4 Calibrate

**Purpose:** Compute a 4-parameter Helmert (affine similarity) transformation from a set of known control points. This is used to determine the local distortion between observed grid coordinates and coordinates derived from WGS84, producing correction parameters that can be applied to improve transformation accuracy in a specific survey area.

**Table Columns:**
- **#** - Row number (auto-incremented).
- **Latitude** - Known WGS84 latitude of the control point.
- **Longitude** - Known WGS84 longitude of the control point.
- **Easting** - Known grid easting (observed/surveyed value).
- **Northing** - Known grid northing (observed/surveyed value).
- **Grid** - Dropdown to select GNG or GMG for each point individually.
- **X** - Button to remove the row.

**Buttons:**
- **+ Add Point** - Adds a new empty row to the table (maximum 50 rows).
- **Run Calibration** - Executes the least-squares computation. Requires at least 2 valid control points.
- **Clear All** - Removes all rows and hides results.
- **Export CSV** - Downloads all control points as `geodetic_calibration.csv`.
- **Import CSV** - Opens a file picker to load control points from a CSV file.

**Output:** After running calibration, a result card shows:
- **Scale Factor** - The computed scale (should be close to 1.00000000 if the datum is well-fitted).
- **Rotation** - The rotation angle in decimal degrees.
- **Translation X** - Easting translation offset in metres (parameter c).
- **Translation Y** - Northing translation offset in metres (parameter d).
- **Parameter a** - The rotation-scale easting coefficient.
- **Parameter b** - The rotation-scale northing coefficient.
- **RMS Residual** - Root mean square of all point residuals in metres.
- **Max Residual** - The largest single-point residual in metres.
- **Affine Formula** - The explicit transformation equations with numerical coefficients substituted.
- **Residuals Table** - Per-point breakdown of dE (easting residual), dN (northing residual), and the vector magnitude |d| for each control point.

**How it works internally:** For each control point, the WGS84 coordinates are converted to grid coordinates using proj4js to get the "true" grid position. These serve as the target values. The user's entered Easting/Northing serve as the observed values. The 4-parameter Helmert transformation is then solved via least squares to find the best-fit parameters (a, b, c, d) that map observed to true coordinates. See Section 4.4 for the full mathematical derivation.

---

### 3.5 Settings

**Purpose:** View and modify the Coordinate Reference System (CRS) parameters used by all conversion functions. This allows advanced users to experiment with different projection parameters, test alternative datum shifts, or configure the tool for a custom local grid.

**GNG Section:**
- **False Easting (m)** - The easting value assigned to the central meridian at the origin latitude. Default: `274319.514`.
- **False Northing (m)** - The northing value assigned to the equator. Default: `0`.
- **Central Meridian** - The longitude of the central meridian in decimal degrees. Default: `-1` (1 degree West).
- **Origin Latitude** - The latitude of the projection origin in decimal degrees. Default: `4.6666666667` (4 degrees 40 minutes North).
- **Scale Factor** - The scale factor at the central meridian. Default: `0.99975`.
- **Datum Shift (dx,dy,dz)** - Comma-separated 3-parameter Helmert shift from Leigon datum to WGS84 in metres. Default: `-130,29,364`.

**GMG Section:** Same parameters with False Easting defaulting to `1000000` instead of `274319.514`.

**Buttons:**
- **Apply Settings** - Reads all fields and re-initialises the proj4js CRS definitions with the new values. All subsequent conversions will use the updated parameters. A toast notification confirms success.
- **Reset to Defaults** - Restores all fields to the factory defaults and re-initialises the CRS definitions.

**Important notes:** Changing these parameters affects all conversion panels immediately. There is no undo beyond clicking Reset to Defaults. The server-side API endpoints in `app.py` use their own hardcoded CRS definitions and are NOT affected by changes made in the Settings panel.

---

## 4. Mathematical Reference

This section provides the complete mathematical foundation behind every transformation performed by the tool, enabling independent verification and cross-checking of results.

### 4.1 Reference Ellipsoid

All Ghana grid systems are defined on the **Clarke 1880 (RGS)** ellipsoid, specified by two fundamental parameters:

| Parameter | Symbol | Value | Description |
|---|---|---|---|
| Semi-major axis | a | 6,378,249.145 m | Equatorial radius |
| Reciprocal flattening | 1/f | 293.466307656 | Defines the ellipsoid shape |

From these, derived parameters are computed:

**Semi-minor axis (b):**
```
b = a * (1 - f)
b = 6378249.145 * (1 - 1/293.466307656)
b = 6356514.8696 m (approximately)
```

**First eccentricity (e):**
```
e = sqrt(2f - f^2)
e = sqrt(2/293.466307656 - 1/293.466307656^2)
e = 0.08248325679 (approximately)
```

**Second eccentricity (e'):**
```
e' = e / sqrt(1 - e^2)
e' = 0.08280532506 (approximately)
```

WGS84 uses a different ellipsoid (GRS 80): a = 6,378,137.0 m, 1/f = 298.257222101. The datum transformation (Section 4.3) bridges these two ellipsoids.

---

### 4.2 Transverse Mercator Projection

Both GNG and GMG use the **Transverse Mercator** projection with the same underlying parameters except for the false easting. The projection formulas convert geodetic coordinates on the Clarke 1880 ellipsoid to rectangular grid coordinates.

**Projection Parameters (shared by GNG and GMG):**

| Parameter | Value | DMS Notation |
|---|---|---|
| Central Meridian (lambda_0) | -1.00000000 | 1 deg 00 min 00 sec W |
| Origin Latitude (phi_0) | 4.6666666667 | 4 deg 40 min 00 sec N |
| Scale Factor at CM (k_0) | 0.99975 | - |
| GNG False Easting (E_0) | 274,319.514 m | - |
| GMG False Easting (E_0) | 1,000,000.000 m | - |
| False Northing (N_0) | 0 m | - |

**Forward Projection (Geodetic to Grid):**

Given geodetic coordinates (latitude phi, longitude lambda) on the Clarke 1880 ellipsoid:

1. Compute the meridional arc distance from the equator to latitude phi using the series expansion:
```
S = a * [A_0 * phi - A_2 * sin(2*phi) + A_4 * sin(4*phi) - A_6 * sin(6*phi) + ...]
```
where the coefficients A_n depend on the ellipsoid parameters n, e, and e'.

2. Compute the conformal latitude chi from the geodetic latitude phi using the series:
```
chi = phi - (e^2/2 + 5*e^4/24 + e^6/12 + ...) * sin(2*phi)
        + (7*e^4/48 + 29*e^6/240 + ...) * sin(4*phi)
        - (7*e^6/120 + ...) * sin(6*phi) + ...
```

3. Compute the isometric latitude:
```
psi = ln(tan(pi/4 + chi/2))
```

4. Compute the projection using the Transverse Mercator formulas:
```
B = (e'^2/4 + e'^4/64 + ...) * sin(2*chi)
eta_prime = e'^2 * cos^2(chi)
nu = a / sqrt(1 - e^2 * sin^2(phi))
rho = a * (1 - e^2) / (1 - e^2 * sin^2(phi))^(3/2)

E = k_0 * nu * [A + (1-T+C)*A^3/6 + (5-18T+T^2+72C-58*e'^2)*A^5/120] + E_0
N = k_0 * [M + nu * tan(phi) * (A^2/2 + (5-T+9C+4C^2)*A^4/24
        + (61-58T+T^2+600C-330*e'^2)*A^6/720)] + N_0
```
where:
- A = (lambda - lambda_0) * cos(chi)
- T = tan^2(chi)
- C = e'^2 * cos^2(chi)
- M = meridional arc distance

In practice, proj4js and pyproj implement these formulas using highly optimised numerical algorithms with iterative convergence for the inverse projection, ensuring sub-millimetre accuracy.

**Inverse Projection (Grid to Geodetic):**

The inverse uses an iterative Newton-Raphson method. Given grid coordinates (E, N), the footpoint latitude is first estimated, then iteratively refined until convergence:

1. Compute the footpoint latitude phi_1 from the northing.
2. Iterate to refine phi_1 until the change is negligible.
3. Compute the longitude from the easting.

The full iterative formulas are implemented in the PROJ library (underlying both proj4js and pyproj) and follow the standard Transverse Mercator inverse equations documented in Snyder (1987), "Map Projections: A Working Manual", USGS Professional Paper 1395.

**The difference between GNG and GMG:** Both grids use identical ellipsoid, datum, central meridian, origin latitude, and scale factor. The ONLY difference is the false easting: GNG uses 274,319.514 m (chosen to keep eastings positive across Ghana) while GMG uses 1,000,000 m (a round number convention). Converting between them simply requires subtracting the source false easting, adding the target false easting, and accounting for any slight differences due to the datum transformation path.

---

### 4.3 Datum Transformation (3-Parameter Helmert)

The Leigon datum (used by GNG and GMG) and WGS84 are defined on different ellipsoids and have a relative position offset. The tool uses a **3-parameter Helmert (Molodensky) transformation** to bridge the two datums.

**Transformation Parameters (Leigon to WGS84):**

| Parameter | Value | Unit |
|---|---|---|
| X translation (dx) | -130 | metres |
| Y translation (dy) | +29 | metres |
| Z translation (dz) | +364 | metres |

These three shifts represent the position of the Leigon datum origin relative to the WGS84 datum origin in the 3D geocentric Cartesian coordinate system.

**Forward Transformation (WGS84 to Leigon):**

1. Convert WGS84 geodetic coordinates (phi_WGS84, lambda_WGS84, h) to WGS84 geocentric Cartesian:
```
X = (N + h) * cos(phi) * cos(lambda)
Y = (N + h) * cos(phi) * sin(lambda)
Z = [N * (1 - e^2) + h] * sin(phi)
```
where N = a / sqrt(1 - e^2 * sin^2(phi)) is the radius of curvature in the prime vertical.

2. Apply the datum shift (note the sign reversal since we are going FROM WGS84 TO Leigon):
```
X_Leigon = X_WGS84 + dx   = X + (-130)
Y_Leigon = Y_WGS84 + dy   = Y + 29
Z_Leigon = Z_WGS84 + dz   = Z + 364
```

3. Convert back to geodetic coordinates on the Clarke 1880 ellipsoid using the inverse formulas:
```
phi = arctan(Z_Leigon / sqrt(X_Leigon^2 + Y_Leigon^2) * (1 + e'^2 * N * sin(phi) / (N + h)))
lambda = arctan2(Y_Leigon, X_Leigon)
```
This requires iteration for phi.

4. The resulting (phi, lambda) on Clarke 1880 are then used as input to the Transverse Mercator projection.

**Inverse Transformation (Leigon to WGS84):** The same process in reverse, applying the shifts with opposite signs.

**Accuracy note:** The 3-parameter Helmert is an approximation that assumes the two ellipsoids are related by a simple translation with no rotation or scale difference between their axes. This is adequate for many surveying applications in Ghana (typically yielding sub-metre accuracy) but may not capture regional distortions. The calibration panel (Section 3.4) provides a way to model and correct these localised distortions.

---

### 4.4 4-Parameter Helmert Calibration (Affine Similarity)

The calibration feature solves for a **4-parameter Helmert (similarity) transformation** that relates observed grid coordinates to computed grid coordinates. This models scale, rotation, and translation differences between a local survey and the national grid.

**Transformation Equations:**
```
E'_i = a * E_i - b * N_i + c
N'_i = b * E_i + a * N_i + d
```

Where:
- (E_i, N_i) = observed/surveyed grid coordinates of point i
- (E'_i, N'_i) = computed grid coordinates of point i (derived from WGS84 via projection)
- a, b = rotation-scale parameters
- c, d = translation parameters (in metres)

**Derived quantities:**
```
Scale factor:    s = sqrt(a^2 + b^2)
Rotation angle:  theta = atan2(b, a)  (in radians, convert to degrees by multiplying by 180/pi)
Translation:     (c, d) in metres
```

**Least-Squares Solution:**

The system is overdetermined when more than 2 points are available. It is solved using the method of normal equations.

For n control points, we form the design matrix A and observation vector b:

```
A = | E_1  -N_1  1  0 |       b = | E'_1 |
    | N_1   E_1  0  1 |           | N'_1 |
    | E_2  -N_2  1  0 |           | E'_2 |
    | N_2   E_2  0  1 |           | N'_2 |
    | ...              |           | ...  |
    | E_n  -N_n  1  0 |           | E'_n |
    | N_n   E_n  0  1 |           | N'_n |
```

The normal equations are:
```
(A^T * A) * p = A^T * b
```
where p = [a, b, c, d]^T.

This 4x4 linear system is solved using **Gaussian elimination with partial pivoting**:
1. Forward elimination: For each column, find the row with the largest absolute value (partial pivoting), swap rows, eliminate entries below the pivot.
2. Back substitution: Solve for p starting from the last row upward.

**Residual Analysis:**

After computing the parameters, the residuals for each point are:
```
dE_i = (a * E_i - b * N_i + c) - E'_i
dN_i = (b * E_i + a * N_i + d) - N'_i
|d|_i = sqrt(dE_i^2 + dN_i^2)
```

**Root Mean Square (RMS) of residuals:**
```
RMS = sqrt( (1/n) * sum(|d|_i^2) )
```

A lower RMS indicates a better fit. Points with residuals significantly larger than the RMS may be outliers or errors in the survey data. For a well-fitted transformation with high-quality control points, RMS values below 0.1 m are typical.

**Minimum points:** The 4-parameter model requires at least 2 control points (producing 4 equations for 4 unknowns). With exactly 2 points, the system is exactly determined and residuals will be zero. With 3 or more points, the least-squares solution provides a best fit and the residuals become meaningful for quality assessment.

---

## 5. Default Parameters Reference

The following tables document every default value exposed in the Settings panel and used internally by the conversion engine.

### Ellipsoid Parameters

| Parameter | Value | Unit |
|---|---|---|
| Semi-major axis (a) | 6,378,249.145 | metres |
| Reciprocal flattening (1/f) | 293.466307656 | dimensionless |
| Ellipsoid name | Clarke 1880 (RGS) | - |
| proj4 identifier | `clrk80` | - |

### Ghana National Grid (GNG) Defaults

| Parameter | Field ID | Default Value | Notes |
|---|---|---|---|
| False Easting | set_gng_x0 | 274319.514 | metres |
| False Northing | set_gng_y0 | 0 | metres |
| Central Meridian | set_gng_lon0 | -1 | degrees (1W) |
| Origin Latitude | set_gng_lat0 | 4.6666666667 | degrees (4d40'N) |
| Scale Factor | set_gng_k | 0.99975 | dimensionless |
| Datum Shift | set_gng_towgs | -130,29,364 | dx,dy,dz in metres |

### Ghana Metre Grid (GMG) Defaults

| Parameter | Field ID | Default Value | Notes |
|---|---|---|---|
| False Easting | set_gmg_x0 | 1000000 | metres |
| False Northing | set_gmg_y0 | 0 | metres |
| Central Meridian | set_gmg_lon0 | -1 | degrees (1W) |
| Origin Latitude | set_gmg_lat0 | 4.6666666667 | degrees (4d40'N) |
| Scale Factor | set_gmg_k | 0.99975 | dimensionless |
| Datum Shift | set_gmg_towgs | -130,29,364 | dx,dy,dz in metres |

### Complete proj4 Definition Strings

**GNG:**
```
+proj=tmerc +lat_0=4.6666666667 +lon_0=-1 +k=0.99975 +x_0=274319.514 +y_0=0 +a=6378249.145 +rf=293.466307656 +towgs84=-130,29,364 +units=m +no_defs
```

**GMG:**
```
+proj=tmerc +lat_0=4.6666666667 +lon_0=-1 +k=0.99975 +x_0=1000000 +y_0=0 +a=6378249.145 +rf=293.466307656 +towgs84=-130,29,364 +units=m +no_defs
```

---

## 6. CSV Data Format

### Conversion Result Export

Conversion results are exported as CSV with two columns:

```csv
Label,Value
"Latitude (input)","5.60370000"
"Longitude (input)","-0.18700000"
"GNG Easting","752468.500"
"GNG Northing","620457.300"
```

### Calibration Point Export/Import

Calibration points use five columns:

```csv
Latitude,Longitude,Easting,Northing,GridType
5.60370000,-0.18700000,752468.500,620457.300,GNG
5.55100000,-0.22500000,748230.100,615890.700,GNG
5.61200000,-0.15800000,754100.200,621880.400,GMG
```

Rules for CSV import:
- The first row is treated as a header if it contains alphabetic characters; otherwise it is parsed as data.
- All five columns are required. Missing columns will cause the row to be skipped.
- The GridType column accepts `GNG` or `GMG` (case-insensitive). If blank or unrecognised, it defaults to `GNG`.
- Empty rows and rows with non-numeric latitude/longitude are silently skipped.
- A maximum of 50 rows can be imported (matching the UI limit).

---

## 7. REST API Reference

The Flask backend exposes the following JSON API endpoints. All endpoints return `Content-Type: application/json`.

### POST /api/convert

Single coordinate conversion. Accepts a JSON body with a `type` field that determines the conversion direction.

**WGS84 to Grid:**
```json
// Request
{
  "type": "wgs84_to_grid",
  "lat": 5.6037,
  "lon": -0.1870,
  "tgt_grid": "GNG"
}

// Response
{
  "status": "ok",
  "easting": 752468.5,
  "northing": 620457.3,
  "grid": "GNG",
  "lat": 5.6037,
  "lon": -0.187
}
```

**Grid to WGS84:**
```json
// Request
{
  "type": "grid_to_wgs84",
  "easting": 752468.5,
  "northing": 620457.3,
  "src_grid": "GNG"
}

// Response
{
  "status": "ok",
  "latitude": 5.60370000,
  "longitude": -0.18700000,
  "grid": "GNG",
  "easting": 752468.5,
  "northing": 620457.3
}
```

**Grid to Grid:**
```json
// Request
{
  "type": "grid_to_grid",
  "easting": 752468.5,
  "northing": 620457.3,
  "src_grid": "GNG",
  "tgt_grid": "GMG"
}

// Response
{
  "status": "ok",
  "src_grid": "GNG",
  "tgt_grid": "GMG",
  "src_easting": 752468.5,
  "src_northing": 620457.3,
  "tgt_easting": 1478148.986,
  "tgt_northing": 620457.300,
  "intermediate_lat": 5.60370000,
  "intermediate_lon": -0.18700000
}
```

### POST /api/batch

Batch conversion of multiple points in a single request.

```json
// Request
{
  "type": "wgs84_to_grid",
  "grid": "GNG",
  "points": [
    {"lat": 5.6037, "lon": -0.1870},
    {"lat": 5.5510, "lon": -0.2250}
  ]
}

// Response
{
  "status": "ok",
  "grid": "GNG",
  "count": 2,
  "results": [
    {"lat": 5.6037, "lon": -0.187, "easting": 752468.5, "northing": 620457.3},
    {"lat": 5.551, "lon": -0.225, "easting": 748230.1, "northing": 615890.7}
  ]
}
```

### POST /api/calibrate

4-parameter Helmert calibration from control points.

```json
// Request
{
  "points": [
    {"lat": 5.6037, "lon": -0.187, "easting": 752468.5, "northing": 620457.3, "grid": "GNG"},
    {"lat": 5.551, "lon": -0.225, "easting": 748230.1, "northing": 615890.7, "grid": "GNG"}
  ]
}

// Response
{
  "status": "ok",
  "points_used": 2,
  "parameters": {"a": 1.0000123456, "b": 0.0000234567, "c": 0.0123, "d": -0.0045},
  "scale": 1.00001234,
  "rotation_deg": 0.001345,
  "translation_x_m": 0.0123,
  "translation_y_m": -0.0045,
  "rms_residual_m": 0.0234,
  "residuals": [
    {"point": 1, "dE": 0.012, "dN": -0.008, "d": 0.014},
    {"point": 2, "dE": -0.005, "dN": 0.022, "d": 0.023}
  ]
}
```

### GET /api/crs

Returns the full CRS parameter sets for both GNG and GMG, including projection name, ellipsoid, datum, all numerical parameters, and the complete proj4 definition strings.

### GET /api/health

Returns `{"status": "ok", "service": "Geodetic Knife", "version": "2.0.0"}`.

---

## 8. Troubleshooting

| Problem | Cause | Solution |
|---|---|---|
| "Conversion error" toast | Invalid coordinates or CRS not initialised | Ensure latitude is between -90 and 90, longitude between -180 and 180. Click Apply Settings. |
| All conversions return 0,0 | Input fields contain non-numeric text | Clear the fields and re-enter numbers in decimal degrees. |
| 404 when loading the page | `index.html` not in same folder as `app.py` | Move `index.html` to the same directory as `app.py`. |
| "Singular matrix" in calibration | Control points are collinear or identical | Use at least 2 well-separated points. Check for duplicate coordinates. |
| Settings changes have no effect on API | Frontend and backend use independent CRS definitions | The Settings panel only affects browser-side proj4js conversions. Server API uses hardcoded values in `app.py`. |
| ModuleNotFoundError: flask/pyproj | Python dependencies not installed | Run `pip install flask pyproj` or `pip install -r requirements.txt`. |
| Port 5000 already in use | Another process using the port | Run on a different port: `python app.py` and modify the port in the last line, or kill the conflicting process. |
