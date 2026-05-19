# api/index.py — complete replacement with calibration support

import json
import math
from flask import Flask, request, jsonify
from pyproj import CRS, Transformer

app = Flask(__name__)

GOLD_COAST_FOOT = 0.304799710181509
GMG_FALSE_EASTING = 900000 * GOLD_COAST_FOOT
GNG_FALSE_EASTING = 900000
GOLD_COAST_FOOT_INV = 1.0 / GOLD_COAST_FOOT

WO_A = 6378300.0; WO_RF = 296.0; WO_F = 1.0/WO_RF
WO_B = WO_A*(1-WO_F); WO_E2 = 2*WO_F - WO_F**2

WGS84_A = 6378137.0; WGS84_F = 1.0/298.257223563
WGS84_B = WGS84_A*(1-WGS84_F); WGS84_E2 = 2*WGS84_F - WGS84_F**2

TM_LAT0_DEG = 4.0 + 39.0/60.0; TM_LON0_DEG = -1.0
TM_K0 = 0.99975; TM_FE = 274319.739163358

GMG_PROJ4 = ("+proj=tmerc +lat_0=4.66666666666667 +lon_0=-1 +k=0.99975 "
    "+x_0=274319.739163358 +y_0=0 +a=6378300 +rf=296 "
    "+towgs84=-199,32,322 +units=m +no_defs")

gmg_crs = CRS.from_proj4(GMG_PROJ4)
wgs84_crs = CRS.from_epsg(4326)
wgs84_to_gmg = Transformer.from_crs(wgs84_crs, gmg_crs, always_xy=True)
gmg_to_wgs84 = Transformer.from_crs(gmg_crs, wgs84_crs, always_xy=True)

ACCURACY_META = {"horizontal_accuracy_meters": "2.5",
    "method": "Molodensky 3-param", "grid_accuracy": "exact arithmetic conversion"}

def _get_transformers(cal=None):
    if cal and cal.get("towgs84"):
        p = ("+proj=tmerc +lat_0=4.66666666666667 +lon_0=-1 +k=0.99975 "
             "+x_0=274319.739163358 +y_0=0 +a=6378300 +rf=296 "
             "+towgs84="+str(cal["towgs84"])+" +units=m +no_defs")
        crs = CRS.from_proj4(p)
        return {"fwd": Transformer.from_crs(wgs84_crs, crs, always_xy=True),
                "inv": Transformer.from_crs(crs, wgs84_crs, always_xy=True)}
    return {"fwd": wgs84_to_gmg, "inv": gmg_to_wgs84}

def _cal(d):
    c = d.get("calibration")
    return c if c and isinstance(c, dict) and c.get("towgs84") else None

def wgs84_to_gmg_grid(lat, lon, cal=None):
    t = _get_transformers(cal); e, n = t["fwd"].transform(lon, lat)
    return {"easting": e, "northing": n}

def wgs84_to_gng_grid(lat, lon, cal=None):
    g = wgs84_to_gmg_grid(lat, lon, cal)
    return gng_to_gmg_grid(g["easting"], g["northing"])

def gmg_to_wgs84_geo(e, n, cal=None):
    t = _get_transformers(cal); lon, lat = t["inv"].transform(e, n)
    return {"lat": lat, "lon": lon}

def gng_to_wgs84_geo(ef, nf, cal=None):
    g = gng_to_gmg_grid(ef, nf)
    return gmg_to_wgs84_geo(g["easting"], g["northing"], cal)

def gng_to_gmg_grid(ef, nf):
    return {"easting": (ef-GNG_FALSE_EASTING)*GOLD_COAST_FOOT+GMG_FALSE_EASTING,
            "northing": nf*GOLD_COAST_FOOT}

def gmg_to_gng_grid(em, nm):
    return {"easting": (em-GMG_FALSE_EASTING)*GOLD_COAST_FOOT_INV+GNG_FALSE_EASTING,
            "northing": nm*GOLD_COAST_FOOT_INV}

