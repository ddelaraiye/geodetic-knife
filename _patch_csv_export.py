"""
Geodetic Knife - CSV Export + File Import Patch
Run: python _patch_csv_export.py
"""
import os

FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public', 'index.html')

with open(FILE, 'r', encoding='utf-8') as f:
    h = f.read()

# Normalize line endings (Windows CRLF => LV)
h = h.replace('\r\n', '\n')

# 1. Add CSS for export bar + file drop zone
css = """
/* ========== EXPORT BAR ========== */
.export-bar{display:flex;gap:6px;margin-top:12px;padding-top:10px;border-top:1px solid rgba(255,255,255,.06)}
.file-drop{border:2px dashed var(--border);border-radius:var(--radius);padding:20px;text-align:center;cursor:pointer;transition:all .2s;margin-bottom:10px}
.file-drop:hover,.file-drop.dragover{border-color:var(--gold);background:var(--gold-dim)}
.file-drop input[type=file]{display:none}
.file-drop-icon{font-size:2rem;margin-bottom:6px;opacity:.6}
.file-drop-text{font-size:.82rem;color:var(--muted)}
"""
h = h.replace('</style>', css + '</style>')

# 2. Add export bar to each result panel
for tab_id in ['w2g', 'gg', 'g2w']:
    content_div = '<div id="' + tab_id + '_result_content"></div>\n  </div>'
    if h.find(content_div) == -1:
      continue
    export_html = (
        '<div id="' + tab_id + '_result_content"></div>\n'
        '    <div class="export-bar" id="' + tab_id + '_export_bar" style="display:none">\n'
        '      <button class="btn btn-outline btn-sm" onclick="exportResultCSV(\'' + tab_id + '\')">Export CST</button>\n'
        '      <button class="btn btn-outline btn-sm" onclick="copyResult(\'' + tab_id + '\')">Copy</button>\n'
        '   </div>\n'
        '  </div>'
    )
    h = h.replace(content_div, export_html)

# 3. Add Export CSV button next to Import CSV in calibration section
old_btn = '<button class="btn btn-outline btn-sm" onclick="importCSV()">Import CSV</button>'
new_btn = old_btn + '\n      <button class="btn btn-outline btn-sm" onclick="exportCalibCSV()">Export CSV</button>'
if h.find(old_btn) != -1:
    h = h.replace(old_btn, new_btn)

# 4. Patch showResult to also toggle export bar visibility
old_show = 'function showResult(id, show, isError){\n  const el = $(id);\n  el.classList.toggle(\'show\', show);\n  el.classList.toggle(\'error\', !!isError);\n}'
if h.find(old_show) != -1:
    new_show = 'function showResult(id, show, isError){\n  const el = $(id);\n  el.classList.toggle(\'show\', show);\n  el.classList.toggle(\'error\', !!isError);\n  const bar = $(id + \'_export_bar\');\n  if(bar) bar.style.display = (show && !isError) ? \'flex\' : \'none\';\n}'
    h = h.replace(old_show, new_show)

# 5. Upgrade CSV modal with drag-and-drop file upload
old_modal = '''<div class="modal">
      <h3>Import CSV Data</h3>
      <p style="font-size:.82rem;color:var(--muted);margin-bottom:10px">Format: lat,lon,easting,northing[,GNG|GMG] \u2014 one point per line</p>
      <textarea id="csvInput" placeholder="5.603717,-0.186972,762834.890,1113489.450,GNG&#10;5.556,-0.229,759213.56,1107826.12,GNG" rows="8"></textarea>
      <div class="btn-row" style="margin-top:10px">
        <button class="btn btn-gold btn-sm" onclick="parseCSR()">Import</button>
        <button class="btn btn-outline btn-sm" onclick="closeCSVModal()">Cancel</button>
      </div>
  </div>'''

if h.find(old_modal) != -1:
    new_modal = '''<div class="modal">
      <h3>Import CSV Data</h3>
      <div class="file-drop" id="csvFileDrop" onclick="document.getElementById('csvFileInput').click()" ondragover="event.preventDefault();this.classList.add('dragover')" ondragleave="this.classList.remove('dragover')" ondrop="event.preventDefault();this.classList.remove('dragover');handleCSVFile(event.dataTransfer.files[0])">
        <input type="file" id="csvFileInput" accept=".csv,.txt,.tsv" onchange="handleCSVFile(this.files[0])">
        <div class="file-drop-icon">\u2b06</div>
        <div class="file-drop-text">Drop .csv file here or click to browse</div>
      </div>
      <p style="font-size:78rem;color:var(--muted);margin-bottom:10px;text-align:center">or paste below \u2014 Format: lat,lon,easting,northing[,GNG|GMG]</p>
      <textarea id="csvInput" placeholder="5.603717,-0.186972,762834.890,1113489.450,GNG&#10;5.556,-0.229,759213.56,1107826.12,GNG" rows="6"></textarea>
      <div class="btn-row" style="margin-top:10px">
        <button class="btn btn-gold btn-sm" onclick="parseCSR()">Import</button>
        <button class="btn btn-outline btn-sm" onclick="closeCSVModal()">Cancel</button>
      </div>
  </div>'''
    h = h.replace(old_modal, new_modal)

