param([ValidatePattern('^gait_drawing_pilot_v[0-9]+$')][string]$Version='gait_drawing_pilot_v2')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraReady=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready'
$soraOut=Join-Path $soraReady "run_loop/direct_generation_retry_v1/$Version"
if(Test-Path -LiteralPath $soraOut){throw 'Preserve previous gait pilot'}
$soraBody=Join-Path $soraReady 'run_loop/direct_generation_retry_v1/motion_refinement_v4/sora_run_loop_02.png'
$soraClothes=Join-Path $soraReady 'run_loop/direct_generation_retry_v1/whole_frame_review_v1/sora_run_loop_02.png'
$soraBoots=Join-Path $soraReady 'run_loop/direct_generation_retry_v1/whole_frame_review_v1/sora_run_loop_00.png'
$soraHashes=@($soraBody,$soraClothes,$soraBoots | ForEach-Object {(Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash.ToLowerInvariant()})
Add-Type -AssemblyName System.Drawing
Add-Type -Path (Join-Path $PSScriptRoot 'GeneratedGaitPainting.cs') -ReferencedAssemblies System.Drawing
$soraNear=[System.Drawing.PointF]::new(315,371)
$soraFar=[System.Drawing.PointF]::new(278,(470-[GeneratedGaitPainting]::SoleOffset($soraBoots,0)))
# Validate leg reach before creating output.
[GeneratedGaitPainting]::Knee([System.Drawing.PointF]::new(272,312),$soraNear,$true) | Out-Null
[GeneratedGaitPainting]::Knee([System.Drawing.PointF]::new(291,321),$soraFar,$false) | Out-Null
New-Item -ItemType Directory -Path $soraOut | Out-Null
$soraFile=Join-Path $soraOut 'sora_near_passing_pilot.png'
$soraJoints=[GeneratedGaitPainting]::Paint($soraBody,$soraClothes,$soraBoots,$soraFile,-4,$soraNear,-35,$soraFar,0)
$soraBoard=[System.Drawing.Bitmap]::new(1536,560);$soraG=[System.Drawing.Graphics]::FromImage($soraBoard);$soraG.Clear([System.Drawing.Color]::White)
$soraFont=[System.Drawing.Font]::new('Arial',14)
$soraFiles=@($soraBody,$soraFile,(Join-Path $soraReady 'run_loop/direct_generation_retry_v1/motion_refinement_v4/sora_run_loop_03.png'))
$soraTitles=@('Existing pose02','New passing-leg pilot - inspect finish','Existing pose03')
for($soraColumn=0;$soraColumn -lt 3;$soraColumn++){
    $soraImage=[System.Drawing.Bitmap]::new($soraFiles[$soraColumn]);$soraG.DrawImageUnscaled($soraImage,$soraColumn*512,0)
    $soraG.DrawString($soraTitles[$soraColumn],$soraFont,[System.Drawing.Brushes]::Black,$soraColumn*512+10,523);$soraImage.Dispose()
}
$soraBoard.Save((Join-Path $soraOut 'Passing_Pose_Comparison.png'),[System.Drawing.Imaging.ImageFormat]::Png)
$soraG.Dispose();$soraBoard.Dispose();$soraFont.Dispose()
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'GeneratedGaitPainting.cs') -Destination (Join-Path $soraOut 'Flat_Gait_Painter_Source.cs')
[ordered]@{status='New leg drawing pilot; not inserted into the cycle';bodyShiftY=-4;protectedUpperExclusiveY=266;nearShoeAngle=-35;farShoeAngle=0;joints=@($soraJoints | ForEach-Object {,@($_.X,$_.Y)});nearThigh=[GeneratedGaitPainting]::NearThigh;nearShin=[GeneratedGaitPainting]::NearShin;farThigh=[GeneratedGaitPainting]::FarThigh;farShin=[GeneratedGaitPainting]::FarShin;sourceFiles=@($soraBody,$soraClothes,$soraBoots);sourceHashes=$soraHashes;file='sora_near_passing_pilot.png';sha256=(Get-FileHash -LiteralPath $soraFile -Algorithm SHA256).Hash.ToLowerInvariant();method='One complete canvas, new fixed-length leg joints and direct garment/calf contours; complete PNG clothing/shoe reference brushes; no part rasters, scaling or production layers'} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $soraOut 'manifest.json') -Encoding UTF8
Write-Output 'New complete passing-leg pilot created; inspect native finish, sole and silhouette before insertion.'