def build_full_result(gng, gmg, wgs, cal=None):
    return {"gng": gng, "gmg": gmg, "wgs84": wgs, "accuracy": {
        "horizontal_accuracy_meters": "<0.5" if cal else "2.5",
        "method": "calibrated 7-param Helmert" if cal else "Molodensky 3-param",
        "grid_accuracy": "exact arithmetic conversion", "calibrated": cal is not None}}

@app.route("/api/convert", methods=["POST"])
def convert():
    data = request.get_json()
    if not data: return jsonify({"error": "No JSON body"}), 400
    mode = data.get("mode"); fc = data.get("from_crs", data.get("gridType", "GNG"))
    cal = _cal(data)
    try:
        if mode == "WGS84_TO_GRID":
            lat, lon = float(data["lat"]), float(data["lon"])
            g = wgs84_to_gmg_grid(lat, lon, cal)
            return jsonify(build_full_result(gmg_to_gng_grid(g["easting"], g["northing"]), g, {"lat": lat, "lon": lon}, cal))
        elif mode == "GNG_GMG":
            e, n = float(data["easting"]), float(data["northing"])
            if fc == "GNG":
                gm = gng_to_gmg_grid(e, n); w = gmg_to_wgs84_geo(gm["easting"], gm["northing"], cal)
                return jsonify(build_full_result({"easting": e, "northing": n}, gm, w, cal))
            else:
                gn = gmg_to_gng_grid(e, n); w = gmg_to_wgs84_geo(e, n, cal)
                return jsonify(build_full_result(gn, {"easting": e, "northing": n}, w, cal))
        elif mode == "GRID_TO_WGS84":
            e, n = float(data["easting"]), float(data["northing"])
            if fc == "GNG":
                w = gng_to_wgs84_geo(e, n, cal); g = wgs84_to_gmg_grid(w["lat"], w["lon"], cal)
                return jsonify(build_full_result({"easting": e, "northing": n}, g, w, cal))
            else:
                w = gmg_to_wgs84_geo(e, n, cal); g = gmg_to_gng_grid(e, n)
                return jsonify(build_full_result(g, {"easting": e, "northing": n}, w, cal))
        return jsonify({"error": "Unknown mode"}), 400
    except Exception as ex:
        return jsonify({"error": str(ex)}), 400

@app.route("/api/convert_batch", methods=["POST"])
def convert_batch():
    data = request.get_json(); pts = data.get("points", [])
    if not pts: return jsonify({"error": "No points"}), 400
    cal = _cal(data); results = []; errors = []
    for i, pt in enumerate(pts):
        try:
            m = pt.get("mode"); fc = pt.get("from_crs", pt.get("gridType", "GNG"))
            if m == "WGS84_TO_GRID":
                lat, lon = float(pt["lat"]), float(pt["lon"])
                g = wgs84_to_gmg_grid(lat, lon, cal)
                results.append(build_full_result(gmg_to_gng_grid(g["easting"], g["northing"]), g, {"lat": lat, "lon": lon}, cal))
            elif m == "GNG_GMG":
                e, n = float(pt["easting"]), float(pt["northing"])
                if fc == "GNG":
                    gm = gng_to_gmg_grid(e, n); w = gmg_to_wgs84_geo(gm["easting"], gm["northing"], cal)
                    results.append(build_full_result({"easting": e, "northing": n}, gm, w, cal))
                else:
                    gn = gmg_to_gng_grid(e, n); w = gmg_to_wgs84_geo(e, n, cal)
                    results.append(build_full_result(gn, {"easting": e, "northing": n}, w, cal))
            elif m == "GRID_TO_WGS84":
                e, n = float(pt["easting"]), float(pt["northing"])
                if fc == "GNG":
                    w = gng_to_wgs84_geo(e, n, cal); g = wgs84_to_gmg_grid(w["lat"], w["lon"], cal)
                    results.append(build_full_result({"easting": e, "northing": n}, g, w, cal))
                else:
                    w = gmg_to_wgs84_geo(e, n, cal); g = gmg_to_gng_grid(e, n)
                    results.append(build_full_result(g, {"easting": e, "northing": n}, w, cal))
            else:
                errors.append({"row": i, "error": "Unknown mode"})
        except Exception as ex:
            errors.append({"row": i, "error": str(ex)})
    return jsonify({"results": results, "errors": errors})

