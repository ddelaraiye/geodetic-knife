"""
Geodetic Knife - Ghana Geodetic Transformation Tool
Flask backend with pyproj for coordinate transformations.
Serves the static frontend and provides REST API endpoints.
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from pyproj import Transformer, CRS

app = Flask(__name__, static_folder=".", static_url_path="")

# ---------------------------------------------------------------------------
# CRS Definitions - Ghana National Grid (GNG) & Ghana Metre Grid (GMG)
# Based on War Office Clarke 1880 ellipsoid, Transverse Mercator projection
# Leigon datum with 3-parameter Helmert shift to WGS84
# ---------------------------------------------------------------------------

ELLIPSOID = "Clarke 1880 (RGS)"
TOWGS84 = -130, 29, 364  # dx, dy, dz (metres)

# GNG: False Easting = 274 319.514 m, Origin = 4d40'N 1dW
GNG_DEF = (
    "+proj=tmerc +lat_0=4.6666666667 +lon_0=-1 +k=0.99975 "
    "+x_0=274319.514 +y_0=0 +ellps=clrk80 +towgs84=-130,29,364 "
    "+units=m +no_defs"
)

# GMG: False Easting = 1 000 000 m, same origin and datum
GMG_DEF = (
    "+proj=tmerc +lat_0=4.6666666667 +lon_0=-1 +k=0.99975 "
    "+x_0=1000000 +y_0=0 +ellps=clrk80 +towgs84=-130,29,364 "
    "+units=m +no_defs"
)

WGS84 = "EPSG:4326"

def get_transformer(from_crs, to_crs):
    """Create a pyproj Transformer, always_xy for lon/lat order."""
    return Transformer.from_crs(from_crs, to_crs, always_xy=True)


# ---------------------------------------------------------------------------
# API Routes - Coordinate Conversion Endpoints
# ---------------------------------------------------------------------------

@app.route("/api/convert", methods=["POST"])
def convert():
    """
    Convert coordinates between WGS84 and Ghana grids (GNG/GMG).
    Request body: { "type": "wgs84_to_grid" | "grid_to_wgs84" | "grid_to_grid",
                    "lat": float, "lon": float,
                    "easting": float, "northing": float,
                    "src_grid": "GNG"|"GMG", "tgt_grid": "GNG"|"GMG" }
    """
    data = request.get_json(force=True)
    conv_type = data.get("type", "")

    try:
        if conv_type == "wgs84_to_grid":
            lat = float(data["lat"])
            lon = float(data["lon"])
            tgt = data.get("tgt_grid", "GNG")
            tgt_crs = GNG_DEF if tgt.upper() == "GNG" else GMG_DEF
            t = get_transformer(WGS84, tgt_crs)
            easting, northing = t.transform(lon, lat)
            return jsonify({
                "status": "ok",
                "easting": round(easting, 4),
                "northing": round(northing, 4),
                "grid": tgt.upper(),
                "lat": lat,
                "lon": lon
            })

        elif conv_type == "grid_to_wgs84":
            easting = float(data["easting"])
            northing = float(data["northing"])
            src = data.get("src_grid", "GNG")
            src_crs = GNG_DEF if src.upper() == "GNG" else GMG_DEF
            t = get_transformer(src_crs, WGS84)
            lon, lat = t.transform(easting, northing)
            return jsonify({
                "status": "ok",
                "latitude": round(lat, 8),
                "longitude": round(lon, 8),
                "grid": src.upper(),
                "easting": easting,
                "northing": northing
            })

        elif conv_type == "grid_to_grid":
            easting = float(data["easting"])
            northing = float(data["northing"])
            src = data.get("src_grid", "GNG")
            tgt = data.get("tgt_grid", "GMG")
            if src.upper() == tgt.upper():
                return jsonify({"status": "error", "message": "Source and target grids must differ."}), 400
            src_crs = GNG_DEF if src.upper() == "GNG" else GMG_DEF
            tgt_crs = GNG_DEF if tgt.upper() == "GNG" else GMG_DEF
            # Grid -> WGS84 -> Grid
            t1 = get_transformer(src_crs, WGS84)
            t2 = get_transformer(WGS84, tgt_crs)
            lon, lat = t1.transform(easting, northing)
            dest_e, dest_n = t2.transform(lon, lat)
            return jsonify({
                "status": "ok",
                "src_grid": src.upper(),
                "tgt_grid": tgt.upper(),
                "src_easting": easting,
                "src_northing": northing,
                "tgt_easting": round(dest_e, 4),
                "tgt_northing": round(dest_n, 4),
                "intermediate_lat": round(lat, 8),
                "intermediate_lon": round(lon, 8)
            })

        else:
            return jsonify({"status": "error", "message": f"Unknown conversion type: {conv_type}"}), 400

    except (KeyError, ValueError) as e:
        return jsonify({"status": "error", "message": f"Invalid input: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/batch", methods=["POST"])
def batch_convert():
    """
    Batch convert multiple coordinates at once.
    Request body: { "type": "wgs84_to_grid" | "grid_to_wgs84",
                    "points": [{ "lat": float, "lon": float } | { "easting": float, "northing": float }],
                    "grid": "GNG"|"GMG" }
    """
    data = request.get_json(force=True)
    conv_type = data.get("type", "")
    points = data.get("points", [])
    grid = data.get("grid", "GNG").upper()
    grid_crs = GNG_DEF if grid == "GNG" else GMG_DEF

    if not points:
        return jsonify({"status": "error", "message": "No points provided."}), 400

    results = []
    try:
        if conv_type == "wgs84_to_grid":
            t = get_transformer(WGS84, grid_crs)
            for pt in points:
                lon, lat = float(pt["lon"]), float(pt["lat"])
                e, n = t.transform(lon, lat)
                results.append({"lat": lat, "lon": lon, "easting": round(e, 4), "northing": round(n, 4)})
        elif conv_type == "grid_to_wgs84":
            t = get_transformer(grid_crs, WGS84)
            for pt in points:
                e, n = float(pt["easting"]), float(pt["northing"])
                lon, lat = t.transform(e, n)
                results.append({"easting": e, "northing": n, "latitude": round(lat, 8), "longitude": round(lon, 8)})
        else:
            return jsonify({"status": "error", "message": f"Unknown batch type: {conv_type}"}), 400

        return jsonify({"status": "ok", "grid": grid, "count": len(results), "results": results})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/crs", methods=["GET"])
def get_crs_info():
    """Return CRS definitions for GNG and GMG."""
    return jsonify({
        "GNG": {
            "name": "Ghana National Grid",
            "projection": "Transverse Mercator",
            "ellipsoid": ELLIPSOID,
            "datum": "Leigon",
            "false_easting": 274319.514,
            "false_northing": 0,
            "central_meridian": -1.0,
            "origin_latitude": 4.6666666667,
            "scale_factor": 0.99975,
            "towgs84": list(TOWGS84),
            "proj4": GNG_DEF
        },
        "GMG": {
            "name": "Ghana Metre Grid",
            "projection": "Transverse Mercator",
            "ellipsoid": ELLIPSOID,
            "datum": "Leigon",
            "false_easting": 1000000,
            "false_northing": 0,
            "central_meridian": -1.0,
            "origin_latitude": 4.6666666667,
            "scale_factor": 0.99975,
            "towgs84": list(TOWGS84),
            "proj4": GMG_DEF
        }
    })


@app.route("/api/calibrate", methods=["POST"])
def calibrate():
    """
    Compute 4-parameter Helmert (affine) transformation from control points.
    Request body: { "points": [{ "lat", "lon", "easting", "northing", "grid" }] }
    Returns transformation parameters (a, b, c, d), scale, rotation, residuals.
    """
    data = request.get_json(force=True)
    points = data.get("points", [])

    if len(points) < 2:
        return jsonify({"status": "error", "message": "Minimum 2 control points required."}), 400

    try:
        # Build observation equations using pyproj
        A = []
        bx = []
        by = []
        for pt in points:
            lat, lon = float(pt["lat"]), float(pt["lon"])
            e, n = float(pt["easting"]), float(pt["northing"])
            grid = pt.get("grid", "GNG").upper()
            grid_crs = GNG_DEF if grid == "GNG" else GMG_DEF
            t = get_transformer(WGS84, grid_crs)
            xp, yp = t.transform(lon, lat)  # "true" grid coords from WGS84
            # Observed: (e, n), Computed: (xp, yp)
            # E' = a*E - b*N + c,  N' = b*E + a*N + d
            A.append([e, -n, 1, 0])
            A.append([n,  e, 0, 1])
            bx.append(xp)
            bx.append(yp)

        # Solve normal equations (A^T A) p = A^T b
        m = 4
        ATA = [[sum(A[k][i] * A[k][j] for k in range(len(A))) for j in range(m)] for i in range(m)]
        ATb = [sum(A[k][i] * bx[k] for k in range(len(A))) for i in range(m)]

        # Gaussian elimination with partial pivoting
        for col in range(m):
            max_row = max(range(col, m), key=lambda r: abs(ATA[r][col]))
            ATA[col], ATA[max_row] = ATA[max_row], ATA[col]
            ATb[col], ATb[max_row] = ATb[max_row], ATb[col]
            if abs(ATA[col][col]) < 1e-15:
                return jsonify({"status": "error", "message": "Singular matrix - check control points."}), 400
            for row in range(col + 1, m):
                factor = ATA[row][col] / ATA[col][col]
                for c in range(col, m):
                    ATA[row][c] -= factor * ATA[col][c]
                ATb[row] -= factor * ATb[col]

        # Back substitution
        params = [0] * m
        for i in range(m - 1, -1, -1):
            params[i] = ATb[i] - sum(ATA[i][j] * params[j] for j in range(i + 1, m))
            params[i] /= ATA[i][i]

        a, b, c, d = params
        scale = (a ** 2 + b ** 2) ** 0.5
        rotation = __import__("math").atan2(b, a) * 180 / __import__("math").pi

        # Compute residuals
        residuals = []
        for idx, pt in enumerate(points):
            lat, lon = float(pt["lat"]), float(pt["lon"])
            e, n = float(pt["easting"]), float(pt["northing"])
            grid = pt.get("grid", "GNG").upper()
            grid_crs = GNG_DEF if grid == "GNG" else GMG_DEF
            t = get_transformer(WGS84, grid_crs)
            xp, yp = t.transform(lon, lat)
            eh = a * e - b * n + c
            nh = b * e + a * n + d
            de, dn = eh - xp, nh - yp
            residuals.append({"point": idx + 1, "dE": round(de, 4), "dN": round(dn, 4), "d": round((de**2 + dn**2)**0.5, 4)})

        rms = (sum(r["d"] ** 2 for r in residuals) / len(residuals)) ** 0.5

        return jsonify({
            "status": "ok",
            "points_used": len(points),
            "parameters": {"a": round(a, 10), "b": round(b, 10), "c": round(c, 4), "d": round(d, 4)},
            "scale": round(scale, 8),
            "rotation_deg": round(rotation, 6),
            "translation_x_m": round(c, 4),
            "translation_y_m": round(d, 4),
            "rms_residual_m": round(rms, 4),
            "residuals": residuals
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    """API health check endpoint."""
    return jsonify({"status": "ok", "service": "Geodetic Knife", "version": "2.0.0"})


# ---------------------------------------------------------------------------
# Static file serving - serve index.html and other static assets
# ---------------------------------------------------------------------------

@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")


@app.route("/<path:path>")
def serve_static(path):
    file_path = os.path.join(".", path)
    if os.path.isfile(file_path):
        return send_from_directory(".", path)
    return send_from_directory(".", "index.html")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 50)
    print("  Geodetic Knife v2.0")
    print("  Ghana Geodetic Transformation Tool")
    print("=" * 50)
    print("  API endpoints:")
    print("    POST /api/convert     - Single coordinate conversion")
    print("    POST /api/batch       - Batch conversion")
    print("    POST /api/calibrate   - Helmert calibration")
    print("    GET  /api/crs         - CRS definitions")
    print("    GET  /api/health      - Health check")
    print()
    print("  Open http://127.0.0.1:5000 in your browser")
    print("=" * 50)
    app.run(host="127.0.0.1", port=5000, debug=True)
