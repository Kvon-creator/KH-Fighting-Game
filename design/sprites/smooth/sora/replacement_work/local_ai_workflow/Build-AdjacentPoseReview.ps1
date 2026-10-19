param([ValidatePattern('^approved_style_sequence_v[0-9]+$')][string]$Version='approved_style_sequence_v1')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraTrial=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready/run_loop/comfyui_trial'
$soraOut=Join-Path $soraTrial $Version
if(Test-Path -LiteralPath $soraOut){throw 'Preserve previous review'}
$soraFiles=@('attempt_03/final_pose_v1.png','attempt_04/candidate_00.png','attempt_05/candidate_00.png')
if((Get-FileHash -LiteralPath (Join-Path $soraTrial $soraFiles[0]) -Algorithm SHA256).Hash.ToLowerInvariant() -ne '3dd7b620289eaf707973cb71ec05d901637f5251c45d3745f180f657a77b7d2b'){throw 'Approved pilot changed'}
foreach($soraAttempt in @('attempt_04','attempt_05')){
    $soraQa=Get-Content -LiteralPath (Join-Path $soraTrial "$soraAttempt/Adjacent_Pose_QA.json") -Raw | ConvertFrom-Json
    if(-not $soraQa.preservationPassed -or (Get-FileHash -LiteralPath (Join-Path $soraTrial "$soraAttempt/candidate_00.png") -Algorithm SHA256).Hash.ToLowerInvariant() -ne $soraQa.nativeSha256){throw 'Pose preservation/hash check failed'}
    $soraReview=Get-Content -LiteralPath (Join-Path $soraTrial "$soraAttempt/art_review.json") -Raw | ConvertFrom-Json
    if($soraReview.status -ne 'internal_adjacent_pose_review_passed'){throw 'Inspect native artwork before packaging'}
}
Add-Type -AssemblyName System.Drawing
Add-Type -Path (Join-Path $PSScriptRoot '../AnimationPackaging.cs') -ReferencedAssemblies System.Drawing
New-Item -ItemType Directory -Path $soraOut | Out-Null
$soraImages=[System.Collections.Generic.List[System.Drawing.Bitmap]]::new()
$soraRecords=@();$soraPhases=@('Approved contact anchor','Compression / arm descends','Early passing / arm forward')
$soraBoard=[System.Drawing.Bitmap]::new(1536,570,[System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
$soraG=[System.Drawing.Graphics]::FromImage($soraBoard);$soraG.Clear([System.Drawing.Color]::White)
$soraFont=[System.Drawing.Font]::new('Arial',13)
for($soraIndex=0;$soraIndex -lt 3;$soraIndex++){
    $soraFile='sora_run_loop_{0:d2}.png' -f $soraIndex
    Copy-Item -LiteralPath (Join-Path $soraTrial $soraFiles[$soraIndex]) -Destination (Join-Path $soraOut $soraFile)
    $soraImage=[System.Drawing.Bitmap]::new((Join-Path $soraOut $soraFile));$soraImages.Add($soraImage)
    $soraG.DrawImageUnscaled($soraImage,$soraIndex*512,34)
    $soraG.DrawString($soraPhases[$soraIndex],$soraFont,[System.Drawing.Brushes]::Black,$soraIndex*512+10,8)
    $soraRecords += [ordered]@{index=$soraIndex;file=$soraFile;phase=$soraPhases[$soraIndex];durationMs=80;source=$soraFiles[$soraIndex];sha256=(Get-FileHash -LiteralPath (Join-Path $soraOut $soraFile) -Algorithm SHA256).Hash.ToLowerInvariant();original=('../../direct_generation_retry_v1/whole_frame_review_v1/sora_run_loop_{0:d2}.png' -f $soraIndex)}
}
$soraBoard.Save((Join-Path $soraOut 'Contact_Sheet.png'),[System.Drawing.Imaging.ImageFormat]::Png)
[AnimationPackaging]::Gif((Join-Path $soraOut 'Three_Pose_Once.gif'),$soraImages.ToArray(),[int[]]@(80,80,80),$false)
[AnimationPackaging]::Gif((Join-Path $soraOut 'Three_Pose_Slow_Once.gif'),$soraImages.ToArray(),[int[]]@(320,320,320),$false)
$soraHtml=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'adjacent_review_template.html') -Raw
$soraHtml=$soraHtml.Replace('__SEQUENCE_JSON__',($soraRecords | ConvertTo-Json -Depth 4 -Compress))
$soraHtml | Set-Content -LiteralPath (Join-Path $soraOut 'Review.html') -Encoding UTF8
[ordered]@{status='Three complete poses in the approved visual treatment; unfinished partial running study';frameCount=3;loop=$false;durationMs=240;canvas=@(512,512);background='opaque white';componentProductionLayers=$false;frames=$soraRecords;remaining='Full alternating gait, later phases, wrap/start/stop joins, cloth/chain follow-through, transparent export, final motion approval and engine integration';browserPlaybackTested=$false;godotIntegrated=$false} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $soraOut 'manifest.json') -Encoding UTF8
$soraG.Dispose();$soraBoard.Dispose();$soraFont.Dispose();foreach($soraImage in $soraImages){$soraImage.Dispose()}
Write-Output "Three-pose once-only review saved in $Version. This is not a complete loop."