# ── HELMERT SOLVER ──

def _ll2ecef(la, lo, h, a, e2):
    lr, lor = math.radians(la), math.radians(lo)
    sl, cl = math.sin(lr), math.cos(lr)
    N = a/math.sqrt(1-e2*sl*sl)
    return (N+h)*cl*math.cos(lor), (N+h)*cl*math.sin(lor), (N*(1-e2)+h)*sl

def _tm_inv(E, Ni):
    a, e2 = WO_A, WO_E2; ep2 = e2/(1-e2)
    l0, lo0, k0, fe = math.radians(TM_LAT0_DEG), math.radians(TM_LON0_DEG), TM_K0, TM_FE
    E1 = E-fe; M1 = Ni/k0
    mu = M1/(a*(1-e2/4-3*e2*e2/64-5*e2**3/256))
    e1 = (1-math.sqrt(1-e2))/(1+math.sqrt(1-e2))
    e12,e13,e14 = e1*e1, e12*e1, e13*e1
    p1 = (mu+(3*e1/2-27*e13/32)*math.sin(2*mu)+(21*e12/16-55*e14/32)*math.sin(4*mu)
         +(151*e13/96)*math.sin(6*mu)+(1097*e14/512)*math.sin(8*mu))
    sp,cp,tp = math.sin(p1),math.cos(p1),math.tan(p1)
    N1 = a/math.sqrt(1-e2*sp*sp); T1=tp*tp; C1=ep2*cp*cp
    R1 = N1*(1-e2)/(1-e2*sp*sp); D = E1/(N1*k0)
    D2,D3,D4,D5,D6 = D*D, D2*D, D3*D, D4*D, D5*D
    lat = p1-(N1*tp/R1)*(D2/2-(5+3*T1+10*C1-4*C1*C1-9*ep2)*D4/24
         +(61+90*T1+298*C1+45*T1*T1-252*ep2-3*C1*C1)*D6/720)
    lon = lo0+(D-(1+2*T1+C1)*D3/6+(5-2*C1+28*T1-3*C1*C1+8*ep2+24*T1*T1)*D5/120)/cp
    return math.degrees(lat), math.degrees(lon)

def _minv(M):
    n = len(M)
    aug = [r[:]+[1.0 if i==j else 0.0 for j in range(n)] for i,r in enumerate(M)]
    for c in range(n):
        mr = max(range(c,n), key=lambda r: abs(aug[r][c]))
        aug[c], aug[mr] = aug[mr], aug[c]
        if abs(aug[c][c]) < 1e-14: raise ValueError("Singular matrix")
        piv = aug[c][c]
        for j in range(2*n): aug[c][j] /= piv
        for r in range(n):
            if r != c:
                f = aug[r][c]
                for j in range(2*n): aug[r][j] -= f*aug[c][j]
    return [r[n:] for r in aug]

