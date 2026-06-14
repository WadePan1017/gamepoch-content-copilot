$ErrorActionPreference = "Stop"

$baseUrl = "http://localhost:8000"
$checks = @(
    @{ Name = "Home"; Method = "GET"; Url = "$baseUrl/" },
    @{ Name = "Content opportunities"; Method = "GET"; Url = "$baseUrl/api/content/opportunities" },
    @{ Name = "Custom topic generation"; Method = "GET"; Url = "$baseUrl/api/content/topic?q=Elden%20Ring" },
    @{ Name = "Event planner"; Method = "GET"; Url = "$baseUrl/api/events/planner" },
    @{ Name = "Publishing calendar"; Method = "GET"; Url = "$baseUrl/api/content/calendar" },
    @{ Name = "Markdown brief"; Method = "GET"; Url = "$baseUrl/api/content/brief" },
    @{ Name = "Word brief"; Method = "GET"; Url = "$baseUrl/api/content/brief/docx" },
    @{ Name = "Demo status"; Method = "GET"; Url = "$baseUrl/api/demo/status" }
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " GamePoch Content Copilot demo check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$failed = @()

foreach ($check in $checks) {
    try {
        $response = Invoke-WebRequest -Uri $check.Url -Method $check.Method -UseBasicParsing -TimeoutSec 20
        if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300) {
            Write-Host ("[OK]   {0} ({1})" -f $check.Name, $response.StatusCode) -ForegroundColor Green
        } else {
            Write-Host ("[FAIL] {0} ({1})" -f $check.Name, $response.StatusCode) -ForegroundColor Red
            $failed += $check.Name
        }
    } catch {
        Write-Host ("[FAIL] {0} - {1}" -f $check.Name, $_.Exception.Message) -ForegroundColor Red
        $failed += $check.Name
    }
}

try {
    $ops = Invoke-RestMethod -Uri "$baseUrl/api/content/opportunities?refresh=1" -Method GET -TimeoutSec 30
    $body = $ops.hero | ConvertTo-Json -Depth 20
    $pack = Invoke-RestMethod -Uri "$baseUrl/api/content/generate" -Method POST -ContentType "application/json; charset=utf-8" -Body $body -TimeoutSec 30
    $hasUsefulPack = (
        $pack.titles.bilibili.Count -ge 3 -and
        $pack.shot_list.Count -ge 5 -and
        $pack.asset_checklist.Count -ge 5 -and
        $pack.risk_checklist.Count -ge 4 -and
        $pack.publish_copy.douyin -and
        $pack.work_order_markdown
    )
    if ($hasUsefulPack) {
        Write-Host "[OK]   Useful content pack (titles, shots, assets, risks, publish copy, work order)" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Useful content pack is incomplete" -ForegroundColor Red
        $failed += "Useful content pack"
    }
} catch {
    Write-Host ("[FAIL] Useful content pack - {0}" -f $_.Exception.Message) -ForegroundColor Red
    $failed += "Useful content pack"
}

Write-Host ""

if ($failed.Count -eq 0) {
    Write-Host "Demo check passed. Ready to present." -ForegroundColor Green
    Write-Host "Demo URL: $baseUrl" -ForegroundColor Cyan
    exit 0
}

Write-Host "Demo check failed:" -ForegroundColor Red
$failed | ForEach-Object { Write-Host "- $_" -ForegroundColor Red }
Write-Host ""
Write-Host "Please make sure the server is running: python app.py" -ForegroundColor Yellow
exit 1
