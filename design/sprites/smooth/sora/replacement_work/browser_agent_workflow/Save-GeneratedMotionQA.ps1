param([ValidatePattern('^motion_refinement_v[0-9]+$')][string]$Version='motion_refinement_v3')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraReady=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready'
$soraLoop=Join-Path $soraReady "run_loop/direct_generation_retry_v1/$Version"
$soraStop=Join-Path $soraReady "run_stop/direct_generation_retry_v1/$Version"
foreach($soraFolder in @($soraLoop,$soraStop)){if(Test-Path -LiteralPath (Join-Path $soraFolder 'QA_Report.json')){throw 'Preserve previous QA report'}}
$soraRaw=& python (Join-Path $PSScriptRoot 'inspect_generated_motion_study.py') $Version
if($LASTEXITCODE -ne 0){throw 'Read-only image/provenance QA failed'}
$soraViewer=& node (Join-Path $PSScriptRoot 'check_generated_motion_viewer.mjs') (Join-Path $soraLoop 'Review.html')
if($LASTEXITCODE -ne 0){throw 'Offline viewer QA failed'}
$soraReport=$soraRaw | ConvertFrom-Json
$soraReport | Add-Member -NotePropertyName offlineViewerChecks -NotePropertyValue "$soraViewer"
$soraReport | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $soraLoop 'QA_Report.json') -Encoding UTF8
Copy-Item -LiteralPath (Join-Path $soraLoop 'QA_Report.json') -Destination (Join-Path $soraStop 'QA_Report.json')
Write-Output 'Read-only PNG/GIF/provenance and offline viewer checks passed. No actual-browser or Godot test.'
