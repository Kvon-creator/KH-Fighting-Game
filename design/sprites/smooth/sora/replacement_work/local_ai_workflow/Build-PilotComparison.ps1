param([ValidatePattern('^attempt_[0-9]{2,}$')][string]$Attempt='attempt_01')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraOut=Join-Path $soraRoot "design/sprites/smooth/sora/replacement_work/ready/run_loop/comfyui_trial/$Attempt"
$soraReceipt=Get-Content -LiteralPath (Join-Path $soraOut 'receipt.json') -Raw | ConvertFrom-Json
if($soraReceipt.status -ne 'generated_pending_review' -or $soraReceipt.files.Count -ne 1){throw 'Collect one real whole-pose candidate before comparison'}
$soraReference=[System.IO.Path]::GetFullPath((Join-Path $soraRoot $soraReceipt.reference))
if(-not $soraReference.StartsWith($soraRoot+'\',[System.StringComparison]::OrdinalIgnoreCase)){throw 'Reference escaped workspace'}
$soraCandidate=Join-Path $soraOut 'candidate_00.png'
if((Get-FileHash -LiteralPath $soraCandidate -Algorithm SHA256).Hash.ToLowerInvariant() -ne $soraReceipt.files[0].sha256){throw 'Candidate hash differs'}
if((Get-FileHash -LiteralPath $soraReference -Algorithm SHA256).Hash.ToLowerInvariant() -ne $soraReceipt.referenceSha256){throw 'Reference hash differs'}
$soraTarget=Join-Path $soraOut 'Original_Candidate_Comparison.png'
if(Test-Path -LiteralPath $soraTarget){throw 'Preserve comparison'}
Add-Type -AssemblyName System.Drawing
$soraOriginal=[System.Drawing.Bitmap]::new($soraReference);$soraNew=[System.Drawing.Bitmap]::new($soraCandidate)
if($soraOriginal.Size.Width -ne 512 -or $soraOriginal.Size.Height -ne 512 -or $soraNew.Width -ne 512 -or $soraNew.Height -ne 512){throw 'Unexpected complete canvas sizes'}
$soraBoard=[System.Drawing.Bitmap]::new(1024,570,[System.Drawing.Imaging.PixelFormat]::Format24bppRgb);$soraGraphics=[System.Drawing.Graphics]::FromImage($soraBoard);$soraGraphics.Clear([System.Drawing.Color]::White)
$soraFont=[System.Drawing.Font]::new('Arial',13);$soraSmall=[System.Drawing.Font]::new('Arial',10)
$soraGraphics.DrawImageUnscaled($soraOriginal,0,30);$soraGraphics.DrawImageUnscaled($soraNew,512,30)
$soraGraphics.DrawString('Original whole pose (reference)',$soraFont,[System.Drawing.Brushes]::Black,12,6)
$soraGraphics.DrawString('Local AI candidate (pending review)',$soraFont,[System.Drawing.Brushes]::Black,524,6)
$soraGraphics.DrawString('Backward-arm art test; original legs held. No full-cycle, transparency or final-art approval.',$soraSmall,[System.Drawing.Brushes]::Black,12,546)
$soraBoard.Save($soraTarget,[System.Drawing.Imaging.ImageFormat]::Png)
$soraGraphics.Dispose();$soraBoard.Dispose();$soraOriginal.Dispose();$soraNew.Dispose();$soraFont.Dispose();$soraSmall.Dispose()
Write-Output 'Native-size whole-canvas comparison saved; visual review remains required.'
