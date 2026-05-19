import os, shutil
ROOT = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(ROOT, 'public', 'index.html')

CSS = """
/* CALIBRATION */
#calContainer{display:none;flex:1;flex-direction:column;gap:.6rem;padding:0}
#calContainer.active{display:flex}
.cal-bar{display:flex;align-items:center;gap:.8rem;padding:.5rem .8rem;background:var(--card);border:1px solid var(--border);border-radius:var(--radius);font-size:.82rem;flex-wrap:wrap}
.cal-badge{padding:.15rem .5rem;border-radius:12px;font-size:.72rem;font-weight:600;white-space:nowrap}
.cal-badge.default{background:#334155;color:var(--muted)}.cal-badge.calibrated{background:#065f46;color:#6ee7b7}.cal-badge.pending{background:#78350f;color:#fcd34d}
.cal-section{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:.8rem}
.cal-section h4{font-size:.8rem;color:var(--dim);margin-bottom:.5rem;text-transform:uppercase;letter-spacing:.04em}
.cp-wrap{max-height:260px;overflow:auto;border:1px solid var(--border);border-radius:4px;font-size:.72rem}
.cp-wrap table{width:100%;border-collapse:collapse}.cp-wrap th,.cp-wrap td{padding:.25rem .35rem;text-align:left;border-bottom:1px solid var(--border)}
.cp-wrap th{position:sticky;top:0;background:var(--card);color:var(--dim);font-weight:600;font-size:.68rem;text-transform:uppercase}
.cp-wrap input{width:100%;padding:.2rem .3rem;background:var(--surface);border:1px solid var(--border);border-radius:3px;color:var(--text);font-size:.72rem;font-family:var(--font-mono)}
.cp-wrap input:focus{border-color:var(--accent)}.cal-btns{display:flex;gap:.4rem;flex-wrap:wrap;margin-top:.4rem}
.cal-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(100px,1fr));gap:.4rem}
.cal-stat{background:var(--surface);border-radius:6px;padding:.4rem .5rem;text-align:center}
.cal-stat .v{font-size:.95rem;font-weight:700;font-family:var(--font-mono)}.cal-stat .l{font-size:.65rem;color:var(--dim);margin-top:.1rem}
.cal-res-wrap{max-height:200px;overflow:auto;border:1px solid var(--border);border-radius:4px;font-size:.7rem}
.cal-res-wrap table{width:100%;border-collapse:collapse}.cal-res-wrap th,.cal-res-wrap td{padding:.2rem .3rem;text-align:left;border-bottom:1px solid var(--border)}
.cal-res-wrap th{position:sticky;top:0;background:var(--card);color:var(--dim);font-weight:600;font-size:.65rem}
.g{color:#22c55e}.y{color:#f59e0b}.r{color:#ef4444}
.cal-params table{width:100%;border-collapse:collapse;font-size:.72rem}.cal-params th,.cal-params td{padding:.25rem .4rem;text-align:left;border-bottom:1px solid var(--border)}
.cal-params th{color:var(--dim);font-weight:600;font-size:.68rem}.cal-params td{font-family:var(--font-mono)}
"""

TAB = '\n<button class="tab-btn" data-tab="calibration">\u2699 Calibrate</button>\n'

