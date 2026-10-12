param([ValidatePattern('^motion_refinement_v[0-9]+$')][string]$Version='motion_refinement_v4')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraReady=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready'
$soraOutput=Join-Path $soraReady "run_loop/direct_generation_retry_v1/$Version/Original_Refinement_Comparison.png"
if(Test-Path -LiteralPath $soraOutput){throw 'Preserve existing comparison'}
Add-Type -AssemblyName System.Drawing
$soraCanvas=[System.Drawing.Bitmap]::new(2048,1160);$soraGraphics=[System.Drawing.Graphics]::FromImage($soraCanvas);$soraGraphics.Clear([System.Drawing.Color]::White)
$soraFont=[System.Drawing.Font]::new('Arial',16)
foreach($soraRow in @(0,1)){
    $soraPairs=if($soraRow -eq 0){@(@('run_loop',0),@('run_stop',0))}else{@(@('run_loop',5),@('run_stop',4))}
    for($soraPair=0;$soraPair -lt 2;$soraPair++){
        $soraAnimation=$soraPairs[$soraPair][0];$soraIndex=$soraPairs[$soraPair][1]
        $soraFile=('sora_{0}_{1:00}.png' -f $soraAnimation,$soraIndex)
        for($soraSide=0;$soraSide -lt 2;$soraSide++){
            $soraFolder=if($soraSide -eq 0){'whole_frame_review_v1'}else{$Version}
            $soraImage=[System.Drawing.Bitmap]::new((Join-Path $soraReady "$soraAnimation/direct_generation_retry_v1/$soraFolder/$soraFile"))
            $soraX=($soraPair*2+$soraSide)*512;$soraY=$soraRow*580
            $soraGraphics.DrawImageUnscaled($soraImage,$soraX,$soraY+36)
            $soraTitle=if($soraSide -eq 0){"$soraAnimation $soraIndex - original order"}else{"$soraAnimation $soraIndex - refinement study"}
            $soraGraphics.DrawString($soraTitle,$soraFont,[System.Drawing.Brushes]::Black,$soraX+12,$soraY+8)
            $soraImage.Dispose()
        }
    }
}
$soraGraphics.DrawString('Run: articulated free arm. Stop: selected complete carry poses; new braking drawings remain unfinished.',$soraFont,[System.Drawing.Brushes]::Black,12,1130)
$soraCanvas.Save($soraOutput,[System.Drawing.Imaging.ImageFormat]::Png)
$soraGraphics.Dispose();$soraCanvas.Dispose();$soraFont.Dispose()
Write-Output $soraOutput
