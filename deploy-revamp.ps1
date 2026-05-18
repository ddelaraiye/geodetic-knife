# ═══════════════════════════════════════════════════════
# GH Geodetic Tool — UI Revamp v2 Deployment
# Run this from PowerShell to update your local project
# ═══════════════════════════════════════════════════════

$srcFile  = Join-Path $PSScriptRoot "ghana-geodetic-python\templates\index.html"
$destDir  = "D:\Projects\ghana-geodetic-python\templates"
$destFile = Join-Path $destDir "index.html"

if (-not (Test-Path $srcFile)) {
    Write-Host "[ERROR] Source file not found: $srcFile" -ForegroundColor Red
    Write-Host "        Make sure this script sits next to the ghana-geodetic-python folder." -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $destDir)) {
    Write-Host "[ERROR] Target directory not found: $destDir" -ForegroundColor Red
    Write-Host "        Is your Flask project at D:\Projects\ghana-geodetic-python ?" -ForegroundColor Yellow
    exit 1
}

# Backup the existing file
if (Test-Path $destFile) {
    $backup = $destFile -replace '\.html$', '_backup.html'
    Copy-Item $destFile $backup -Force
    Write-Host "[OK] Backed up existing file to: $backup" -ForegroundColor Green
}

# Deploy
Copy-Item $srcFile $destFile -Force
Write-Host "[OK] Deployed revamp to: $destFile" -ForegroundColor Green
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor Cyan
Write-Host "    1. cd D:\Projects\ghana-geodetic-python" -ForegroundColor White
Write-Host "    2. python app.py" -ForegroundColor White
Write-Host "    3. Open http://localhost:5000" -ForegroundColor White
Write-Host ""