CTNR = """
<div id="calContainer">
<div class="cal-bar">
<span id="calBadge" class="cal-badge default">DEFAULT (EPSG:6896)</span>
<span id="calRmsLabel" style="color:var(--dim);font-size:.75rem"></span>
<div style="margin-left:auto;display:flex;gap:.3rem">
<button class="btn btn-sm" style="background:var(--accent);color:#000;font-weight:600" onclick="doCalibrate()">&#9881; Calculate</button>
<button class="btn btn-sm" style="background:#7f1d1d;color:#fca5a5" onclick="clearCal()">&#10005; Clear</button>
</div></div>
<div class="cal-section">
<div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.5rem">
<h4 style="margin:0">Control Points</h4>
<select id="calTarget" style="font-size:.75rem;padding:.15rem .4rem;background:var(--surface);border:1px solid var(--border);border-radius:4px;color:var(--text)">
<option value="GNG">GNG (Gold Coast Feet)</option><option value="GMG">GMG (Metres)</option></select>
<span style="color:var(--dim);font-size:.7rem">min 3</span></div>
<div class="cp-wrap"><table><thead><tr><th>#</th><th>Lat</th><th>Lon</th><th>H(m)</th><th>Easting</th><th>Northing</th><th></th></tr></thead><tbody id="cpBody"></tbody></table></div>
<div class="cal-btns">
<button class="btn btn-sm" onclick="addCP()">+ Add</button>
<button class="btn btn-sm" onclick="rmCP()">- Remove</button>
<button class="btn btn-sm" onclick="document.getElementById('cpFile').click()">Import CSV</button>
<input type="file" id="cpFile" accept=".csv,.txt,.tsv" style="display:none" onchange="loadCPFile(event)">
<button class="btn btn-sm" onclick="loadSampleCP()">Load Sample</button></div></div>
<div id="calResults" class="cal-section" style="display:none">
<h4>Results</h4><div class="cal-stats" id="calStats"></div>
<h4 style="margin-top:.6rem">7 Parameters</h4><div class="cal-params" id="calParamsTable"></div>
<h4 style="margin-top:.6rem">Residuals</h4><div class="cal-res-wrap" id="calResTable"></div>
<div class="cal-btns" style="margin-top:.5rem">
<button class="btn btn-sm" style="background:#065f46;color:#6ee7b7;font-weight:600" onclick="applyCal()">&#10003; Apply to Conversions</button>
<button class="btn btn-sm" onclick="exportCal()">Export</button></div></div></div>
"""

