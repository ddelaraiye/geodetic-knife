#!/usr/bin/env python3
"""fix_cal_v2.py - Polished calibration UI with balance scale"""
import os
PROJECT = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(PROJECT, 'public', 'index.html')
API  = os.path.join(PROJECT, 'api', 'index.py')
print("Geodetic Knife - Calibration UI v2")
print("=" * 42)
with open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()
fixed = 0

# --- Injection 1: Polished CSS ---
if '.cp-table' not in html:
    css = """
/* ═══════ CALIBRATION MODULE ═══════ */
#calContainer{display:none;padding:0}
#calContainer.active{display:block}
.cal-hero{background:linear-gradient(135deg,var(--card) 0%,#1a2a1a 100%);border-radius:12px;padding:24px;margin-bottom:16px;text-align:center;position:relative;overflow:hidden;border:1px solid var(--border)}
.cal-hero::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#3a6b3a,#5A8A5A,#7ab87a,#5A8A5A,#3a6b3a)}
.cal-hero h3{margin:0 0 4px;font-size:18px;font-weight:700;color:#cde6cd;letter-spacing:0.5px}
.cal-hero .sub{font-size:12px;color:var(--muted);margin:0 0 16px}
/* Balance Scale SVG */
.cal-scale-wrap{display:flex;justify-content:center;margin-bottom:16px}
.cal-scale-wrap svg{width:120px;height:70px;filter:drop-shadow(0 2px 6px rgba(0,0,0,0.3))}
.cal-scale-wrap .pan-left,.cal-scale-wrap .pan-right{animation:cal-swing 3s ease-in-out infinite alternate}
@keyframes cal-swing{0%{transform:rotate(-2deg)}100%{transform:rotate(2deg)}}
.cal-scale-labels{display:flex;justify-content:space-around;max-width:220px;margin:0 auto}
.cal-scale-labels span{font-size:10px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:1px}
.cal-status-row{display:flex;align-items:center;justify-content:center;gap:8px;margin-top:12px}
.cal-status{display:inline-flex;align-items:center;gap:5px;padding:4px 14px;border-radius:20px;font-size:12px;font-weight:600}
.cal-status .dot{width:7px;height:7px;border-radius:50%}
.cal-status.inactive{background:#2a2a1a;color:#aa5}
.cal-status.inactive .dot{background:#aa5}
.cal-status.active{background:#1a3a1a;color:#5f5}
.cal-status.active .dot{background:#5f5;box-shadow:0 0 6px #5f5}
/* Target selector */
.cal-target-row{display:flex;align-items:center;justify-content:center;gap:10px;margin:10px 0 0;font-size:13px;color:var(--fg)}
.cal-target-row select{background:var(--bg);color:var(--fg);border:1px solid var(--border);padding:5px 10px;border-radius:6px;font-size:12px;cursor:pointer}
/* Sections */
.cal-card{background:var(--card);border-radius:10px;padding:14px;margin-bottom:14px;border:1px solid var(--border)}
.cal-card h4{margin:0 0 10px;font-size:13px;font-weight:700;color:#8ab88a;display:flex;align-items:center;gap:6px}
.cal-card h4 .icon{font-size:15px}
/* Control point table */
.cp-table-wrap{overflow-x:auto;border-radius:6px;border:1px solid var(--border)}
.cp-table{width:100%;border-collapse:collapse;font-size:12px}
.cp-table th{background:#1a2a1a;color:#8ab88a;padding:7px 5px;font-weight:600;text-align:center;white-space:nowrap;font-size:11px;text-transform:uppercase;letter-spacing:0.5px}
.cp-table td{padding:4px 3px;text-align:center;border-top:1px solid var(--border)}
.cp-table tr:nth-child(even) td{background:rgba(255,255,255,0.015)}
.cp-table input{width:100%;min-width:65px;background:var(--bg);color:var(--fg);border:1px solid var(--border);padding:5px 6px;border-radius:5px;font-size:12px;text-align:center;transition:border-color .2s}
.cp-table input:focus{border-color:#5A8A5A;outline:none}
.cp-table .rm-btn{background:transparent;color:#855;border:1px solid #855;padding:3px 8px;border-radius:5px;cursor:pointer;font-size:12px;transition:all .2s}
.cp-table .rm-btn:hover{background:#5a2020;color:#faa;border-color:#733}
/* Buttons */
.cal-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.cal-btn{padding:9px 18px;border:none;border-radius:8px;cursor:pointer;font-size:12px;font-weight:600;transition:all .2s;display:inline-flex;align-items:center;gap:6px;letter-spacing:0.3px}
.cal-btn.primary{background:linear-gradient(135deg,#3a6b3a,#5A8A5A);color:#fff;box-shadow:0 2px 8px rgba(90,138,90,0.3)}
.cal-btn.primary:hover{box-shadow:0 4px 14px rgba(90,138,90,0.5);transform:translateY(-1px)}
.cal-btn.secondary{background:var(--border);color:var(--fg)}
.cal-btn.secondary:hover{background:#3a3a3a;transform:translateY(-1px)}
.cal-btn.danger{background:#3a1a1a;color:#e88;border:1px solid #633}
.cal-btn.danger:hover{background:#5a2020;transform:translateY(-1px)}
/* Results area */
.cal-results{display:none;margin-top:14px}
.cal-results.visible{display:block}
.cal-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:14px}
.cal-stat{background:linear-gradient(135deg,var(--card),#1a2a1a);border:1px solid var(--border);border-radius:10px;padding:14px 10px;text-align:center}
.cal-stat .val{font-size:20px;font-weight:800;color:#5A8A5A}
.cal-stat .val.good{color:#5f5}
.cal-stat .val.warn{color:#ee5}
.cal-stat .val.bad{color:#e55}
.cal-stat .lbl{font-size:10px;color:var(--muted);margin-top:4px;text-transform:uppercase;letter-spacing:0.5px}
.cal-params{overflow-x:auto}
.cal-params table{width:100%;border-collapse:collapse;font-size:12px}
.cal-params th{background:#1a2a1a;color:#8ab88a;padding:6px 10px;text-align:center;font-size:11px;text-transform:uppercase;letter-spacing:0.5px;border:1px solid var(--border)}
.cal-params td{padding:6px 10px;text-align:center;border:1px solid var(--border);font-family:'Courier New',monospace;font-size:12px}
.cal-residuals{overflow-x:auto}
.cal-residuals table{width:100%;border-collapse:collapse;font-size:11px}
.cal-residuals th{background:#1a2a1a;color:#8ab88a;padding:5px 6px;text-align:center;font-size:10px;text-transform:uppercase;letter-spacing:0.5px;border:1px solid var(--border);white-space:nowrap}
.cal-residuals td{padding:4px 6px;text-align:center;border:1px solid var(--border);white-space:nowrap}
.cal-residuals .good{color:#5f5;font-weight:600}
.cal-residuals .warn{color:#ee5;font-weight:600}
.cal-residuals .bad{color:#e55;font-weight:600}
@media(max-width:600px){
  .cal-stats{grid-template-columns:repeat(2,1fr)}
  .cal-hero{padding:16px}
  .cal-btn{padding:8px 12px;font-size:11px}
}
"""
    html = html.replace('</style>', css + '</style>', 1)
    fixed += 1; print("[+] Injected polished calibration CSS")
