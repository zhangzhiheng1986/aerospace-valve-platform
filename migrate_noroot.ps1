# migrate_noroot.ps1 — Light migration for pages without :root CSS variables
param([string[]]$Files)

$frontend = "C:\Users\Administrator\.qclaw\workspace\aerospace-valve-platform\frontend"
$sharedCSS = '<link rel="stylesheet" href="/frontend/shared/bundle.css">' + "`n" +
             '<link rel="stylesheet" href="/frontend/shared/compat.css">'
$sharedJS = '<script src="/frontend/shared/utils.js"></script>' + "`n" +
            '<script src="/frontend/shared/toast.js"></script>' + "`n" +
            '<script src="/frontend/shared/api.js"></script>'

$migrated = 0
foreach ($file in $Files) {
  $path = Join-Path $frontend $file
  if (-not (Test-Path $path)) { Write-Host "SKIP $file (not found)"; continue }
  
  $html = [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)
  
  if ($html -match '/frontend/shared/bundle\.css') {
    Write-Host "SKIP $file (already migrated)"; continue
  }
  
  $origSize = $html.Length
  
  # 1. Remove * { margin:0; padding:0; box-sizing:border-box; }
  $html = $html -replace '\*\s*\{\s*margin\s*:\s*0\s*;\s*padding\s*:\s*0\s*;\s*box-sizing\s*:\s*border-box\s*;?\s*\}', ''
  
  # 2. Insert shared CSS before existing <style>
  $html = $html -replace '(<style>)', ($sharedCSS + "`n`$1")
  
  # 3. Add shared JS before </body> if page has scripts
  if ($html -match '<script>' -or $html -match '<script src=') {
    $html = $html -replace '</body>', ($sharedJS + "`n</body>")
  }
  
  [System.IO.File]::WriteAllText($path, $html, (New-Object System.Text.UTF8Encoding $false))
  Write-Host "OK $file ($origSize -> $($html.Length) chars)"
  $migrated++
}

Write-Host "`n$migrated files migrated."