JS = """
var _calibration=null,_pendingCal=null;
try{_calibration=JSON.parse(localStorage.getItem('geodetic_calibration'));}catch(e){}
function addCP(lat,lon,h,e,n){var tb=document.getElementById('cpBody'),nr=tb.children.length+1,tr=document.createElement('tr');
tr.innerHTML='<td style="color:var(--dim);text-align:center">'+nr+'</td><td><input value="'+(lat||'')+'" placeholder="5.6037" class="cpL"></td><td><input value="'+(lon||'')+'" placeholder="-0.1870" class="cpLn"></td><td><input value="'+(h||'')+'" placeholder="0" class="cpH" style="width:60px"></td><td><input value="'+(e||'')+'" placeholder="E" class="cpE"></td><td><input value="'+(n||'')+'" placeholder="N" class="cpN"></td><td><button class="btn btn-sm" style="background:#7f1d1d;color:#fca5a5;padding:.1rem .3rem" onclick="this.closest(\\'tr\\').remove();renumCP()">&#10005;</button></td>';tb.appendChild(tr);}
function rmCP(){var tb=document.getElementById('cpBody');if(tb.lastChild)tb.removeChild(tb.lastChild);renumCP();}
function renumCP(){document.querySelectorAll('#cpBody tr').forEach(function(r,i){r.children[0].textContent=i+1;});}
function getCP(){var pts=[];document.querySelectorAll('#cpBody tr').forEach(function(tr){var la=tr.querySelector('.cpL').value.trim(),lo=tr.querySelector('.cpLn').value.trim(),h=tr.querySelector('.cpH').value.trim(),e=tr.querySelector('.cpE').value.trim(),n=tr.querySelector('.cpN').value.trim();if(la&&lo&&e&&n)pts.push({lat:parseFloat(la),lon:parseFloat(lo),h:h?parseFloat(h):0,easting:parseFloat(e),northing:parseFloat(n)});});return pts;}
function loadSampleCP(){document.getElementById('cpBody').innerHTML='';[[5.603717,-0.186972,28.5,892345.67,123456.78],[5.605124,-0.185234,29.1,894128.43,123678.90],[5.600891,-0.190123,27.8,888756.21,123102.55],[5.607452,-0.183891,30.2,896432.89,124015.33],[5.598213,-0.191456,26.9,886543.12,122598.77]].forEach(function(p){addCP(p[0],p[1],p[2],p[3],p[4]);});toast('Loaded 5 sample points','info');}
function loadCPFile(ev){var f=ev.target.files[0];if(!f)return;var rd=new FileReader();rd.onload=function(){var ls=rd.result.trim().split(/\\r?\\n/);if(ls.length<2)return;var hd=ls[0].split(/[\\t,;]/).map(function(h){return h.trim().toLowerCase().replace(/['"]/g,'');});var lk=hd.indexOf('lat'),ok=hd.indexOf('lon'),ek=hd.indexOf('easting'),nk=hd.indexOf('northing');if(lk<0)lk=hd.indexOf('latitude');if(ok<0){ok=hd.indexOf('longitude');if(ok<0)ok=hd.indexOf('lng');}if(ek<0)ek=hd.indexOf('e');if(nk<0)nk=hd.indexOf('n');if(lk<0||ok<0||ek<0||nk<0){toast('Need lat,lon,easting,northing columns','error');return;}document.getElementById('cpBody').innerHTML='';var c=0;for(var i=1;i<ls.length;i++){var vs=ls[i].split(/[\\t,;]/).map(function(v){return v.trim().replace(/['"]/g,'');});if(vs.length>=4&&vs[lk]&&vs[ok]&&vs[ek]&&vs[nk]){addCP(vs[lk],vs[ok],'',vs[ek],vs[nk]);c++;}}toast('Imported '+c+' points','success');};rd.readAsText(f);ev.target.value='';}
async function doCalibrate(){var pts=getCP();if(pts.length<3){toast('Need min 3 points','error');return;}var tgt=document.getElementById('calTarget').value;try{var res=await fetch('/api/calibrate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({points:pts,target:tgt})});var r=await res.json();if(!r.success){toast(r.error,'error');return;}_pendingCal=r;var s=r.statistics;document.getElementById('calBadge').className='cal-badge pending';document.getElementById('calBadge').textContent='PENDING - RMS '+s.rms_combined+' m';document.getElementById('calRmsLabel').textContent=s.num_points+' pts, '+s.degrees_of_freedom+' DoF';var rc=s.rms_combined;document.getElementById('calStats').innerHTML='<div class="cal-stat"><div class="v">'+s.num_points+'</div><div class="l">Points</div></div><div class="cal-stat"><div class="v">'+s.degrees_of_freedom+'</div><div class="l">DoF</div></div><div class="cal-stat"><div class="v '+(s.rms_e<.5?'g':s.rms_e<1?'y':'r')+'">'+s.rms_e+'</div><div class="l">RMS E</div></div><div class="cal-stat"><div class="v '+(s.rms_n<.5?'g':s.rms_n<1?'y':'r')+'">'+s.rms_n+'</div><div class="l">RMS N</div></div><div class="cal-stat"><div class="v '+(rc<.1?'g':rc<.5?'y':'r')+'" style="font-size:1.1rem">'+rc+'</div><div class="l">RMS (m)</div></div><div class="cal-stat"><div class="v" style="color:#3b82f6">'+(s.scale_ppm>0?'+':'')+s.scale_ppm+'</div><div class="l">Scale ppm</div></div>';var p=r.params,asr=180/Math.PI/3600;document.getElementById('calParamsTable').innerHTML='<table><tr><th>Param</th><th>Value</th><th>Unit</th></tr><tr><td>Tx</td><td>'+p.tx.toFixed(4)+'</td><td>m</td></tr><tr><td>Ty</td><td>'+p.ty.toFixed(4)+'</td><td>m</td></tr><tr><td>Tz</td><td>'+p.tz.toFixed(4)+'</td><td>m</td></tr><tr><td>Rx</td><td>'+(p.rx*asr).toFixed(4)+'</td><td>arcsec</td></tr><tr><td>Ry</td><td>'+(p.ry*asr).toFixed(4)+'</td><td>arcsec</td></tr><tr><td>Rz</td><td>'+(p.rz*asr).toFixed(4)+'</td><td>arcsec</td></tr><tr><td>Scale</td><td>'+p.scale.toFixed(9)+'</td><td>unitless</td></tr></table>';var rh='<table><tr><th>#</th><th>Lat</th><th>Lon</th><th>E Act</th><th>E Pred</th><th>N Act</th><th>N Pred</th><th>dE</th><th>dN</th><th>Comb</th></tr>';r.residuals.forEach(function(rv){var c=rv.res_combined<.1?'g':rv.res_combined<.5?'y':'r';rh+='<tr><td>'+rv.point+'</td><td>'+rv.lat+'</td><td>'+rv.lon+'</td><td>'+rv.e_actual+'</td><td>'+rv.e_predicted+'</td><td>'+rv.n_actual+'</td><td>'+rv.n_predicted+'</td><td>'+rv.res_e+'</td><td>'+rv.res_n+'</td><td class="'+c+'"><b>'+rv.res_combined+'</b></td></tr>';});rh+='</table>';document.getElementById('calResTable').innerHTML=rh;document.getElementById('calResults').style.display='block';toast('RMS = '+rc+' m',rc<.5?'success':'info',4000);}catch(e){toast('Error: '+e.message,'error');}}
function applyCal(){if(!_pendingCal){toast('Calculate first','error');return;}_calibration={towgs84:_pendingCal.towgs84,statistics:_pendingCal.statistics};localStorage.setItem('geodetic_calibration',JSON.stringify(_calibration));document.getElementById('calBadge').className='cal-badge calibrated';document.getElementById('calBadge').textContent='CALIBRATED - '+_calibration.statistics.rms_combined+' m RMS';toast('Calibration applied!','success',5000);}
function clearCal(){_calibration=null;_pendingCal=null;localStorage.removeItem('geodetic_calibration');document.getElementById('calResults').style.display='none';document.getElementById('calBadge').className='cal-badge default';document.getElementById('calBadge').textContent='DEFAULT (EPSG:6896)';document.getElementById('calRmsLabel').textContent='';toast('Calibration cleared','info');}
function exportCal(){if(!_pendingCal)return;var c=_pendingCal,p=c.params,asr=180/Math.PI/3600;var t='GEODETIC KNIFE CALIBRATION\\n'+new Date().toISOString()+'\\nTarget: '+c.target+'\\nRMS: '+c.statistics.rms_combined+' m\\n\\ntowgs84='+c.towgs84+'\\n\\nTx='+p.tx.toFixed(6)+' Ty='+p.ty.toFixed(6)+' Tz='+p.tz.toFixed(6)+'\\nRx='+(p.rx*asr).toFixed(6)+' Ry='+(p.ry*asr).toFixed(6)+' Rz='+(p.rz*asr).toFixed(6)+' arcsec\\nScale='+p.scale.toFixed(12)+' ('+c.statistics.scale_ppm.toFixed(2)+' ppm)\\n';downloadFile('calibration_'+c.target+'_'+Date.now()+'.txt',t,'text/plain');}
(function(){var _f=window.fetch;window.fetch=function(u,o){if(o&&o.method==='POST'&&typeof u==='string'&&(u.indexOf('/api/convert')>=0||u.indexOf('/api/convert_batch')>=0)){try{if(_calibration&&_calibration.towgs84){var b=JSON.parse(o.body);b.calibration={towgs84:_calibration.towgs84};o=Object.assign({},o,{body:JSON.stringify(b)});}}catch(e){}}return _f.apply(this,arguments);};})();
(function(){var cC=document.getElementById('calContainer'),iP=document.getElementById('inputPanel'),oP=document.getElementById('outputPanel');if(!cC)return;document.querySelectorAll('.tab-btn').forEach(function(b){b.addEventListener('click',function(){if(b.dataset.tab==='calibration'){setTimeout(function(){if(iP)iP.style.display='none';if(oP)oP.style.display='none';cC.classList.add('active');},0);}else{setTimeout(function(){cC.classList.remove('active');if(iP)iP.style.display='';if(oP)oP.style.display='';},0);}});});if(_calibration&&_calibration.statistics){document.getElementById('calBadge').className='cal-badge calibrated';document.getElementById('calBadge').textContent='CALIBRATED - '+_calibration.statistics.rms_combined+' m RMS';document.getElementById('calRmsLabel').textContent=_calibration.statistics.num_points+' pts';}})();
addCP();addCP();addCP();
"""

with open(HTML, 'r', encoding='utf-8') as f:
    h = f.read()

shutil.copy2(HTML, HTML + '.calbak')
p = 0
if '</style>' in h and 'cal-bar' not in h:
    h = h.replace('</style>', CSS + '\n</style>', 1); p += 1
if 'data-tab="grid_to_wgs84"' in h and 'data-tab="calibration"' not in h:
    h = h.replace('data-tab="grid_to_wgs84">Grid &rarr; WGS 84</button>', 'data-tab="grid_to_wgs84">Grid &rarr; WGS 84</button>' + TAB, 1); p += 1
if '<script>' in h and 'calContainer' not in h:
    h = h.replace('<script>', CTNR + '\n<script>', 1); p += 1
if '</script>' in h and '_pendingCal' not in h:
    h = h.replace('</script>', JS + '\n</script>', 1); p += 1

with open(HTML, 'w', encoding='utf-8') as f:
    f.write(h)

print(f"Patched {p}/4 injections into {HTML}")
print(f"Backup: {HTML}.calbak")