$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraReady=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready'
$soraFolder=Join-Path $soraReady 'run_loop/direct_generation_retry_v1/gait_drawing_pilot_v1'
if(Test-Path -LiteralPath $soraFolder){throw 'Preserve existing gait pilot'}
New-Item -ItemType Directory -Path $soraFolder | Out-Null
Add-Type -AssemblyName System.Drawing
$soraBoard=[System.Drawing.Bitmap]::new(1536,552);$soraG=[System.Drawing.Graphics]::FromImage($soraBoard);$soraG.Clear([System.Drawing.Color]::White)
$soraFont=[System.Drawing.Font]::new('Arial',10)
$soraGrid=[System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(110,135,148,158),1)
$soraColumn=0
foreach($soraIndex in @(2,4,8)){
    $soraImage=[System.Drawing.Bitmap]::new((Join-Path $soraReady ('run_loop/direct_generation_retry_v1/whole_frame_review_v1/sora_run_loop_{0:00}.png' -f $soraIndex)))
    $soraG.DrawImageUnscaled($soraImage,$soraColumn*512,0)
    foreach($soraPosition in @(50,100,150,200,250,300,350,400,450)){
        $soraG.DrawLine($soraGrid,$soraColumn*512+$soraPosition,0,$soraColumn*512+$soraPosition,512)
        $soraG.DrawLine($soraGrid,$soraColumn*512,$soraPosition,$soraColumn*512+512,$soraPosition)
        $soraG.DrawString("$soraPosition",$soraFont,[System.Drawing.Brushes]::DarkSlateGray,$soraColumn*512+$soraPosition,5)
        $soraG.DrawString("$soraPosition",$soraFont,[System.Drawing.Brushes]::DarkSlateGray,$soraColumn*512+5,$soraPosition)
    }
    $soraG.DrawString("Whole source $soraIndex - coordinates for new leg drawing",$soraFont,[System.Drawing.Brushes]::Black,$soraColumn*512+12,525)
    $soraImage.Dispose();$soraColumn++
}
$soraBoard.Save((Join-Path $soraFolder 'Native_Leg_Inspection.png'),[System.Drawing.Imaging.ImageFormat]::Png)
$soraG.Dispose();$soraBoard.Dispose();$soraGrid.Dispose();$soraFont.Dispose()
