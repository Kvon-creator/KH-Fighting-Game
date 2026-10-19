param([ValidatePattern('^adjacent_guides_v[0-9]+$')][string]$Version='adjacent_guides_v1')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraReady=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready'
$soraTrial=Join-Path $soraReady 'run_loop/comfyui_trial'
$soraSources=Join-Path $soraReady 'run_loop/direct_generation_retry_v1/whole_frame_review_v1'
$soraPilot=Join-Path $soraTrial 'attempt_03/final_pose_v1.png'
$soraOriginal=Join-Path $soraTrial 'reference_v1/whole_pose_00_white.png'
$soraChecks=@(@($soraPilot,'3dd7b620289eaf707973cb71ec05d901637f5251c45d3745f180f657a77b7d2b'),@($soraOriginal,'a3681849fa6b2a235fd36622866057191f0d073d39ea9cff8b7e30764f6d9022'))
foreach($soraPair in $soraChecks){if((Get-FileHash -LiteralPath $soraPair[0] -Algorithm SHA256).Hash.ToLowerInvariant() -ne $soraPair[1]){throw 'Approved pilot/source changed'}}
$soraOut=Join-Path $soraTrial $Version
if(Test-Path -LiteralPath $soraOut){throw 'Preserve existing guide version'}
Add-Type -AssemblyName System.Drawing
Add-Type -Path (Join-Path $PSScriptRoot 'AdjacentRunPainting.cs') -ReferencedAssemblies System.Drawing
New-Item -ItemType Directory -Path $soraOut | Out-Null
$soraFrames=@()
foreach($soraIndex in @(1,2)){
    $soraName='pose_{0:d2}' -f $soraIndex
    $soraFolder=Join-Path $soraOut $soraName
    New-Item -ItemType Directory -Path $soraFolder | Out-Null
    $soraSource=Join-Path $soraSources ('sora_run_loop_{0:d2}.png' -f $soraIndex)
    $soraBob=if($soraIndex -eq 1){3}else{1}
    [AdjacentRunGuide]::Paint($soraPilot,$soraOriginal,$soraSource,(Join-Path $soraFolder 'whole_pose_guide.png'),(Join-Path $soraFolder 'temporary_selection.png'),$soraIndex,$soraBob)
    $soraFrames += [ordered]@{index=$soraIndex;phase=if($soraIndex -eq 1){'compression after approved contact'}else{'early passing after compression'};source=$soraSource;sourceSha256=(Get-FileHash -LiteralPath $soraSource -Algorithm SHA256).Hash.ToLowerInvariant();bodyShiftY=$soraBob;guide="$soraName/whole_pose_guide.png";guideSha256=(Get-FileHash -LiteralPath (Join-Path $soraFolder 'whole_pose_guide.png') -Algorithm SHA256).Hash.ToLowerInvariant();mask="$soraName/temporary_selection.png";maskSha256=(Get-FileHash -LiteralPath (Join-Path $soraFolder 'temporary_selection.png') -Algorithm SHA256).Hash.ToLowerInvariant();protectedRectangles=@(@(125,(100+$soraBob),188,140),@(298,(100+$soraBob),137,139),@(404,(177+$soraBob),81,80))}
}
[ordered]@{status='Complete flat chronological guides; inspect before model submission';approvedAnchor=$soraPilot;approvedAnchorSha256=$soraChecks[0][1];originalWholePose=$soraOriginal;method='Whole source canvases and temporary selections on a single flat output; new articulated free arms; unchanged-resolution original01/02 leg drawings; whole upper carry integer bob';componentProductionLayers=$false;scaledPoseCopies=$false;frames=$soraFrames} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $soraOut 'provenance.json') -Encoding UTF8
Write-Output "Two complete flat guides saved in $Version; visual review required."
