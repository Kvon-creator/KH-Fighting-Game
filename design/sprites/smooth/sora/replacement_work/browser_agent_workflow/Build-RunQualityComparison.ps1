param([ValidatePattern('^quality_refinement_v[0-9]+$')][string]$Version='quality_refinement_v4')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraReady=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready'
$soraOut=Join-Path $soraReady "run_loop/$Version"
if(Test-Path -LiteralPath (Join-Path $soraOut 'Benchmark_Comparison.png')){throw 'Preserve existing comparison'}
Add-Type -AssemblyName System.Drawing
$soraPaths=@(
    'run_start/sync_refinement_v2/flat_lift_pilot_v5/full_start_study/frame_11.png','run_loop/flat_cycle_v5/sora_run_loop_00.png',"run_loop/$Version/sora_run_loop_00.png",
    'run_start/sync_refinement_v2/flat_lift_pilot_v5/full_start_study/frame_12.png','run_loop/flat_cycle_v5/sora_run_loop_14.png',"run_loop/$Version/sora_run_loop_14.png",
    'run_start/sync_refinement_v2/flat_lift_pilot_v5/full_start_study/frame_00.png','run_stop/flat_stop_v5/sora_run_stop_15.png',"run_stop/$Version/sora_run_stop_15.png"
)
$soraLabels=@('Run-start reference: reach','Previous run contact','Refined run contact','Run-start reference: flight','Previous run flight','Refined run flight','Run-start reference: ready','Previous stop guard','Refined stop guard')
$soraHashes=@($soraPaths | ForEach-Object {(Get-FileHash -LiteralPath (Join-Path $soraReady $_) -Algorithm SHA256).Hash})
$soraBoard=[System.Drawing.Bitmap]::new(1536,1626)
$soraG=[System.Drawing.Graphics]::FromImage($soraBoard)
$soraG.Clear([System.Drawing.Color]::White)
$soraFont=[System.Drawing.Font]::new('Arial',14)
for($soraIndex=0;$soraIndex -lt 9;$soraIndex++){
    $soraImage=[System.Drawing.Bitmap]::new((Join-Path $soraReady $soraPaths[$soraIndex]))
    $soraX=($soraIndex%3)*512;$soraY=[Math]::Floor($soraIndex/3)*542
    $soraG.DrawImageUnscaled($soraImage,$soraX,$soraY)
    $soraG.DrawString($soraLabels[$soraIndex],$soraFont,[System.Drawing.Brushes]::Black,$soraX+8,$soraY+514)
    $soraImage.Dispose()
}
$soraBoard.Save((Join-Path $soraOut 'Benchmark_Comparison.png'),[System.Drawing.Imaging.ImageFormat]::Png)
$soraG.Dispose();$soraBoard.Dispose();$soraFont.Dispose()
for($soraIndex=0;$soraIndex -lt 9;$soraIndex++){if((Get-FileHash -LiteralPath (Join-Path $soraReady $soraPaths[$soraIndex]) -Algorithm SHA256).Hash -ne $soraHashes[$soraIndex]){throw 'Comparison changed a source'}}
[ordered]@{status='visual style comparison; different poses, not a quantitative style-match certificate';nativeCanvas=512;allFiguresUnscaled=$true;inputs=$soraPaths;hashes=$soraHashes;benchmark='Run_Start_13_Once.gif';remaining='New anatomy, occlusion, surface projection and final idle join require visual review.'} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $soraOut 'comparison_manifest.json') -Encoding UTF8
$soraHtmlPath=Join-Path $soraOut 'Review.html'
$soraHtml=Get-Content -LiteralPath $soraHtmlPath -Raw
$soraHtml=$soraHtml.Replace('16 alternating strides, then 16 braking and guard-recovery drawings.','16 run poses and16 braking/guard-recovery drawings. Compare the fuller clothing and native material detail with the run-start reference.')
$soraHtml=$soraHtml.Replace('<select id="kind">','<p><a href="Benchmark_Comparison.png" style="color:#a8d5ff">Open full-size reference / previous / refined comparison</a></p><select id="kind">')
[System.IO.File]::WriteAllText($soraHtmlPath,$soraHtml.TrimEnd()+[Environment]::NewLine,[System.Text.UTF8Encoding]::new($false))
Write-Output 'Native-size3-column comparison created; original benchmark and input images unchanged.'
