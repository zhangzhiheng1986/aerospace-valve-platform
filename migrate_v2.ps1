# migrate_v2.ps1 — Proper brace-matching migration for all :root-based pages
param([string[]]$Files, [switch]$DryRun)

$frontend = "C:\Users\Administrator\.qclaw\workspace\aerospace-valve-platform\frontend"
$sharedCSS = '<link rel="stylesheet" href="/frontend/shared/bundle.css">'
$compatCSS = '<link rel="stylesheet" href="/frontend/shared/compat.css">'
$sharedJS = '<script src="/frontend/shared/utils.js"></script>' + "`n" +
            '<script src="/frontend/shared/toast.js"></script>' + "`n" +
            '<script src="/frontend/shared/api.js"></script>'

# Page-specific custom properties to preserve (not in shared tokens)
$preserveVars = @('--sidebar-w','--formula-list-w','--safe-bottom','--header-h','--nav-w')

# Find and remove a CSS block (like :root{...}) with proper brace counting
function Remove-CSSBlock([string]$text, [string]$selector, [ref]$removed) {
  $idx = $text.IndexOf($selector)
  if ($idx -lt 0) { return $text }
  
  $braceIdx = $text.IndexOf('{', $idx)
  if ($braceIdx -lt 0) { return $text }
  
  $depth = 1
  $i = $braceIdx + 1
  while ($i -lt $text.Length -and $depth -gt 0) {
    $ch = $text[$i]
    if ($ch -eq '{') { $depth++ }
    elseif ($ch -eq '}') { $depth-- }
    $i++
  }
  
  if ($depth -eq 0) {
    $block = $text.Substring($idx, $i - $idx)
    $removed.Value = $block
    return $text.Remove($idx, $i - $idx)
  }
  return $text
}

$migrated = 0
foreach ($file in $Files) {
  $path = Join-Path $frontend $file
  if (-not (Test-Path $path)) { Write-Host "SKIP $file (not found)"; continue }
  
  $html = [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)
  
  if ($html -match '/frontend/shared/bundle\.css') {
    Write-Host "SKIP $file (already migrated)"; continue
  }
  
  if ($html -notmatch ':root\s*\{') {
    Write-Host "SKIP $file (no :root)"; continue
  }
  
  $origSize = $html.Length
  
  # 1. Extract custom vars from :root block before removing it
  $rootBlock = ''
  $tmp = Remove-CSSBlock $html ':root' ([ref]$rootBlock)
  if (-not $rootBlock) { Write-Host "SKIP $file (can't parse :root)"; continue }
  
  $customVars = ''
  $varMatches = [regex]::Matches($rootBlock, '(--[\w-]+)\s*:')
  foreach ($m in $varMatches) {
    $vn = $m.Groups[1].Value
    if ($vn -in $preserveVars) {
      # Extract full property value
      $propMatch = [regex]::Match($rootBlock, [regex]::Escape($vn) + '\s*:\s*([^;]+)')
      if ($propMatch.Success) {
        $customVars += "  $vn" + ': ' + $propMatch.Groups[1].Value.Trim() + ";`n"
      }
    }
  }
  
  # 2. Remove :root block
  $html = $tmp
  
  # 3. Remove *{margin:0;padding:0;box-sizing:border-box} (variants)
  $html = $html -replace '\*\s*\{\s*margin\s*:\s*0\s*;\s*padding\s*:\s*0\s*;\s*box-sizing\s*:\s*border-box\s*;?\s*\}', ''
  
  # 4. Insert shared CSS links + custom vars
  $cssInsert = "$sharedCSS`n$compatCSS"
  if ($customVars) {
    $customBlock = "`n<style>`n:root {`n$customVars}`n</style>"
    $cssInsert += $customBlock
  }
  
  if ($html -match '^(\s*)<style>') {
    $indent = $matches[1]
    $html = $html -replace '(<style>)', ($cssInsert + "`n`$1")
  } else {
    $html = $html -replace '</head>', ($cssInsert + "`n</head>")
  }
  
  # 5. Simplify body — keep only non-default properties
  $bodyBlock = ''
  $html = Remove-CSSBlock $html 'body' ([ref]$bodyBlock)
  if ($bodyBlock) {
    $bodyInner = ''
    if ($bodyBlock -match 'body\s*\{(.*)\}') { $bodyInner = $matches[1] }
    $kept = @()
    foreach ($prop in ($bodyInner -split ';')) {
      $p = $prop.Trim()
      if (-not $p) { continue }
      if ($p -match 'font-family') { continue }
      if ($p -match 'background\s*:\s*var\(--bg') { continue }
      if ($p -match 'color\s*:\s*var\(--text') { continue }
      if ($p -match '^\s*line-height') { continue }
      $kept += $p
    }
    if ($kept.Count -gt 0) {
      $newBody = 'body{' + ($kept -join ';') + '}'
      # Insert before where body was
      $headIdx = $html.IndexOf('</style>')
      if ($headIdx -ge 0) {
        $html = $html.Insert($headIdx, "`n$newBody`n")
      }
    }
  }
  
  # 6. Add shared JS before </body> (only if page has inline scripts)
  if ($html -match '<script>' -or $html -match '<script src=') {
    $html = $html -replace '</body>', ($sharedJS + "`n</body>")
  }
  
  # 7. Write
  if ($DryRun) {
    $cvCount = if ($customVars) { ($customVars -split "`n" | Where-Object { $_ -match '--' }).Count } else { 0 }
    Write-Host "DRY-RUN $file ($origSize -> $($html.Length) chars, $cvCount custom vars)"
  } else {
    [System.IO.File]::WriteAllText($path, $html, (New-Object System.Text.UTF8Encoding $false))
    Write-Host "OK $file ($origSize -> $($html.Length) chars)"
    $migrated++
  }
}

Write-Host "`n$migrated files migrated."
