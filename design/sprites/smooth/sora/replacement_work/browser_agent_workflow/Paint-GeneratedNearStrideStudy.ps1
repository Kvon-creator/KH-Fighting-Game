param([ValidatePattern('^near_stride_study_v[0-9]+$')][string]$Version='near_stride_study_v1')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraReady=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready'
$soraOut=Join-Path $soraReady "run_loop/direct_generation_retry_v1/$Version"
if(Test-Path -LiteralPath $soraOut){throw 'Preserve previous stride study'}
$soraBody=Join-Path $soraReady 'run_loop/direct_generation_retry_v1/motion_refinement_v4/sora_run_loop_02.png'
$soraClothes=Join-Path $soraReady 'run_loop/direct_generation_retry_v1/whole_frame_review_v1/sora_run_loop_02.png'
$soraBoots=Join-Path $soraReady 'run_loop/direct_generation_retry_v1/whole_frame_review_v1/sora_run_loop_00.png'
$soraHashes=@($soraBody,$soraClothes,$soraBoots | ForEach-Object {(Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash.ToLowerInvariant()})
Add-Type -AssemblyName System.Drawing
Add-Type -Path (Join-Path $PSScriptRoot 'GeneratedGaitPainting.cs') -ReferencedAssemblies System.Drawing
Add-Type -Path (Join-Path $PSScriptRoot '../AnimationPackaging.cs') -ReferencedAssemblies System.Drawing
$soraSole=[GeneratedGaitPainting]::SoleOffset($soraBoots,0)
$soraPlan=@(
    @{phase='near leg passing';shift=-4;near=@(315,371);far=@(278,(470-$soraSole));nearAngle=-35;farAngle=0;support='far'},
    @{phase='near leg reaching in flight';shift=-8;near=@(352,387);far=@(230,358);nearAngle=-20;farAngle=25;support='none'},
    @{phase='near leg contact';shift=-2;near=@(353,(470-$soraSole));far=@(213,360);nearAngle=0;farAngle=35;support='near'}
)
foreach($soraPose in $soraPlan){
    [GeneratedGaitPainting]::Knee([System.Drawing.PointF]::new(272,316+$soraPose.shift),[System.Drawing.PointF]::new($soraPose.near[0],$soraPose.near[1]),$true) | Out-Null
    [GeneratedGaitPainting]::Knee([System.Drawing.PointF]::new(291,325+$soraPose.shift),[System.Drawing.PointF]::new($soraPose.far[0],$soraPose.far[1]),$false) | Out-Null
}
New-Item -ItemType Directory -Path $soraOut,(Join-Path $soraOut 'frames_128') | Out-Null
$soraBoard=[System.Drawing.Bitmap]::new(1536,560);$soraG=[System.Drawing.Graphics]::FromImage($soraBoard);$soraG.Clear([System.Drawing.Color]::White)
$soraFont=[System.Drawing.Font]::new('Arial',13);$soraLarge=[System.Collections.Generic.List[System.Drawing.Bitmap]]::new();$soraSmall=[System.Collections.Generic.List[System.Drawing.Bitmap]]::new()
$soraRecords=[System.Collections.Generic.List[object]]::new()
for($soraIndex=0;$soraIndex -lt 3;$soraIndex++){
    $soraPose=$soraPlan[$soraIndex];$soraFile=('sora_near_stride_{0:00}.png' -f $soraIndex);$soraTarget=Join-Path $soraOut $soraFile
    $soraJoints=[GeneratedGaitPainting]::Paint($soraBody,$soraClothes,$soraBoots,$soraTarget,$soraPose.shift,[System.Drawing.PointF]::new($soraPose.near[0],$soraPose.near[1]),$soraPose.nearAngle,[System.Drawing.PointF]::new($soraPose.far[0],$soraPose.far[1]),$soraPose.farAngle)
    $soraImage=[System.Drawing.Bitmap]::new($soraTarget);$soraG.DrawImageUnscaled($soraImage,$soraIndex*512,0)
    $soraG.DrawString($soraPose.phase,$soraFont,[System.Drawing.Brushes]::Black,$soraIndex*512+12,520)
    foreach($soraSize in @(512,128)){
        $soraFlat=[System.Drawing.Bitmap]::new($soraSize,$soraSize);$soraGraphics=[System.Drawing.Graphics]::FromImage($soraFlat);$soraGraphics.Clear([System.Drawing.Color]::White)
        $soraGraphics.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic;$soraGraphics.DrawImage($soraImage,0,0,$soraSize,$soraSize);$soraGraphics.Dispose()
        if($soraSize -eq 512){$soraLarge.Add($soraFlat)}else{$soraSmall.Add($soraFlat)}
    }
    $soraGame=[System.Drawing.Bitmap]::new(128,128,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb);$soraGraphics=[System.Drawing.Graphics]::FromImage($soraGame)
    $soraGraphics.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic;$soraGraphics.DrawImage($soraImage,0,0,128,128);$soraGraphics.Dispose()
    $soraGame.Save((Join-Path $soraOut "frames_128/$soraFile"),[System.Drawing.Imaging.ImageFormat]::Png)
    $soraRecords.Add([pscustomobject][ordered]@{index=$soraIndex;file=$soraFile;phase=$soraPose.phase;durationMs=100;bodyShiftY=$soraPose.shift;protectedUpperExclusiveY=270+$soraPose.shift;support=$soraPose.support;nearShoeAngle=$soraPose.nearAngle;farShoeAngle=$soraPose.farAngle;joints=@($soraJoints | ForEach-Object {,@($_.X,$_.Y)});sha256=(Get-FileHash -LiteralPath $soraTarget -Algorithm SHA256).Hash.ToLowerInvariant()})
    $soraGame.Dispose();$soraImage.Dispose()
}
$soraBoard.Save((Join-Path $soraOut 'Near_Stride_Contact_Sheet.png'),[System.Drawing.Imaging.ImageFormat]::Png)
foreach($soraSize in @(512,128)){
    $soraFrames=if($soraSize -eq 512){$soraLarge.ToArray()}else{$soraSmall.ToArray()}
    $soraGif=Join-Path $soraOut "Near_Stride_${soraSize}_Once.gif";[AnimationPackaging]::Gif($soraGif,$soraFrames,[int[]]@(100,100,100))
    $soraBytes=[System.IO.File]::ReadAllBytes($soraGif)
    if([System.Text.Encoding]::ASCII.GetString($soraBytes,16,11) -ne 'NETSCAPE2.0'){throw 'Unexpected GIF header'}
    [System.IO.File]::WriteAllBytes($soraGif,[byte[]]($soraBytes[0..12]+$soraBytes[32..($soraBytes.Length-1)]))
}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'GeneratedGaitPainting.cs') -Destination (Join-Path $soraOut 'Flat_Gait_Painter_Source.cs')
[ordered]@{status='New opposite-leg drawings; partial stride study, not inserted into full loop';frameCount=3;canvas=@(512,512);gameExport=@(128,128);durationMs=300;loop=$false;nearThigh=[GeneratedGaitPainting]::NearThigh;nearShin=[GeneratedGaitPainting]::NearShin;farThigh=[GeneratedGaitPainting]::FarThigh;farShin=[GeneratedGaitPainting]::FarShin;sourceFiles=@($soraBody,$soraClothes,$soraBoots);sourceHashes=$soraHashes;frames=$soraRecords.ToArray();method='One complete canvas per pose; new curved garments, calf drawings and fixed-length articulated legs with complete native image brushes. Head/carry retain exact pixels after integer body bob; no part rasters, layers or pose scaling.';limitations=@('Garment volume, texture joins and depth overlap require visual refinement.','Whole-cycle ordering, intermediate legs, free-arm matching and start/stop joins remain unfinished.','Stylized foreground weapon projection is inherited from the source, not a verified exact3D construction.','No actual-browser or Godot playback test.')} | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $soraOut 'manifest.json') -Encoding UTF8
$soraG.Dispose();$soraBoard.Dispose();$soraFont.Dispose();foreach($soraImage in @($soraLarge.ToArray())+@($soraSmall.ToArray())){$soraImage.Dispose()}
Write-Output 'Three genuinely articulated opposite-leg drawings saved; inspect art/sole placement before building a full cycle.'
