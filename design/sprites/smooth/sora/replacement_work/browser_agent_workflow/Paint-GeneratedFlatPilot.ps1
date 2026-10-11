param([ValidatePattern('^flat_refinement_pilot_v[0-9]+$')][string]$Version='flat_refinement_pilot_v1')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraReady=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready'
$soraReference=Join-Path $soraReady 'run_loop/direct_generation_retry_v1/whole_frame_review_v1/sora_run_loop_00.png'
foreach($soraAnimation in @('run_loop','run_stop')){if(Test-Path -LiteralPath (Join-Path $soraReady "$soraAnimation/direct_generation_retry_v1/$Version")){throw 'Preserve prior pilot'}}
Add-Type -AssemblyName System.Drawing
Add-Type -Path (Join-Path $PSScriptRoot 'GeneratedFlatRefinement.cs') -ReferencedAssemblies System.Drawing
$soraBoard=[System.Drawing.Bitmap]::new(1536,1080);$soraGraphics=[System.Drawing.Graphics]::FromImage($soraBoard);$soraGraphics.Clear([System.Drawing.Color]::White)
$soraFont=[System.Drawing.Font]::new('Arial',13)
$soraExamples=@(@('run_loop',0,115,-105),@('run_loop',5,35,-60),@('run_stop',4,65,-70))
$soraColumn=0
foreach($soraExample in $soraExamples){
    $soraAnimation=$soraExample[0];$soraIndex=[int]$soraExample[1];$soraFile=('sora_{0}_{1:00}.png' -f $soraAnimation,$soraIndex)
    $soraFolder=Join-Path $soraReady "$soraAnimation/direct_generation_retry_v1/$Version"
    if(-not(Test-Path -LiteralPath $soraFolder)){New-Item -ItemType Directory -Path $soraFolder | Out-Null}
    if(-not(Test-Path -LiteralPath (Join-Path $soraFolder 'Flat_Painter_Source.cs'))){Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'GeneratedFlatRefinement.cs') -Destination (Join-Path $soraFolder 'Flat_Painter_Source.cs')}
    $soraSource=Join-Path $soraReady "$soraAnimation/direct_generation_retry_v1/whole_frame_review_v1/$soraFile"
    $soraTarget=Join-Path $soraFolder $soraFile
    $soraRaw=[GeneratedFlatRefinement]::Paint($soraSource,$soraReference,$soraTarget,$soraExample[2],$soraExample[3],$false,($soraAnimation -eq 'run_stop'))
    $soraOriginal=[System.Drawing.Bitmap]::new($soraSource);$soraResult=[System.Drawing.Bitmap]::new($soraTarget)
    $soraGraphics.DrawImageUnscaled($soraOriginal,$soraColumn*512,0);$soraGraphics.DrawImageUnscaled($soraResult,$soraColumn*512,540)
    $soraGraphics.DrawString("$soraAnimation $soraIndex original",$soraFont,[System.Drawing.Brushes]::Black,$soraColumn*512+15,512)
    $soraGraphics.DrawString("Flat pilot: inspect seams",$soraFont,[System.Drawing.Brushes]::Black,$soraColumn*512+15,1052)
    $soraOriginal.Dispose();$soraResult.Dispose();$soraColumn++
    Write-Output "$soraAnimation $soraIndex joints: $soraRaw"
}
$soraBoard.Save((Join-Path $soraReady "run_loop/direct_generation_retry_v1/$Version/Pilot_Comparison.png"),[System.Drawing.Imaging.ImageFormat]::Png)
$soraGraphics.Dispose();$soraBoard.Dispose();$soraFont.Dispose()