else:
    print("[=] CSS already present")

# --- Injection 2: Tab button ---
if "switchTab('calibration')" not in html:
    tab_html = '    <button class="tab-btn" onclick="switchTab(\'calibration\')">&#9878; Calibrate</button>\n'
    idx = html.rfind('class="tab-btn"')
    if idx > 0:
        end = html.find('</button>', idx) + len('</button>')
        html = html[:end] + '\n' + tab_html + html[end:]
        fixed += 1; print("[+] Injected calibration tab button")
    else: print("[!] WARNING: Could not find tab button anchor")
else: print("[=] Tab button already present")

# --- Injection 3: HTML container ---
if 'id="calContainer"' not in html:
    container = """
<div id="calContainer" class="panel">
  <div class="cal-hero">
    <h3>&#9878; Local Calibration</h3>
    <div class="sub">7-Parameter Helmert Transformation &bull; Least-Squares Solver</div>
    <div class="cal-scale-wrap">
      <svg viewBox="0 0 120 70" fill="none" xmlns="http://www.w3.org/2000/svg">
        <line x1="60" y1="5" x2="60" y2="35" stroke="#5A8A5A" stroke-width="2"/>
        <polygon points="56,35 64,35 60,30" fill="#5A8A5A"/>
        <rect x="54" y="34" width="12" height="4" rx="1" fill="#5A8A5A"/>
        <g class="pan-left">
          <line x1="15" y1="28" x2="105" y2="28" stroke="#8ab88a" stroke-width="1.5"/>
          <line x1="20" y1="28" x2="20" y2="45" stroke="#8ab88a" stroke-width="1"/>
          <line x1="10" y1="45" x2="30" y2="45" stroke="#8ab88a" stroke-width="1.5" stroke-linecap="round"/>
          <line x1="10" y1="45" x2="15" y2="50" stroke="#8ab88a" stroke-width="1" stroke-linecap="round"/>
          <line x1="30" y1="45" x2="25" y2="50" stroke="#8ab88a" stroke-width="1" stroke-linecap="round"/>
        </g>
        <g class="pan-right">
          <line x1="100" y1="28" x2="100" y2="45" stroke="#8ab88a" stroke-width="1"/>
          <line x1="90" y1="45" x2="110" y2="45" stroke="#8ab88a" stroke-width="1.5" stroke-linecap="round"/>
          <line x1="90" y1="45" x2="95" y2="50" stroke="#8ab88a" stroke-width="1" stroke-linecap="round"/>
          <line x1="110" y1="45" x2="105" y2="50" stroke="#8ab88a" stroke-width="1" stroke-linecap="round"/>
        </g>
        <rect x="52" y="4" width="16" height="3" rx="1.5" fill="#8ab88a"/>
      </svg>
    </div>
    <div class="cal-scale-labels">
      <span>WGS 84</span>
      <span style="color:#5A8A5A;font-size:11px">&#8644;</span>
      <span>GNG / GMG</span>
    </div>
    <div class="cal-status-row">
      <span style="font-size:12px;color:var(--muted)">Status:</span>
      <span id="calStatusBadge" class="cal-status inactive"><span class="dot"></span>Not calibrated</span>
    </div>
    <div class="cal-target-row">
      <label>Target Grid:</label>
      <select id="calTarget">
        <option value="GNG" selected>GNG (Gold Coast Feet)</option>
        <option value="GMG">GMG (Ghana Metre Grid)</option>
      </select>
    </div>
  </div>
  <div class="cal-card">
    <h4><span class="icon">&#128203;</span> Control Points <span style="font-weight:400;color:var(--muted);font-size:11px">&mdash; min 3, recommended 5&ndash;10+</span></h4>
    <div class="cp-table-wrap">
      <table class="cp-table" id="cpTable">
        <thead><tr><th>#</th><th>Latitude</th><th>Longitude</th><th>H (m)</th><th>Easting</th><th>Northing</th><th></th></tr></thead>
        <tbody id="cpBody"></tbody>
      </table>
    </div>
    <div class="cal-actions">
      <button class="cal-btn secondary" onclick="addCP()">+ Add Point</button>
      <button class="cal-btn secondary" onclick="loadSampleCP()">&#128197; Load Sample</button>
      <button class="cal-btn secondary" onclick="loadCPFile()">&#128196; Load CSV</button>
      <input type="file" id="cpFileInput" accept=".csv,.txt,.tsv" style="display:none" onchange="handleCPFile(event)">
    </div>
  </div>
  <div class="cal-actions" style="justify-content:center;padding:4px 0">
    <button class="cal-btn primary" onclick="doCalibrate()">&#128295; Run Calibration</button>
    <button class="cal-btn secondary" onclick="applyCal()">&#9989; Apply</button>
    <button class="cal-btn danger" onclick="clearCal()">&#128465; Clear</button>
    <button class="cal-btn secondary" onclick="exportCal()">&#128229; Export</button>
  </div>
  <div id="calResults" class="cal-results">
    <div class="cal-card"><h4><span class="icon">&#128200;</span> Statistics</h4><div class="cal-stats" id="calStats"></div></div>
    <div class="cal-card"><h4><span class="icon">&#128290;</span> 7-Parameter Helmert Coefficients</h4><div class="cal-params" id="calParams"></div></div>
    <div class="cal-card"><h4><span class="icon">&#128202;</span> Residual Analysis</h4><div class="cal-residuals" id="calResiduals"></div></div>
  </div>
</div>
"""
    html = html.replace('<script>', container + '\n<script>', 1)
    fixed += 1; print("[+] Injected calibration panel HTML")
