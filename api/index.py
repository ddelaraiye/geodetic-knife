import json
import math
from flask import Flask, request, jsonify
from pyproj import CRS, Transformer

app = Flask(__name__)

# -- CONSTANTS --
GOLD_COAST_FOOT = 0.304799710181509
GMG_FALSE_EASTING = 900000 * GOLD_COAST_FOOT
GNG_FALSE_EASTING = 900000
GOLD_COAST_FOOT_INV = 1.0 / GOLD_COAST_FOOT

GMG_PROJ4 = (
    "+proj=tmerc +lat_0=4.66666666666667 +lon_0=-1 +k=0.99975 "
    "+x_0=274319.739163358 +y_0=0 "
    "+a=6378300 +rf=296 "
    "+towgs84=-199,32,322 "
    "+units=m +no_defs"
)

gmg_crs = CRS.from_proj4(GMG_PROJ4)
wgs84_crs = CRS.from_epsg(4326)
wgs84_to_gmg = Transformer.from_crs(wgs84_crs, gmg_crs, always_xy=True)
gmg_to_wgs84 = Transformer.from_crs(gmg_crs, wgs84_crs, always_xy=True)

ACCURACY_META = {
    "horizontal_accuracy_meters": "2.5",
    "method": "Molodensky 3-param",
    "grid_accuracy": "exact arithmetic conversion"
}

# -- CONVERSION HELPERS --
def wgs84_to_gmg_grid(lat, lon):
    e, n = wgs84_to_gmg.transform(lon, lat)
    return {"easting": e, "northing": n}

def wgs84_to_gng_grid(lat, lon):
    gmg = wgs84_to_gmg_grid(lat, lon)
    return gng_to_gmg_grid(gmg["easting"], gmg["northing"])

def gmg_to_wgs84_geo(easting, northing):
    lon, lat = gmg_to_wgs84.transform(easting, northing)
    return {"lat": lat, "lon": lon}

def gng_to_wgs84_geo(easting_ft, northing_ft):
    gmg = gng_to_gmg_grid(easting_ft, northing_ft)
    return gmg_to_wgs84_geo(gmg["easting"], gmg["northing"])

def gng_to_gmg_grid(easting_ft, northing_ft):
    raw_e = easting_ft - GNG_FALSE_EASTING
    return {"easting": raw_e * GOLD_COAST_FOOT + GMG_FALSE_EASTING, "northing": northing_ft * GOLD_COAST_FOOT}

def gmg_to_gng_grid(easting_m, northing_m):
    raw_e = easting_m - GMG_FALSE_EASTING
    return {"easting": raw_e * GOLD_COAST_FOOT_INV + GNG_FALSE_EASTING, "northing": northing_m * GOLD_COAST_FOOT_INV}

def build_full_result(gng, gmg, wgs84):
    return {
        "gng": gng,
        "gmg": gmg,
        "wgs84": wgs84,
        "accuracy": ACCURACY_META
    }

# -- API: SINGLE CONVERSION --
@app.route("/api/convert", methods=["POST"])
def convert():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400

    mode = data.get("mode")
    from_crs = data.get("from_crs", data.get("gridType", "GNG"))

    try:
        if mode == "WGS84_TO_GRID":
            lat = float(data["lat"])
            lon = float(data["lon"])
            gmg = wgs84_to_gmg_grid(lat, lon)
            gng = gmg_to_gmg_grid(gmg["easting"], gmg["northing"])
            return jsonify(build_full_result(gng, gmg, {"lat": lat, "lon": lon}))

        elif mode == "GNG_GMG":
            e = float(data["easting"])
            n = float(data["northing"])
            if from_crs == "GNG":
                gmg = gng_to_gmg_grid(e, n)
                gng = {"easting": e, "northing": n}
                wgs = gmg_to_wgs84_geo(gmg["easting"], gmg["northing"])
            else:
                gng = gmg_to_gng_grid(e, n)
                gmg = {"easting": e, "northing": n}
                wgs = gmg_to_wgs84_geo(e, n)
            return jsonify(build_full_result(gng, gmg, wgs))

        elif mode == "GRID_TO_WGS84":
            e = float(data["easting"])
            n = float(data["northing"])
            if from_crs == "GNG":
                wgs = gng_to_wgs84_geo(e, n)
                gmg = wgs84_to_gmg_grid(wgs["lat"], wgs["lon"])
                gng = {"easting": e, "northing": n}
            else:
                wgs = gmg_to_wgs84_geo(e, n)
                gng = gmg_to_gng_grid(e, n)
                gmg = {"easting": e, "northing": n}
            return jsonify(build_full_result(gng, gmg, wgs))

        return jsonify({"error": "Unknown mode: " + str(mode)}), 400

    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

