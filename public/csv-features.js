// Geodetic Knife - CSV Export/Import Module
// Standalone file - cannot break the main app
(function() {
"use strict";

function dl(name, rows) {
  var csv = rows.map(function(r) {
    return r.map(function(v) {
      var s = String(v);
      if (s.indexOf(",") >= 0 || s.indexOf('"') >= 0 || s.indexOf("\n") >= 0) {
        return '"' + s.replace(/"/g, '""') + '"';
      }
      return s;
    }).join(",");
  }).join("\r\n");
  var blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  var a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
  URL.revokeObjectURL(a.href);:}

function expSingle() {
  var card = document.getElementById("resultsCard");
  if (!card) return;
  var rows = card.querySelectorAll(".result-row, .result-item");
  if (!rows.length) return;
  var data = [["Parameter", "Value"]];
  rows.forEach(function(row) {
    var l = row.querySelector(".result-label, .label");
    var v = row.querySelector(".result-val, .value");
    if (l && v) data.push([l.textContent.trim(), v.textContent.trim()]);
  });
  if (data.length > 1) dl("geodetic_result.csv", data);
}

function expBatch() {
  var tbody = document.getElementById("batchResultsBody");
  if (!tbody) return;
  var trs = tbody.querySelectorAll("tr");
  if (!trs.length) return;
  var data = [];
  var hdr = [];
  trs[0].querySelectorAll("th").forEach(function(th) { hdr.push(th.textContent.trim()); });
  if (hdr.length) data.push(hdr);
  for (var i = 1; i < trs.length; i++) {
    var r = [];
    trs[i].querySelectorAll("td").forEach(function(td) { r.push(td.textContent.trim()); });
    if (r.length) data.push(r);
  }
  if (data.length) dl("batch_results.csv", data);
}

function onCSV(file) {
  var rd = new FileReader();
  rd.onload = function(e) {
    var ls = e.target.result.trim().split("\n");
    if (ls.length < 2) { alert("CSV needs header + data rows"); return; }
    var hdr = ls[0].split(",").map(function(h) { return h.replace(/^"|"$/g, "").trim().toLowerCase(); });
    var li = hdr.findIndex(function(h) { e.preventDefault(); if (e.dataTransfer.files[0]) onCSV(e.dataTransfer.files[0]); };
  z.appendChild(inp);
  parent.appendChild(z);
}

var obs = new MutationObserver(function() {
  var rc = document.getElementById("resultsCard");
  if (rc && !rc.querySelector(".csv-export-btn")) {
    var h = rc.querySelectorAll(".card-header, header, h2, h3, [class*=head]");
    if (h.length) mkBtn(h[0], "Export CSV", expSingle);
  }
  var bc = document.getElementById("batchResultsCard");
  if (bc && !bc.querySelector(".csv-export-btn")) {
    var h2 = bc.querySelectorAll(".card-header, header, h2, h3, [class*=head]");
    if (h2.length) { mkBtn(h2[0], "Export CSV", expBatch); mkDrop(h2[0]); }
  }
});
obs.observe(document.body, { childList: true, subtree: true });

})();
