# City of Heroes: Homecoming - Batch Pool Power Converter
# Converts all power pools from raw JSON to planner format

$ErrorActionPreference = "Continue"

# Pool list
$pools = @(
    "experimentation",
    "fighting",
    "fitness",
    "flight",
    "force_of_will",
    "gadgetry",
    "invisibility",
    "leadership",
    "leaping",
    "manipulation",
    "medicine",
    "sorcery",
    "speed",
    "teleportation",
    "utility_belt"
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "City of Heroes: Homecoming - Batch Pool Converter" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Converting $($pools.Count) power pools..." -ForegroundColor Yellow
Write-Host ""

$successCount = 0
$failCount = 0
$failedPools = @()

foreach ($pool in $pools) {
    Write-Host "Processing: $pool" -ForegroundColor White
    
    # Run python script directly (let output flow naturally)
    python convert_pool.py $pool
    
    # Check the exit code
    if ($LASTEXITCODE -eq 0) {
        $successCount++
        Write-Host "  Success" -ForegroundColor Green
    } else {
        $failCount++
        $failedPools += $pool
        Write-Host "  Failed (Exit code: $LASTEXITCODE)" -ForegroundColor Red
    }
    
    Write-Host ""
}

# Summary
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "CONVERSION SUMMARY" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Total Pools:    $($pools.Count)" -ForegroundColor White
Write-Host "Successful:     $successCount" -ForegroundColor Green
Write-Host "Failed:         $failCount" -ForegroundColor $(if ($failCount -eq 0) { "Green" } else { "Red" })

if ($failCount -gt 0) {
    Write-Host ""
    Write-Host "Failed pools:" -ForegroundColor Red
    foreach ($pool in $failedPools) {
        Write-Host "  - $pool" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Output directory: C:\Projects\CoH-Planner\js\data\pools\" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

if ($failCount -eq 0) {
    Write-Host ""
    Write-Host "All pools converted successfully!" -ForegroundColor Green
    exit 0
} else {
    exit 1
}