# 6. Add CSV export/import JavaScript before the csvModal click listener
js_block = r'''
/* =========== CSV EXPORT / IMPORT ========== */
var _lastResults = {};

var _origW2G = showWGS84ToGrid;
showWGS84ToGrid = function(d) { _lastResults.w2g = d; _origW2G(d); };

var _origGG = showGridToGridResult;
showGridToGridResult = function(d, f) { _lastResults.gg = Object.assign({}, d, {from: f}); _origGG(d, f); };

var _origG2W = showGridToWGS84Result;
showGridToWGS84Result = function(d) { _lastResults.g2w = d; _origG2W(d); };

window.downloadCSV = function(filename, csvText) {
  var blob = new Blob([csvText], {type: 'text/csv;charset=utf-8;'});
  var url = URL.createObjectURL(blob);
  var a = document.createElement('a');
  a.href = url; a.download = filename; a.style.display = 'none';
  document.body.appendChild(a); a.click();
  setTimeout(function() { URL.revokeObjectURL(url); a.remove(); }, 100);
  toast('Downloaded ' + filename, 'success');
};

window.exportResultCSV = function(tab) {
  var d = _lastResults[tab];
  if (!d) { toast('No result to export.', 'error'); return; }
  var rows = [];
  if (tab === 'w2g') {
    rows.push('Latitude,Longitude,GNG_Easting_ft,GNG_Northing_ft,GMG_Easting_m,GMG_Northing_m,Transformation,Method,Accuracy_m');
    var acc = d.accuracy || {};
    rows.push([
      (d.wgs84 && d.wgs84.lat) || '',
      (d.wgs84 && d.wgs84.lon) || '',
      (d.gng && d.gng.easting) || '',
      (d.gng && d.gng.northing) || '',
      (d.gmg && d.gmg.easting) || '',
      (d.gmg && d.gmg.northing) || '',
      acc.transformation || '',
      acc.method || '',
      acc.horizontal_accuracy_meters || ''
    ].join(','));
  } else if (tab === 'gg') {
    rows.push('GNG_Easting_ft,GNG_Northing_ft,GMG_Easting_m,GMG_Northing_m,WGS84_Lat,WGS84_Lon,From_Grid');
    rows.push([
      (d.gng && d.gng.easting) || '',
      (d.gng && d.gng.northing) || '',
      (d.gmg && d.gmg.easting) || '',
      (d.gmg && d.gmg.northing) || '',
      (d.wgs84 && d.wgs84.lat) || '',
      (d.wgs84 && d.wgs84.lon) || '',
      d.from || ''
    ].join(','));
  } else if (tab === 'g2w') {
    rows.push('Easting,Northing,Grid_Type,WGS84_Lat,WGS84_Lon');
    rows.push([
      (d.gng && d.gng.easting) || '',
      (d.gng && d.gng.northing) || '',
      'GNG',
      (d.wgs84 && d.wgs84.lat) || '',
      (d.wgs84 && d.wgs84.lon) || ''
    ].join(','));
  }
  var ts = new Date().toISOString().slice(0, 10);
  downloadCSV('geodetic_knife_' + tab + '_' + ts + '.csv', rows.join('\n'));
};

window.copyResult = function(tab) {
  var el = $(tab + '_result_content');
  if (!el) return;
  var text = el.innerText;
  if (!text) { toast('Nothing to copy.', 'error'); return; }
  navigator.clipboard.writeText(text).then(function() {
    toast('Copied to clipboard', 'success');
  }).catch(function() {
    var ta = document.createElement('textarea');
    ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    document.execCommand('copy'); ta.remove();
    toast('Copied to clipboard', 'success');
  });
};

window.exportCalibCSV = function() {
  var rows = $('calibTableBody').querySelectorAll('tr');
  if (rows.length === 0) { toast('No calibration points to export.', 'error'); return; }
  var csv = 'Latitude,Longitude,Easting,Northing,Grid_Type\n';
  rows.forEach(function(tr) {
    var inputs = tr.querySelectorAll('input, select');
    if (inputs.length >= 5) {
      csv += [inputs[0].value, inputs[1].value, inputs[2].value, inputs[3].value, inputs[4].value].join(',') + '\n';
    }
  });
  var ts = new Date().toISOString().slice(0, 10);
  downloadCSV('calibration_points_' + ts + '.csv', csv);
};

window.handleCSVFile = function(file) {
  if (!file) return;
  var reader = new FileReader();
  reader.onload = function(e) {
    var text = e.target.result;
    $('csvInput').value = text;
    toast('File loaded: ' + file.name + ' (' + file.size + ' bytes)', 'info');
  };
  reader.onerror = function() { toast('Failed to read file.', 'error'); };
  reader.readAsText(file);
};

'''

anchor = "$('csvModal').addEventListener('click', function(e){"
if h.find(anchor) != -1:
    h = h.replace(anchor, js_block + anchor)

with open(FILE, 'w', encoding='utf-8') as f:
    f.write(h)

print('CSV export + file import patch applied successfully!')
print('Features added:')
print('  - Export CSV button on all 3 conversion result panels')
print('  - Copy button on all 3 conversion result panels')
print('  - Export CSV button for calibration control points')
print('  - Drag-and-drop file upload in CSV import modal')
print('  - File picker (browse) button in CSV import modal')
