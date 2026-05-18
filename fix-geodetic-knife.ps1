# ══════════════════════════════════════════════════════════════
# Geodetic Knife — Fix All & Deploy
# Run from: D:\Jeff\ghana-geodetic-vercel\
# ══════════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"
$root = "D:\Jeff\ghana-geodetic-vercel"

if (-not (Test-Path "$root\public\index.html")) {
    Write-Host "ERROR: Run this from D:\Jeff\ghana-geodetic-vercel\ or check the path." -ForegroundColor Red
    exit 1
}

Write-Host "`n[1/4] Fixing vercel.json ..." -ForegroundColor Cyan

$newVercelJson = @'
{
  "rewrites": [
    { "source": "/api/(.*)", "destination": "/api/index.py" }
  ]
}
'@

$newVercelJson | Out-File -FilePath "$root\vercel.json" -Encoding utf8NoBOM
Write-Host "  Done — removed explicit builds, using rewrites so Vercel serves public/" -ForegroundColor Green

Write-Host "`n[2/4] Fixing public/index.html (CSV header skip) ..." -ForegroundColor Cyan

$html = Get-Content "$root\public\index.html" -Raw -Encoding UTF8

# Fix 1: parseLine returns null instead of 'invalid' for non-numeric rows
$html = $html -replace "if \(nums\.length < 2\) return \{ type:'invalid' \};", "if (nums.length < 2) return null;  // skip header rows and blank lines silently"

# Fix 2: doConvert filters nulls and doesn't count skipped headers as errors
$oldBlock = 'const parsed = lines.map(l => parseLine(l));
      const invalid = parsed.filter(p => p && p.type === ''invalid'').length;
      const valid = parsed.filter(p => p && p.type !== ''invalid'');

      // Validation UI
      const inp = $(''smart-input'');
      if (invalid > 0 && valid.length === 0) {
        inp.classList.add(''error'');
        setStatus(''invalid'', invalid + '' invalid'' + (invalid > 1 ? '' rows'' : '' row''));
        showEmpty(); $(''csv-btn'').disabled = true; return;
      }
      inp.classList.remove(''error'');
      if (invalid > 0) setStatus(''valid'', valid.length + '' valid, '' + invalid + '' invalid'');'

$newBlock = @'
const parsed = lines.map(l => parseLine(l)).filter(p => p !== null);
      const valid = parsed;
      const skipped = lines.length - valid.length;

      // Validation UI
      const inp = $('smart-input');
      if (valid.length === 0) {
        inp.classList.add('error');
        setStatus('invalid', 'No valid coordinates found');
        showEmpty(); $('csv-btn').disabled = true; return;
      }
      inp.classList.remove('error');
      if (skipped > 0) setStatus('valid', valid.length + ' rows' + (skipped ? ' (' + skipped + ' skipped)' : ''));
'@

$html = $html.Replace($oldBlock, $newBlock)

# Fix 3: single valid row status line (handle removed 'invalid' variable)
$html = $html -replace "else if \(valid\.length === 1\) \{", "else {"
$html = $html -replace "const label = p\.type === 'wgs84' \? 'WGS84' : p\.gridType;", "const label = p.type === 'wgs84' ? 'WGS84' : p.gridType;"

# Fix 4: batch row status (remove reference to removed 'invalid' variable)
$html = $html -replace "else \{ setStatus\('valid', valid\.length \+ ' rows'\);", "else { setStatus('valid', valid.length + ' rows' + (skipped > 0 ? ' (' + skipped + ' skipped)' : ''));"

Set-Content "$root\public\index.html" -Value $html -Encoding UTF8 -NoNewline
Write-Host "  Done — header rows now silently skipped in CSV/batch input" -ForegroundColor Green

Write-Host "`n[3/4] Git commit & push ..." -ForegroundColor Cyan

Push-Location $root
git add vercel.json public/index.html
git commit -m "fix: vercel.json rewrites + skip CSV headers in parser"
git push origin main
Pop-Location

Write-Host "`n[4/4] All done!" -ForegroundColor Cyan
Write-Host @"
  vercel.json  → uses rewrites (no more 404)
  index.html   → headerless CSV now works
  Pushed to    → github.com/ddelaraiye/geodetic-knife

  Vercel will auto-redeploy. Check your dashboard.
"@ -ForegroundColor Green