else: print("[=] Container already present")

# --- Injection 4: JavaScript ---
if 'function doCalibrate()' not in html:
    js = """
/* ═══════ CALIBRATION ENGINE ═══════ */
var calState = {towgs84:null, params:null, stats:null};
(function initCal(){
  var saved = localStorage.getItem('geodetic_cal');
  if(saved){
    try { calState = JSON.parse(saved); updateCalBadge(); patchFetch(); }
    catch(e){ localStorage.removeItem('geodetic_cal'); }
  }
})();
function updateCalBadge(){
  var b = document.getElementById('calStatusBadge');
  if(!b) return;
  if(calState && calState.towgs84){
    b.className = 'cal-status active';
    var rms = calState.stats ? calState.stats.rms_combined : '?';
    b.innerHTML = '<span class="dot"></span>Active &mdash; ' + rms + ' m RMS';
  } else {
    b.className = 'cal-status inactive';
    b.innerHTML = '<span class="dot"></span>Not calibrated';
  }
}
var cpCounter = 0;
function addCP(lat, lon, h, e, n){
  cpCounter++;
  var tr = document.createElement('tr');
  tr.innerHTML = '<td>' + cpCounter + '</td>'
    + '<td><input type="text" placeholder="5.6037" value="' + (lat||'') + '" class="cp-lat"></td>'
    + '<td><input type="text" placeholder="-0.1870" value="' + (lon||'') + '" class="cp-lon"></td>'
    + '<td><input type="text" placeholder="0" value="' + (h||'') + '" class="cp-h"></td>'
    + '<td><input type="text" placeholder="easting" value="' + (e||'') + '" class="cp-e"></td>'
    + '<td><input type="text" placeholder="northing" value="' + (n||'') + '" class="cp-n"></td>'
    + '<td><button class="rm-btn" onclick="rmCP(this)">&#10005;</button></td>';
  document.getElementById('cpBody').appendChild(tr);
}
function rmCP(btn){ btn.closest('tr').remove(); }
function loadSampleCP(){
  var pts = [
    [5.6037, -0.1870, 0, 710232.456, 620345.789],
    [5.5512, -0.2234, 0, 706891.123, 614567.234],
    [5.6289, -0.0912, 0, 715678.901, 627890.456],
    [5.5890, -0.3456, 0, 702456.789, 611234.567],
    [5.6501, -0.1543, 0, 712345.678, 625678.123]
  ];
  document.getElementById('cpBody').innerHTML = '';
  cpCounter = 0;
  pts.forEach(function(p){ addCP(p[0], p[1], p[2], p[3], p[4]); });
}
function loadCPFile(){ document.getElementById('cpFileInput').click(); }
function handleCPFile(ev){
  var file = ev.target.files[0];
  if(!file) return;
  var reader = new FileReader();
  reader.onload = function(e){
    var lines = e.target.result.split('\\n');
    var delim = lines[0].indexOf('\\t') > -1 ? '\\t' : ',';
    document.getElementById('cpBody').innerHTML = '';
    cpCounter = 0;
    lines.forEach(function(line){
      var cols = line.trim().split(delim).map(function(s){ return s.trim(); });
      if(cols.length >= 4 && !isNaN(parseFloat(cols[0])) && !isNaN(parseFloat(cols[1])))
        addCP(cols[0], cols[1], cols[2] || '0', cols[3], cols[4] || '');
    });
  };
  reader.readAsText(file); ev.target.value = '';
}
function doCalibrate(){
  var rows = document.querySelectorAll('#cpBody tr');
  if(rows.length < 3){ alert('Need at least 3 control points'); return; }
  var pts = [];
  rows.forEach(function(r){
    var lat=r.querySelector('.cp-lat').value, lon=r.querySelector('.cp-lon').value;
    var h=r.querySelector('.cp-h').value, e=r.querySelector('.cp-e').value, n=r.querySelector('.cp-n').value;
    if(lat && lon && e && n && !isNaN(parseFloat(lat)))
      pts.push({lat:parseFloat(lat),lon:parseFloat(lon),h:parseFloat(h)||0,easting:parseFloat(e),northing:parseFloat(n)});
  });
  if(pts.length < 3){ alert('Need at least 3 valid control points'); return; }
  var tgt = document.getElementById('calTarget').value;
  fetch('/api/calibrate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({points:pts,target:tgt})})
    .then(function(r){return r.json();})
    .then(function(d){
      if(d.error){ alert('Calibration error: ' + d.error); return; }
      calState = {towgs84:d.towgs84, params:d.params, stats:d.statistics};
      showCalResults(d);
    }).catch(function(e){ alert('Network error: ' + e.message); });
}
function showCalResults(d){
  document.getElementById('calResults').classList.add('visible');
  var s = d.statistics;
  var rmsCls = s.rms_combined < 0.1 ? 'good' : s.rms_combined < 0.5 ? 'warn' : 'bad';
  document.getElementById('calStats').innerHTML =
    '<div class="cal-stat"><div class="val">' + s.num_points + '</div><div class="lbl">Points</div></div>'
    + '<div class="cal-stat"><div class="val ' + rmsCls + '">' + s.rms_combined.toFixed(4) + '</div><div class="lbl">RMS Combined (m)</div></div>'
    + '<div class="cal-stat"><div class="val">' + s.rms_e.toFixed(4) + '</div><div class="lbl">RMS Easting (m)</div></div>'
    + '<div class="cal-stat"><div class="val">' + s.rms_n.toFixed(4) + '</div><div class="lbl">RMS Northing (m)</div></div>'
    + '<div class="cal-stat"><div class="val">' + s.scale_ppm.toFixed(2) + '</div><div class="lbl">Scale (ppm)</div></div>'
    + '<div class="cal-stat"><div class="val">' + s.degrees_of_freedom + '</div><div class="lbl">DoF</div></div>';
  var p = d.params;
  var a2s = function(r){ return (r*180/Math.PI*3600).toFixed(4); };
  document.getElementById('calParams').innerHTML =
    '<table><tr><th>Parameter</th><th>Value</th><th>Unit</th></tr>'
    + '<tr><td>TX</td><td>' + p.tx.toFixed(4) + '</td><td>metres</td></tr>'
    + '<tr><td>TY</td><td>' + p.ty.toFixed(4) + '</td><td>metres</td></tr>'
    + '<tr><td>TZ</td><td>' + p.tz.toFixed(4) + '</td><td>metres</td></tr>'
    + '<tr><td>RX</td><td>' + a2s(p.rx) + '</td><td>arc-seconds</td></tr>'
    + '<tr><td>RY</td><td>' + a2s(p.ry) + '</td><td>arc-seconds</td></tr>'
    + '<tr><td>RZ</td><td>' + a2s(p.rz) + '</td><td>arc-seconds</td></tr>'
    + '<tr><td>Scale</td><td>' + (p.scale*1e6).toFixed(4) + '</td><td>ppm</td></tr></table>';
  var rh = '<table><tr><th>#</th><th>Lat</th><th>Lon</th><th>E Act</th><th>N Act</th><th>E Pred</th><th>N Pred</th><th>dE</th><th>dN</th><th>d(m)</th></tr>';
  d.residuals.forEach(function(r){
    var rc = r.res_combined, cls = rc < 0.1 ? 'good' : rc < 0.5 ? 'warn' : 'bad';
    rh += '<tr><td>' + r.point + '</td><td>' + r.lat + '</td><td>' + r.lon + '</td>'
      + '<td>' + r.e_actual + '</td><td>' + r.n_actual + '</td>'
      + '<td>' + r.e_predicted + '</td><td>' + r.n_predicted + '</td>'
      + '<td class="' + cls + '">' + r.res_e + '</td>'
      + '<td class="' + cls + '">' + r.res_n + '</td>'
      + '<td class="' + cls + '">' + r.res_combined + '</td></tr>';
  });
  rh += '</table>';
  document.getElementById('calResiduals').innerHTML = rh;
}
function applyCal(){
  if(!calState || !calState.towgs84){ alert('Run calibration first.'); return; }
  localStorage.setItem('geodetic_cal', JSON.stringify(calState));
  patchFetch(); updateCalBadge();
  alert('Calibration applied! Conversions now use 7-param Helmert.\\nRMS: ' + calState.stats.rms_combined.toFixed(4) + ' m');
}
function clearCal(){
  if(!confirm('Clear calibration? Reverts to Molodensky 3-param.')) return;
  calState = {towgs84:null, params:null, stats:null};
  localStorage.removeItem('geodetic_cal');
  updateCalBadge();
  document.getElementById('calResults').classList.remove('visible');
  alert('Calibration cleared.');
}
function exportCal(){
  if(!calState || !calState.stats){ alert('No results to export'); return; }
  var s = calState.stats, p = calState.params;
  var a2s = function(r){ return (r*180/Math.PI*3600).toFixed(4); };
  var txt = 'Geodetic Knife - Calibration Report\\n====================================\\n\\n'
    + 'Statistics:\\n  Points: ' + s.num_points + '\\n  RMS E: ' + s.rms_e + ' m\\n  RMS N: ' + s.rms_n + ' m\\n'
    + '  RMS Combined: ' + s.rms_combined + ' m\\n  Scale: ' + s.scale_ppm + ' ppm\\n\\n'
    + 'Parameters:\\n  TX: ' + p.tx.toFixed(4) + ' m\\n  TY: ' + p.ty.toFixed(4) + ' m\\n  TZ: ' + p.tz.toFixed(4) + ' m\\n'
    + '  RX: ' + a2s(p.rx) + '"\\n  RY: ' + a2s(p.ry) + '"\\n  RZ: ' + a2s(p.rz) + '"\\n'
    + '  Scale: ' + (p.scale*1e6).toFixed(4) + ' ppm\\n\\nPROJ towgs84:\\n  ' + s.towgs84 + '\\n';
  var blob = new Blob([txt], {type:'text/plain'});
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = 'calibration_report.txt'; a.click();
}
function patchFetch(){
  if(window._origFetch) return;
  window._origFetch = window.fetch;
  window.fetch = function(url, opts){
    if(calState && calState.towgs84 && opts && opts.body){
      try {
        var parsed = JSON.parse(opts.body);
        if(parsed.mode || (parsed.points && parsed.points.length)){
          parsed.calibration = {towgs84: calState.towgs84};
          opts.body = JSON.stringify(parsed);
        }
      } catch(e){}
    }
    return window._origFetch.call(this, url, opts);
  };
  if(!window._origXHROpen){
    var origOpen = XMLHttpRequest.prototype.open, origSend = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.open = function(method, url){ this._calUrl = url; return origOpen.apply(this, arguments); };
    XMLHttpRequest.prototype.send = function(body){
      if(calState && calState.towgs84 && body && this._calUrl && this._calUrl.indexOf('/api/') > -1){
        try {
          var parsed = JSON.parse(body);
          if(parsed.mode || (parsed.points && parsed.points.length)){
            parsed.calibration = {towgs84: calState.towgs84}; body = JSON.stringify(parsed);
          }
        } catch(e){}
      }
      return origSend.call(this, body);
    };
    window._origXHROpen = true;
  }
}
var _origSwitchTab = typeof switchTab !== 'undefined' ? switchTab : function(){};
window.switchTab = function(tab){
  document.querySelectorAll('.tab-btn').forEach(function(btn){
    var oc = btn.getAttribute('onclick') || '';
    btn.classList.toggle('active', oc.indexOf("'" + tab + "'") > -1);
  });
  var cal = document.getElementById('calContainer');
  if(tab === 'calibration'){
    document.querySelectorAll('.panel').forEach(function(p){ p.style.display = 'none'; });
    if(cal){ cal.style.display = 'block'; cal.classList.add('active'); }
    return;
  }
  if(cal){ cal.style.display = 'none'; cal.classList.remove('active'); }
  _origSwitchTab(tab);
};
"""
    html = html.replace('</script>', js + '</script>', 1)
    fixed += 1; print("[+] Injected calibration JavaScript")
else: print("[=] JavaScript already present")

with open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)

with open(API, 'r', encoding='utf-8') as f:
    api = f.read()
if '/api/calibration_status' not in api:
    ep = "\n\n@app.route(\"/api/calibration_status\", methods=[\"GET\"])\ndef calibration_status():\n    return jsonify({\"status\":\"available\",\"method\":\"7-param Helmert\",\"min_points\":3,\"max_points\":50})\n"
    api = api.replace('@app.route("/api/elevation"', ep + '@app.route("/api/elevation"')
    with open(API, 'w', encoding='utf-8') as f:
        f.write(api)
    fixed += 1; print("[+] Added /api/calibration_status endpoint")
else: print("[=] API endpoint already present")

print(); print("=" * 42); print("Done. " + str(fixed) + " fix(es) applied.")
if fixed == 0: print("All injections already present.")
print(); print("Next steps:"); print("  git add -A"); print("  git commit -m \"Polished calibration UI with balance scale\""); print("  git push origin main")
