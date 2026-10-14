$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraReference=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready/run_loop/comfyui_trial/reference_v1/whole_pose_00_white.png'
if((Get-FileHash -LiteralPath $soraReference -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'a3681849fa6b2a235fd36622866057191f0d073d39ea9cff8b7e30764f6d9022'){throw 'Whole reference changed'}
$soraFolder=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready/run_loop/comfyui_trial/reference_v2'
if(Test-Path -LiteralPath $soraFolder){throw 'Preserve existing temporary selection'}
New-Item -ItemType Directory -Path $soraFolder | Out-Null
Add-Type -AssemblyName System.Drawing
$soraMask=[System.Drawing.Bitmap]::new(512,512,[System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
$soraGraphics=[System.Drawing.Graphics]::FromImage($soraMask)
$soraGraphics.Clear([System.Drawing.Color]::Black)
$soraGraphics.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$soraPoints=@(@(321,231),@(351,243),@(377,264),@(480,267),@(487,319),@(427,327),@(327,337),@(266,313),@(258,269),@(292,248))
$soraPolygon=[System.Drawing.PointF[]]@($soraPoints | ForEach-Object {[System.Drawing.PointF]::new($_[0],$_[1])})
$soraGraphics.FillPolygon([System.Drawing.Brushes]::White,$soraPolygon)
$soraProtected=@(@(125,100,188,140),@(298,100,137,139),@(395,177,90,86))
foreach($soraRect in $soraProtected){$soraGraphics.FillRectangle([System.Drawing.Brushes]::Black,$soraRect[0],$soraRect[1],$soraRect[2],$soraRect[3])}
$soraMaskPath=Join-Path $soraFolder 'temporary_selection.png'
$soraMask.Save($soraMaskPath,[System.Drawing.Imaging.ImageFormat]::Png)
$soraGraphics.Dispose();$soraMask.Dispose()
[ordered]@{role='Temporary inpaint selection on one complete flat canvas; not a component sprite or production layer';sourceWholePose=$soraReference;sourceSha256='a3681849fa6b2a235fd36622866057191f0d073d39ea9cff8b7e30764f6d9022';maskSha256=(Get-FileHash -LiteralPath $soraMaskPath -Algorithm SHA256).Hash.ToLowerInvariant();white='allow model refinement';black='preserve original pixels';protectedRectangles=$soraProtected;poseArtCreated=$false} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $soraFolder 'provenance.json') -Encoding UTF8
Write-Output 'Temporary full-canvas selection saved. Original image unchanged; no new pose generated.'
