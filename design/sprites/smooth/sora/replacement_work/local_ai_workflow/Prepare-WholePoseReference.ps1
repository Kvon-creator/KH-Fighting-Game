$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraReady=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready'
$soraTrial=Join-Path $soraReady 'run_loop/direct_generation_retry_v1'
$soraOriginal=Join-Path $soraTrial 'sora_run_loop_generated_original.png'
$soraSource=Join-Path $soraTrial 'whole_frame_review_v1/sora_run_loop_00.png'
$soraOriginalHash='9d919b4f317981b331010a1ddb049a7807fb8f21ba214d82a40b04291c9065c7'
$soraFrameHash='ece443e9917e8e7dd9ae3a49d39ce30c6d6f8257e2025617f436c4a44dc3461c'
foreach($soraPair in @(@($soraOriginal,$soraOriginalHash),@($soraSource,$soraFrameHash))){if((Get-FileHash -LiteralPath $soraPair[0] -Algorithm SHA256).Hash.ToLowerInvariant() -ne $soraPair[1]){throw 'Source hash differs'}}
$soraOut=Join-Path $soraReady 'run_loop/comfyui_trial/reference_v1'
if(Test-Path -LiteralPath $soraOut){throw 'Preserve reference version'}
Add-Type -AssemblyName System.Drawing
$soraImage=[System.Drawing.Bitmap]::new($soraSource)
if($soraImage.Width -ne 512 -or $soraImage.Height -ne 512){throw 'Unexpected full-pose size'}
New-Item -ItemType Directory -Path $soraOut | Out-Null
$soraFlat=[System.Drawing.Bitmap]::new(512,512,[System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
$soraGraphics=[System.Drawing.Graphics]::FromImage($soraFlat);$soraGraphics.Clear([System.Drawing.Color]::White)
$soraGraphics.DrawImageUnscaled($soraImage,0,0)
$soraTarget=Join-Path $soraOut 'whole_pose_00_white.png'
$soraFlat.Save($soraTarget,[System.Drawing.Imaging.ImageFormat]::Png)
$soraGraphics.Dispose();$soraFlat.Dispose();$soraImage.Dispose()
[ordered]@{status='Complete original pose on white for local model input; not a new drawing';originalSheet=$soraOriginal;originalSha256=$soraOriginalHash;completeRegisteredPose=$soraSource;poseSha256=$soraFrameHash;canvas=@(512,512);operation='Flatten the whole existing RGBA canvas onto white at unchanged resolution/coordinates; no pose modification or component layers';output='whole_pose_00_white.png';outputSha256=(Get-FileHash -LiteralPath $soraTarget -Algorithm SHA256).Hash.ToLowerInvariant()} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $soraOut 'provenance.json') -Encoding UTF8
Write-Output 'Complete source reference prepared on white; original sheet/frame unchanged.'