def _mmul(A, B):
    return [[sum(A[i][k]*B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]

def _mT(A):
    return [[A[j][i] for j in range(len(A))] for i in range(len(A[0]))]

def solve_helmert(cps):
    n = len(cps)
    if n < 3: raise ValueError(f"Need min 3 points (have {n})")
    Ar, Lv = [], []
    for cp in cps:
        la,lo = float(cp["lat"]),float(cp["lon"]); h = float(cp.get("h",0))
        e,nv = float(cp["easting"]),float(cp["northing"]); tgt = cp.get("target","GNG")
        Xs,Ys,Zs = _ll2ecef(la,lo,h,WGS84_A,WGS84_E2)
        if tgt == "GNG":
            g = gng_to_gmg_grid(e,nv); em,nm = g["easting"],g["northing"]
        else: em,nm = e,nv
        la2,lo2 = _tm_inv(em,nm); Xt,Yt,Zt = _ll2ecef(la2,lo2,0,WO_A,WO_E2)
        Ar.append([1,0,0,0,-Zs,Ys,Xs]); Ar.append([0,1,0,Zs,0,-Xs,Ys]); Ar.append([0,0,1,-Ys,Xs,0,Zs])
        Lv.extend([Xt-Xs,Yt-Ys,Zt-Zs])
    AT=_mT(Ar); ATA=_mmul(AT,Ar); ATL=_mmul(AT,[[v] for v in Lv])
    x=_mmul(_minv(ATA),ATL)
    p = {"tx":x[0][0],"ty":x[1][0],"tz":x[2][0],"rx":x[3][0],"ry":x[4][0],"rz":x[5][0],"scale":x[6][0]}
    a2s = lambda r: r*180/math.pi*3600
    tw = "%f,%f,%f,%f,%f,%f,%f" % (p["tx"],p["ty"],p["tz"],a2s(p["rx"]),a2s(p["ry"]),a2s(p["rz"]),p["scale"]*1e6)
    res,se2,sn2 = [],0.0,0.0; cc = {"towgs84":tw}
    for i,cp in enumerate(cps):
        la,lo = float(cp["lat"]),float(cp["lon"]); e,nv = float(cp["easting"]),float(cp["northing"])
        tgt = cp.get("target","GNG"); gp = wgs84_to_gmg_grid(la,lo,cc); ep,np = gp["easting"],gp["northing"]
        if tgt=="GNG": g2=gng_to_gmg_grid(ep,np); ep,np = g2["easting"],g2["northing"]
        re,rn = ep-e, np-nv; rc = math.sqrt(re*re+rn*rn)
        res.append({"point":i+1,"lat":round(la,8),"lon":round(lo,8),
            "e_actual":round(e,4),"n_actual":round(nv,4),"e_predicted":round(ep,4),"n_predicted":round(np,4),
            "res_e":round(re,6),"res_n":round(rn,6),"res_combined":round(rc,6)})
        se2+=re*re; sn2+=rn*rn
    stats = {"num_points":n,"degrees_of_freedom":3*n-7,
        "rms_e":round(math.sqrt(se2/n),6),"rms_n":round(math.sqrt(sn2/n),6),
        "rms_combined":round(math.sqrt((se2+sn2)/(2*n)),6),
        "scale_factor":round(1+p["scale"],9),"scale_ppm":round(p["scale"]*1e6,4),"towgs84":tw}
    return p, res, stats

@app.route("/api/calibrate", methods=["POST"])
def calibrate():
    data = request.get_json()
    if not data: return jsonify({"error":"No JSON body"}),400
    pts = data.get("points",[]); tgt = data.get("target","GNG")
    if len(pts)<3: return jsonify({"error":f"Need min 3 points (have {len(pts)})"}),400
    if len(pts)>50: return jsonify({"error":"Max 50 points"}),400
    for i,pt in enumerate(pts):
        try: float(pt["lat"]);float(pt["lon"]);float(pt["easting"]);float(pt["northing"])
        except: return jsonify({"error":f"Point {i+1} invalid"}),400
    for pt in pts: pt["target"]=tgt
    try:
        p,res,st = solve_helmert(pts)
        return jsonify({"success":True,"params":p,"towgs84":st["towgs84"],"residuals":res,"statistics":st,"target":tgt})
    except ValueError as ex: return jsonify({"error":str(ex)}),400
    except Exception as ex: return jsonify({"error":f"Failed: {str(ex)}"}),500



@app.route("/api/calibration_status", methods=["GET"])
def calibration_status():
    return jsonify({"status":"available","method":"7-param Helmert","min_points":3,"max_points":50})
@app.route("/api/elevation", methods=["GET"])
def elevation():
    try: lat=float(request.args.get("lat",0)); lon=float(request.args.get("lon",0))
    except: return jsonify({"error":"Invalid coords"}),400
    try:
        import urllib.request
        url=f"https://api.open-elevation.com/v1/lookup?locations={lat},{lon}"
        req=urllib.request.Request(url,headers={"User-Agent":"GhanaGeodeticTool/1.0"})
        with urllib.request.urlopen(req,timeout=8) as resp:
            d=json.loads(resp.read().decode())
        if d.get("results"): return jsonify({"elevation":d["results"][0].get("elevation"),"source":"SRTM"})
        return jsonify({"elevation":None,"source":"Open-Elevation"})
    except Exception as ex: return jsonify({"elevation":None,"error":str(ex)})

@app.route("/api/geocode", methods=["GET"])
def geocode():
    try: lat=float(request.args.get("lat",0)); lon=float(request.args.get("lon",0))
    except: return jsonify({"error":"Invalid coords"}),400
    try:
        import urllib.request
        url=f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=14&addressdetails=1"
        req=urllib.request.Request(url,headers={"User-Agent":"GhanaGeodeticTool/1.0"})
        with urllib.request.urlopen(req,timeout=8) as resp:
            d=json.loads(resp.read().decode())
        a=d.get("address",{})
        return jsonify({"display_name":d.get("display_name",""),"region":a.get("state",""),
            "district":a.get("county",a.get("city",a.get("town","")))})
    except Exception as ex: return jsonify({"display_name":"","region":"","district":"","error":str(ex)})

@app.route("/api/azimuth_distance", methods=["POST"])
def azimuth_distance():
    data=request.get_json()
    if not data: return jsonify({"error":"No JSON body"}),400
    try:
        la1,lo1=math.radians(float(data["lat1"])),math.radians(float(data["lon1"]))
        la2,lo2=math.radians(float(data["lat2"])),math.radians(float(data["lon2"]))
    except: return jsonify({"error":"Need lat1,lon1,lat2,lon2"}),400
    try:
        a=6378137.0;f=1/298.257223563;b=a*(1-f);L=lo2-lo1
        U1=math.atan((1-f)*math.tan(la1));U2=math.atan((1-f)*math.tan(la2))
        sU1,cU1,sU2,cU2=math.sin(U1),math.cos(U1),math.sin(U2),math.cos(U2)
        lam=L
        for _ in range(1000):
            sl,cl=math.sin(lam),math.cos(lam)
            ss=math.sqrt((cU2*sl)**2+(cU1*sU2-sU1*cU2*cl)**2)
            if ss==0: return jsonify({"distance_m":0,"distance_ft":0,"initial_bearing_deg":0,"final_bearing_deg":0})
            cs=sU1*sU2+cU1*cU2*cl;sig=math.atan2(ss,cs);sa=cU1*cU2*sl/ss;c2a=1-sa**2
            c2sm=0 if c2a==0 else cs-2*sU1*sU2/c2a;C=f/16*c2a*(4+f*(4-3*c2a));lp=lam
            lam=L+(1-C)*f*sa*(sig+C*ss*(c2sm+C*cs*(-1+2*c2sm**2)))
            if abs(lam-lp)<1e-12: break
        u2=c2a*(a**2-b**2)/b**2;Ac=1+u2/16384*(4096+u2*(-768+u2*(320-175*u2)))
        Bc=u2/1024*(256+u2*(-128+u2*(74-47*u2)))
        ds=Bc*ss*(c2sm+Bc/4*(cs*(-1+2*c2sm**2)-Bc/6*c2sm*(-3+4*ss**2)*(-3+4*c2sm**2)))
        dm=b*Ac*(sig-ds);b1=math.degrees(math.atan2(cU2*sl,cU1*sU2-sU1*cU2*cl))%360
        b2=(math.degrees(math.atan2(cU1*sl,-sU1*cU2+cU1*sU2*cl))+180)%360
        return jsonify({"distance_m":dm,"distance_ft":dm/GOLD_COAST_FOOT,"initial_bearing_deg":b1,"final_bearing_deg":b2})
    except Exception as ex: return jsonify({"error":str(ex)}),400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)