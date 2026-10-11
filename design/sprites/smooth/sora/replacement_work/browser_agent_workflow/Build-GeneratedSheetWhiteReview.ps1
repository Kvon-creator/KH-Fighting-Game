param([Parameter(Mandatory=$true)][string]$Animation,[string]$Version='direct_generation_retry_v1',[Parameter(Mandatory=$true)][string]$SourceFile)
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
if($Animation -notin @('run_loop','run_stop')){throw 'Unsupported animation'}
if($Version -notmatch '^direct_generation_retry_v[0-9]+$'){throw 'Unexpected trial version'}
if($SourceFile -notmatch '^sora_run_(loop|stop)_[a-z_]+\.png$'){throw 'Unexpected source name'}
$soraFolder=Join-Path $soraRoot "design/sprites/smooth/sora/replacement_work/ready/$Animation/$Version"
$soraSource=Join-Path $soraFolder $SourceFile
$soraOutput=Join-Path $soraFolder ($SourceFile.Replace('.png','_White_Review.png'))
if(Test-Path -LiteralPath $soraOutput){throw 'Preserve existing review'}
$soraHash=(Get-FileHash -LiteralPath $soraSource -Algorithm SHA256).Hash
Add-Type -AssemblyName System.Drawing
$soraOriginal=[System.Drawing.Bitmap]::new($soraSource)
$soraReview=[System.Drawing.Bitmap]::new($soraOriginal.Width,$soraOriginal.Height)
$soraGraphics=[System.Drawing.Graphics]::FromImage($soraReview)
$soraGraphics.Clear([System.Drawing.Color]::White)
$soraGraphics.DrawImageUnscaled($soraOriginal,0,0)
$soraReview.Save($soraOutput,[System.Drawing.Imaging.ImageFormat]::Png)
$soraGraphics.Dispose();$soraReview.Dispose();$soraOriginal.Dispose()
if((Get-FileHash -LiteralPath $soraSource -Algorithm SHA256).Hash -ne $soraHash){throw 'Review changed native original'}
Write-Output 'White-background alpha-composited review saved; generated source unchanged.'
