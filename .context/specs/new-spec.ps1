param(
  [Parameter(Mandatory = $true)]
  [string]$Slug,

  [ValidateSet("light", "full")]
  [string]$Mode = "full"
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$templateDir = Join-Path $scriptRoot "_templates"

$lightTemplate = Join-Path $templateDir "spec-light.md"
$fullTemplate = Join-Path $templateDir "spec-full.md"
$planTemplate = Join-Path $templateDir "implementation_plan.md"

$missing = @()
if (-not (Test-Path $lightTemplate)) { $missing += $lightTemplate }
if (-not (Test-Path $fullTemplate)) { $missing += $fullTemplate }
if (-not (Test-Path $planTemplate)) { $missing += $planTemplate }
if ($missing.Count -gt 0) {
  Write-Error "Missing templates: $($missing -join ', ')"
  exit 1
}

$Slug = $Slug.Trim() -replace "\s+", "-"
$Slug = $Slug.ToLowerInvariant()

if ($Slug -match "[^a-z0-9-]") {
  Write-Error "Slug must contain only letters, numbers, or dashes."
  exit 1
}

$date = Get-Date -Format "yyyy-MM-dd"
$folderName = "$date-$Slug"
$targetDir = Join-Path $scriptRoot $folderName

if (Test-Path $targetDir) {
  Write-Error "Spec folder already exists: $targetDir"
  exit 1
}

New-Item -ItemType Directory -Path $targetDir | Out-Null

if ($Mode -eq "light") {
  Copy-Item -Path $lightTemplate -Destination (Join-Path $targetDir "spec.md")
} else {
  Copy-Item -Path $fullTemplate -Destination (Join-Path $targetDir "spec.md")
  Copy-Item -Path $planTemplate -Destination (Join-Path $targetDir "implementation_plan.md")
}

Write-Host "Created $targetDir"
