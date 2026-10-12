param([ValidatePattern('^gait_cycle_study_v[0-9]+$')][string]$Version='gait_cycle_study_v4')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraTrial=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready/run_loop/direct_generation_retry_v1'
$soraOut=Join-Path $soraTrial $Version
if(Test-Path -LiteralPath (Join-Path $soraOut 'QA_Report.json')){throw 'Preserve existing QA'}
$soraRaster=(& python (Join-Path $PSScriptRoot 'inspect_generated_gait_cycle.py') $Version) -join [Environment]::NewLine
if($LASTEXITCODE -ne 0){throw 'Read-only gait QA failed'}
$soraReport=$soraRaster | ConvertFrom-Json
$soraViewer=(& node (Join-Path $PSScriptRoot 'check_generated_gait_viewer.mjs') (Join-Path $soraOut 'Review.html')) -join [Environment]::NewLine
if($LASTEXITCODE -ne 0){throw 'Offline viewer QA failed'}
$soraReport | Add-Member -NotePropertyName offlineViewerChecks -NotePropertyValue $soraViewer
$soraReport | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $soraOut 'QA_Report.json') -Encoding UTF8
$soraNear=Join-Path $soraTrial 'near_stride_study_v2'
if(-not (Test-Path -LiteralPath (Join-Path $soraNear 'QA_Report.json'))){
    $soraNearReport=(& python (Join-Path $PSScriptRoot 'inspect_generated_near_stride.py') 'near_stride_study_v2') -join [Environment]::NewLine
    if($LASTEXITCODE -ne 0){throw 'Read-only partial-stride QA failed'}
    $soraNearReport | Set-Content -LiteralPath (Join-Path $soraNear 'QA_Report.json') -Encoding UTF8
}
$soraMax=($soraReport.cyclicAnkleStepMeasurements | ForEach-Object {$_.nearAnkleDistance;$_.farAnkleDistance} | Measure-Object -Maximum).Maximum
Write-Output "Verified $($soraReport.distinctWholeDrawings) whole drawings; largest adjacent ankle gap $soraMax px. Offline viewer passed; no actual-browser/Godot test."
