param([ValidateSet('reference_v2','reference_v4','reference_v5','reference_v6')][string]$Version='reference_v2')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraReference=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready/run_loop/comfyui_trial/reference_v1/whole_pose_00_white.png'
if((Get-FileHash -LiteralPath $soraReference -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'a3681849fa6b2a235fd36622866057191f0d073d39ea9cff8b7e30764f6d9022'){throw 'Whole reference changed'}
$soraFolder=Join-Path $soraRoot "design/sprites/smooth/sora/replacement_work/ready/run_loop/comfyui_trial/$Version"
if(Test-Path -LiteralPath $soraFolder){throw 'Preserve existing temporary selection'}
New-Item -ItemType Directory -Path $soraFolder | Out-Null
Add-Type -AssemblyName System.Drawing
$soraMask=[System.Drawing.Bitmap]::new(512,512,[System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
$soraGraphics=[System.Drawing.Graphics]::FromImage($soraMask)
$soraGraphics.Clear([System.Drawing.Color]::Black)
$soraGraphics.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$soraPoints=@(@(321,231),@(351,243),@(377,264),@(480,267),@(487,319),@(427,327),@(327,337),@(266,313),@(258,269),@(292,248))
if($Version -eq 'reference_v4'){$soraPoints=@(@(321,231),@(351,243),@(377,250),@(490,250),@(496,327),@(427,337),@(327,337),@(266,313),@(258,269),@(292,248))}
if($Version -in @('reference_v5','reference_v6')){$soraPoints=@(@(321,231),@(351,240),@(397,240),@(490,250),@(496,327),@(427,337),@(327,337),@(266,313),@(258,269),@(292,248))}
$soraPolygon=[System.Drawing.PointF[]]@($soraPoints | ForEach-Object {[System.Drawing.PointF]::new($_[0],$_[1])})
$soraGraphics.FillPolygon([System.Drawing.Brushes]::White,$soraPolygon)
$soraProtected=@(@(125,100,188,140),@(298,100,137,139),@(395,177,90,86))
if($Version -eq 'reference_v4'){$soraProtected=@(@(125,100,188,140),@(298,100,137,139),@(395,177,90,80))}
if($Version -in @('reference_v5','reference_v6')){$soraProtected=@(@(125,100,188,140),@(298,100,137,139),@(404,177,81,80))}
foreach($soraRect in $soraProtected){$soraGraphics.FillRectangle([System.Drawing.Brushes]::Black,$soraRect[0],$soraRect[1],$soraRect[2],$soraRect[3])}
$soraGraphics.Dispose()
# Antialiased rectangle edges must not leak refinement into protected pixels.
foreach($soraRect in $soraProtected){for($soraY=$soraRect[1];$soraY -lt $soraRect[1]+$soraRect[3];$soraY++){for($soraX=$soraRect[0];$soraX -lt $soraRect[0]+$soraRect[2];$soraX++){$soraMask.SetPixel($soraX,$soraY,[System.Drawing.Color]::Black)}}}
$soraMaskPath=Join-Path $soraFolder 'temporary_selection.png'
$soraMask.Save($soraMaskPath,[System.Drawing.Imaging.ImageFormat]::Png)
$soraMask.Dispose()
[ordered]@{role='Temporary inpaint selection on one complete flat canvas; not a component sprite or production layer';sourceWholePose=$soraReference;sourceSha256='a3681849fa6b2a235fd36622866057191f0d073d39ea9cff8b7e30764f6d9022';maskSha256=(Get-FileHash -LiteralPath $soraMaskPath -Algorithm SHA256).Hash.ToLowerInvariant();white='allow model refinement';black='preserve original pixels';protectedRectangles=$soraProtected;poseArtCreated=$false} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $soraFolder 'provenance.json') -Encoding UTF8
Write-Output 'Temporary full-canvas selection saved. Original image unchanged; no new pose generated.'