# -- API: BATCH CONVERSION --
@app.route("/api/convert_batch", methods=["POST"])
def convert_batch():
    data = request.get_json()
    points = data.get("points", [])
    if not points:
        return jsonify({"error": "No points provided"}), 400

    results = []
    errors = []

    for i, pt in enumerate(points):
        try:
            mode = pt.get("mode")
            from_crs = pt.get("from_crs", pt.get("gridType", "GNG"))

            if mode == "WGS84_TO_GRID":
                lat = float(pt["lat"])
                lon = float(pt["lon"])
                gmg = wgs84_to_gmg_grid(lat, lon)
                gng = gmg_to_gmg_grid(gmg["easting"], gmg["northing"])
                results.append(build_full_result(gng, gmg, {"lat": lat, "lon": lon}))

            elif mode == "GNG_GMG":
                e = float(pt["easting"])
                n = float(pt["northing"])
                if from_crs == "GNG":
                    gmg_r = gng_to_gmg_grid(e, n)
                    gng_r = {"easting": e, "northing": n}
                    wgs = gmg_to_wgs84_geo(gmg_r["easting"], gmg_r["northing"])
                else:
                    gng_r = gmg_to_gng_grid(e, n)
                    gmg_r = {"easting": e, "northing": n}
                    wgs = gmg_to_wgs84_geo(e, n)
                results.append(build_full_result(gng_r, gmg_r, wgs))

            elif mode == "GRID_TO_WGS84":
                e = float(pt["easting"])
                n = float(pt["northing"])
                if from_crs == "GNG":
                    wgs = gng_to_wgs84_geo(e, n)
                    gmg_r = wgs84_to_gmg_grid(wgs["lat"], wgs["lon"])
                    gng_r = {"easting": e, "northing": n}
                else:
                    wgs = gmg_to_wgs84_geo(e, n)
                    gng_r = gmg_to_gng_grid(e, n)
                    gmg_r = {"easting": e, "northing": n}
                results.append(build_full_result(gng_r, gmg_r, wgs))

            else:
                errors.append({"row": i, "error": "Unknown mode: " + str(mode)})

        except Exception as exc:
            errors.append({"row": i, "error": str(exc)})

    return jsonify({"results": results, "errors": errors})

