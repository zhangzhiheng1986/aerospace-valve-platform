$frontend = 'C:\Users\Administrator\.qclaw\workspace\aerospace-valve-platform\frontend'

# Build set of known variables (from shared tokens.css)
$tokensText = [System.IO.File]::ReadAllText("$frontend\shared\tokens.css", [System.Text.Encoding]::UTF8)
$knownVars = @{}
$tokenMatches = [regex]::Matches($tokensText, '(--[\w-]+)\s*:')
foreach ($m in $tokenMatches) { $knownVars[$m.Groups[1].Value] = 'tokens' }

# Add compat.css variables
$compatText = [System.IO.File]::ReadAllText("$frontend\shared\compat.css", [System.Text.Encoding]::UTF8)
$compatMatches = [regex]::Matches($compatText, '(--[\w-]+)\s*:')
foreach ($m in $compatMatches) { $knownVars[$m.Groups[1].Value] = 'compat' }

# Scan all HTML files
$allUsed = @{}
Get-ChildItem "$frontend\*.html" | ForEach-Object {
  $text = [System.IO.File]::ReadAllText($_.FullName, [System.Text.Encoding]::UTF8)
  $varRefs = [regex]::Matches($text, 'var\((--[\w-]+)')
  foreach ($m in $varRefs) {
    $vn = $m.Groups[1].Value
    if (-not $knownVars.ContainsKey($vn)) {
      if (-not $allUsed.ContainsKey($vn)) { $allUsed[$vn] = @() }
      $allUsed[$vn] += $_.Name
    }
  }
}

if ($allUsed.Count -eq 0) {
  Write-Host 'All CSS variables are covered!'
} else {
  Write-Host "MISSING variables (used but not defined):"
  foreach ($kv in $allUsed.GetEnumerator() | Sort-Object Name) {
    Write-Host "  $($kv.Name) -> used in: $($kv.Value -join ', ')"
  }
}