# -- API: ELEVATION --
@app.route("/api/elevation", methods=["GET"])
def elevation():
    try:
        lat = float(request.args.get("lat", 0))
        lon = float(request.args.get("lon", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid coordinates"}), 400

    try:
        import urllib.request
        url = f"https://api.open-elevation.com/v1/lookup?locations={lat},{lon}"
        req = urllib.request.Request(url, headers={"User-Agent": "GhanaGeodeticTool/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
        if data.get("results") and len(data["results"]) > 0:
            elev = data["results"][0].get("elevation")
            return jsonify({"elevation": elev, "source": "Open-Elevation SRTM"})
        return jsonify({"elevation": None, "source": "Open-Elevation"})
    except Exception as exc:
        return jsonify({"elevation": None, "error": str(exc)})

# -- API: REVERSE GEOCODE --
@app.route("/api/geocode", methods=["GET"])
def geocode():
    try:
        lat = float(request.args.get("lat", 0))
        lon = float(request.args.get("lon", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid coordinates"}), 400

    try:
        import urllib.request
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=14&addressdetails=1"
        req = urllib.request.Request(url, headers={"User-Agent": "GhanaGeodeticTool/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
        addr = data.get("address", {})
        return jsonify({
            "display_name": data.get("display_name", ""),
            "region": addr.get("state", ""),
            "district": addr.get("county", addr.get("city", addr.get("town", "")))
        })
    except Exception as exc:
        return jsonify({"display_name": "", "region": "", "district": "", "error": str(exc)})

# -- API: AZIMUTH & DISTANCE (Vincenty Inverse) --
@app.route("/api/azimuth_distance", methods=["POST"])
def azimuth_distance():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400

    try:
        lat1 = math.radians(float(data["lat1"]))
        lon1 = math.radians(float(data["lon1"]))
        lat2 = math.radians(float(data["lat2"]))
        lon2 = math.radians(float(data["lon2"]))
    except (KeyError, ValueError, TypeError):
        return jsonify({"error": "Provide lat1, lon1, lat2, lon2"}), 400

    try:
        a = 6378137.0
        f = 1 / 298.257223563
        b = a * (1 - f)

        L = lon2 - lon1
        U1 = math.atan((1 - f) * math.tan(lat1))
        U2 = math.atan((1 - f) * math.tan(lat2))
        sinU1, cosU1 = math.sin(U1), math.cos(U1)
        sinU2, cosU2 = math.sin(U2), math.cos(U2)

        lam = L
        for _ in range(1000):
            sin_lam = math.sin(lam)
            cos_lam = math.cos(lam)
            sin_sigma = math.sqrt(
                (cosU2 * sin_lam) ** 2 +
                (cosU1 * sinU2 - sinU1 * cosU2 * cos_lam) ** 2
            )
            if sin_sigma == 0:
                return jsonify({"distance_m": 0, "distance_ft": 0,
                               "initial_bearing_deg": 0, "final_bearing_deg": 0})
            cos_sigma = sinU1 * sinU2 + cosU1 * cosU2 * cos_lam
            sigma = math.atan2(sin_sigma, cos_sigma)
            sin_alpha = cosU1 * cosU2 * sin_lam / sin_sigma
            cos2_alpha = 1 - sin_alpha ** 2
            if cos2_alpha == 0:
                cos_2sigma_m = 0
            else:
                cos_2sigma_m = cos_sigma - 2 * sinU1 * sinU2 / cos2_alpha
            C = f / 16 * cos2_alpha * (4 + f * (4 - 3 * cos2_alpha))
            lam_prev = lam
            lam = L + (1 - C) * f * sin_alpha * (
                sigma + C * sin_sigma * (
                    cos_2sigma_m + C * cos_sigma * (-1 + 2 * cos_2sigma_m ** 2)
                )
            )
            if abs(lam - lam_prev) < 1e-12:
                break

        u2 = cos2_alpha * (a ** 2 - b ** 2) / (b ** 2)
        A_coeff = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
        B_coeff = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
        delta_sigma = B_coeff * sin_sigma * (
            cos_2sigma_m + B_coeff / 4 * (
                cos_sigma * (-1 + 2 * cos_2sigma_m ** 2) -
                B_coeff / 6 * cos_2sigma_m * (-3 + 4 * sin_sigma ** 2) * (-3 + 4 * cos_2sigma_m ** 2)
            )
        )
        dist_m = b * A_coeff * (sigma - delta_sigma)

        bearing1 = math.degrees(math.atan2(
            cosU2 * sin_lam,
            cosU1 * sinU2 - sinU1 * cosU2 * cos_lam
        ))
        bearing1 = (bearing1 + 360) % 360

        bearing2 = math.degrees(math.atan2(
            cosU1 * sin_lam,
            -sinU1 * cosU2 + cosU1 * sinU2 * cos_lam
        ))
        bearing2 = (bearing2 + 180 + 360) % 360

        dist_ft = dist_m / GOLD_COAST_FOOT

        return jsonify({
            "distance_m": dist_m,
            "distance_ft": dist_ft,
            "initial_bearing_deg": bearing1,
            "final_bearing_deg": bearing2
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

# -- LOCAL DEV --
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
