param([ValidatePattern('^gait_cycle_study_v[0-9]+$')][string]$Version='gait_cycle_study_v1',[switch]$CounterSwing,[switch]$Inbetweens)
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraReady=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready'
$soraOut=Join-Path $soraReady "run_loop/direct_generation_retry_v1/$Version"
if(Test-Path -LiteralPath $soraOut){throw 'Preserve previous gait study'}
$soraBody=Join-Path $soraReady 'run_loop/direct_generation_retry_v1/motion_refinement_v4/sora_run_loop_02.png'
$soraClothes=Join-Path $soraReady 'run_loop/direct_generation_retry_v1/whole_frame_review_v1/sora_run_loop_02.png'
$soraBoots=Join-Path $soraReady 'run_loop/direct_generation_retry_v1/whole_frame_review_v1/sora_run_loop_00.png'
$soraHashes=@($soraBody,$soraClothes,$soraBoots | ForEach-Object {(Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash.ToLowerInvariant()})
Add-Type -AssemblyName System.Drawing
Add-Type -Path (Join-Path $PSScriptRoot 'GeneratedGaitPainting.cs') -ReferencedAssemblies System.Drawing
if($CounterSwing){Add-Type -Path (Join-Path $PSScriptRoot 'GeneratedFlatRefinement.cs') -ReferencedAssemblies System.Drawing}
Add-Type -Path (Join-Path $PSScriptRoot '../AnimationPackaging.cs') -ReferencedAssemblies System.Drawing
$soraSole=[GeneratedGaitPainting]::SoleOffset($soraBoots,0)
$soraToeSole=[GeneratedGaitPainting]::SoleOffset($soraBoots,25)
$soraPlan=@(
    @{phase='far contact';shift=-2;near=@(205,356);far=@(330,(470-$soraSole));na=35;fa=0;support='far'},
    @{phase='far compression';shift=4;near=@(205,346);far=@(318,(470-$soraSole));na=45;fa=0;support='far'},
    @{phase='far support, near recovery';shift=0;near=@(243,342);far=@(300,(470-$soraSole));na=15;fa=0;support='far'},
    @{phase='near passing';shift=-4;near=@(315,371);far=@(278,(470-$soraSole));na=-35;fa=0;support='far'},
    @{phase='far toe-off, near extension';shift=-7;near=@(345,386);far=@(255,(470-$soraToeSole));na=-25;fa=25;support='far'},
    @{phase='flight into near contact';shift=-10;near=@(352,387);far=@(230,358);na=-20;fa=25;support='none'},
    @{phase='near contact';shift=-2;near=@(353,(470-$soraSole));far=@(213,360);na=0;fa=35;support='near'},
    @{phase='near compression';shift=4;near=@(340,(470-$soraSole));far=@(225,344);na=0;fa=45;support='near'},
    @{phase='near support, far recovery';shift=0;near=@(318,(470-$soraSole));far=@(255,352);na=0;fa=15;support='near'},
    @{phase='far passing';shift=-4;near=@(295,(470-$soraSole));far=@(316,378);na=0;fa=-35;support='near'},
    @{phase='near toe-off, far extension';shift=-7;near=@(272,(470-$soraToeSole));far=@(330,388);na=25;fa=-25;support='near'},
    @{phase='flight into far contact';shift=-10;near=@(203,356);far=@(336,391);na=35;fa=-20;support='none'}
)
$soraUpper=@(60,62,76,95,110,120,116,112,105,96,80,66)
$soraFore=@(10,15,10,0,-75,-130,-145,-145,-125,-75,10,10)
$soraExpanded=[System.Collections.Generic.List[object]]::new()
for($soraKey=0;$soraKey -lt 12;$soraKey++){
    $soraPose=$soraPlan[$soraKey];$soraPose.keyPosition=$soraKey;$soraPose.duration=80;$soraPose.ua=$soraUpper[$soraKey];$soraPose.fore=$soraFore[$soraKey]
    $soraExpanded.Add($soraPose)
    if($Inbetweens -and $soraKey -in @(2,8,9,10)){
        $soraPose.duration=40;$soraNext=$soraPlan[$soraKey+1]
        $soraMid=@{phase="new transition $soraKey-$($soraKey+1)";keyPosition=($soraKey+.5);duration=40;shift=[int][Math]::Round(($soraPose.shift+$soraNext.shift)/2.0);near=@((($soraPose.near[0]+$soraNext.near[0])/2.0),(($soraPose.near[1]+$soraNext.near[1])/2.0));far=@((($soraPose.far[0]+$soraNext.far[0])/2.0),(($soraPose.far[1]+$soraNext.far[1])/2.0));na=($soraPose.na+$soraNext.na)/2.0;fa=($soraPose.fa+$soraNext.fa)/2.0;support=if($soraPose.support -eq $soraNext.support){$soraPose.support}else{'none'};ua=($soraUpper[$soraKey]+$soraUpper[$soraKey+1])/2.0;fore=($soraFore[$soraKey]+$soraFore[$soraKey+1])/2.0}
        if($soraMid.support -eq 'near'){$soraMid.near[1]=470-[GeneratedGaitPainting]::SoleOffset($soraBoots,$soraMid.na)}
        if($soraMid.support -eq 'far'){$soraMid.far[1]=470-[GeneratedGaitPainting]::SoleOffset($soraBoots,$soraMid.fa)}
        # Route the returning empty hand below the blade instead of through it.
        if($soraKey -eq 9){$soraMid.fore=0}
        $soraExpanded.Add($soraMid)
    }
}
$soraPlan=$soraExpanded.ToArray();$soraCount=$soraPlan.Count
foreach($soraPose in $soraPlan){
    [GeneratedGaitPainting]::Knee([System.Drawing.PointF]::new(272,316+$soraPose.shift),[System.Drawing.PointF]::new($soraPose.near[0],$soraPose.near[1]),$true) | Out-Null
    [GeneratedGaitPainting]::Knee([System.Drawing.PointF]::new(291,325+$soraPose.shift),[System.Drawing.PointF]::new($soraPose.far[0],$soraPose.far[1]),$false) | Out-Null
}
New-Item -ItemType Directory -Path $soraOut,(Join-Path $soraOut 'frames_128'),(Join-Path $soraOut 'registration_probes') | Out-Null
if($CounterSwing){New-Item -ItemType Directory -Path (Join-Path $soraOut 'whole_canvas_stages') | Out-Null}
$soraRecords=[System.Collections.Generic.List[object]]::new();$soraLarge=[System.Collections.Generic.List[System.Drawing.Bitmap]]::new();$soraSmall=[System.Collections.Generic.List[System.Drawing.Bitmap]]::new()
$soraRows=[int][Math]::Ceiling($soraCount/4.0)
$soraBoard=[System.Drawing.Bitmap]::new(1024,$soraRows*280);$soraG=[System.Drawing.Graphics]::FromImage($soraBoard);$soraG.Clear([System.Drawing.Color]::White)
$soraSheet=[System.Drawing.Bitmap]::new(2048,$soraRows*512,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb);$soraSheetG=[System.Drawing.Graphics]::FromImage($soraSheet)
$soraFont=[System.Drawing.Font]::new('Arial',9)
for($soraIndex=0;$soraIndex -lt $soraCount;$soraIndex++){
    $soraPose=$soraPlan[$soraIndex];$soraNear=[System.Drawing.PointF]::new($soraPose.near[0],$soraPose.near[1]);$soraFar=[System.Drawing.PointF]::new($soraPose.far[0],$soraPose.far[1])
    $soraFrameBody=$soraBody;$soraArm=$null;$soraStage=$null
    if($CounterSwing){
        $soraStage=('whole_canvas_stages/arm_pose_{0:00}.png' -f $soraIndex)
        $soraFrameBody=Join-Path $soraOut $soraStage
        # Paint the arm before the legs, so an arm erasure cannot remove a newly raised knee.
        $soraArmJoints=[GeneratedFlatRefinement]::Paint($soraClothes,$soraBoots,$soraFrameBody,$soraPose.ua,$soraPose.fore,$false,$false)
        $soraArm=@{upperAngle=$soraPose.ua;forearmAngle=$soraPose.fore;upperLength=40.4969;forearmLength=36;shoulder=@($soraArmJoints[1],($soraArmJoints[2]+$soraPose.shift));elbow=@($soraArmJoints[3],($soraArmJoints[4]+$soraPose.shift));wrist=@($soraArmJoints[5],($soraArmJoints[6]+$soraPose.shift))}
    }
    $soraAdjust=0;$soraProbeRecords=[System.Collections.Generic.List[object]]::new()
    for($soraAttempt=0;$soraAttempt -lt 3;$soraAttempt++){
        $soraProbe=Join-Path $soraOut ('registration_probes/whole_pose_{0:00}_probe_{1:00}.png' -f $soraIndex,$soraAttempt)
        $soraJoints=[GeneratedGaitPainting]::Paint($soraFrameBody,$soraClothes,$soraBoots,$soraProbe,$soraPose.shift,$soraNear,$soraPose.na,$soraFar,$soraPose.fa)
        $soraCheck=[System.Drawing.Bitmap]::new($soraProbe);$soraOpaqueBottom=0
        for($soraY=511;$soraY -ge 0 -and $soraOpaqueBottom -eq 0;$soraY--){for($soraX=0;$soraX -lt 512;$soraX++){if($soraCheck.GetPixel($soraX,$soraY).A -gt 100){$soraOpaqueBottom=$soraY+1;break}}}
        $soraCheck.Dispose();$soraProbeRecords.Add(@{file=[System.IO.Path]::GetFileName($soraProbe);opaqueExclusiveBottom=$soraOpaqueBottom})
        if($soraPose.support -eq 'none'){if($soraOpaqueBottom -ge 470){throw 'Flight has no solid-sole clearance'};break}
        if($soraOpaqueBottom -eq 470){break}
        $soraDelta=470-$soraOpaqueBottom
        if([Math]::Abs($soraDelta) -gt 4){throw 'Inspect support drawing instead of moving an unexpected footprint'}
        if($soraPose.support -eq 'near'){$soraNear.Y+=$soraDelta}else{$soraFar.Y+=$soraDelta}
        $soraAdjust+=$soraDelta
    }
    if($soraPose.support -ne 'none' -and $soraOpaqueBottom -ne 470){throw 'Support registration not resolved'}
    $soraFile=('sora_run_loop_{0:00}.png' -f $soraIndex);$soraTarget=Join-Path $soraOut $soraFile
    Copy-Item -LiteralPath $soraProbe -Destination $soraTarget
    $soraImage=[System.Drawing.Bitmap]::new($soraTarget);$soraCol=$soraIndex%4;$soraRow=[Math]::Floor($soraIndex/4)
    $soraG.DrawImage($soraImage,[int]($soraCol*256),[int]($soraRow*280),256,256)
    $soraSheetG.DrawImageUnscaled($soraImage,$soraCol*512,$soraRow*512)
    $soraG.DrawString(('{0:00} {1}' -f $soraIndex,$soraPose.phase),$soraFont,[System.Drawing.Brushes]::Black,$soraCol*256+6,$soraRow*280+257)
    foreach($soraSize in @(512,128)){
        $soraFlat=[System.Drawing.Bitmap]::new($soraSize,$soraSize);$soraGraphics=[System.Drawing.Graphics]::FromImage($soraFlat);$soraGraphics.Clear([System.Drawing.Color]::White)
        $soraGraphics.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic;$soraGraphics.DrawImage($soraImage,0,0,$soraSize,$soraSize);$soraGraphics.Dispose()
        if($soraSize -eq 512){$soraLarge.Add($soraFlat)}else{$soraSmall.Add($soraFlat)}
    }
    $soraGame=[System.Drawing.Bitmap]::new(128,128,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb);$soraGraphics=[System.Drawing.Graphics]::FromImage($soraGame)
    $soraGraphics.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic;$soraGraphics.DrawImage($soraImage,0,0,128,128);$soraGraphics.Dispose()
    $soraGame.Save((Join-Path $soraOut "frames_128/$soraFile"),[System.Drawing.Imaging.ImageFormat]::Png);$soraGame.Dispose();$soraImage.Dispose()
    $soraRecords.Add([pscustomobject][ordered]@{index=$soraIndex;keyPosition=$soraPose.keyPosition;file=$soraFile;phase=$soraPose.phase;durationMs=$soraPose.duration;bodyShiftY=$soraPose.shift;protectedUpperExclusiveY=270+$soraPose.shift;upperWholeCanvasStage=$soraStage;upperStageSha256=(Get-FileHash -LiteralPath $soraFrameBody -Algorithm SHA256).Hash.ToLowerInvariant();arm=$soraArm;support=$soraPose.support;supportOpaqueBottom=$soraOpaqueBottom;supportRegistrationAdjustment=$soraAdjust;nearShoeAngle=$soraPose.na;farShoeAngle=$soraPose.fa;joints=@($soraJoints | ForEach-Object {,@($_.X,$_.Y)});registrationProbes=$soraProbeRecords.ToArray();sha256=(Get-FileHash -LiteralPath $soraTarget -Algorithm SHA256).Hash.ToLowerInvariant()})
}
$soraBoard.Save((Join-Path $soraOut 'Contact_Sheet.png'),[System.Drawing.Imaging.ImageFormat]::Png)
$soraSheet.Save((Join-Path $soraOut 'Sprite_Sheet_512.png'),[System.Drawing.Imaging.ImageFormat]::Png)
foreach($soraSize in @(512,128)){$soraFrames=if($soraSize -eq 512){$soraLarge.ToArray()}else{$soraSmall.ToArray()};[AnimationPackaging]::Gif((Join-Path $soraOut "Preview_${soraSize}_Loop.gif"),$soraFrames,[int[]]@($soraRecords | ForEach-Object durationMs))}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'GeneratedGaitPainting.cs') -Destination (Join-Path $soraOut 'Flat_Gait_Painter_Source.cs')
$soraStatus=if($CounterSwing){'Alternating-leg and free-arm drawing study; unfinished garment/follow-through/transition refinement'}else{'Full leg-motion drawing study; fixed upper pose, unfinished arm/garment/transition refinement'}
$soraUpperLimit=if($CounterSwing){'Articulated free-arm counter-swing is added before leg drawing on complete canvases. Torso pitch, carrying shoulder, cloth and chain follow-through remain.'}else{'Upper pose and free arm are held as the art reference; new arm counter-swing and shoulder/torso follow-through remain.'}
if($CounterSwing){Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'GeneratedFlatRefinement.cs') -Destination (Join-Path $soraOut 'Flat_Arm_Painter_Source.cs')}
[ordered]@{status=$soraStatus;counterSwing=[bool]$CounterSwing;inbetweens=[bool]$Inbetweens;frameCount=$soraCount;loop=$true;durationMs=960;canvas=@(512,512);gameExport=@(128,128);nearThigh=[GeneratedGaitPainting]::NearThigh;nearShin=[GeneratedGaitPainting]::NearShin;farThigh=[GeneratedGaitPainting]::FarThigh;farShin=[GeneratedGaitPainting]::FarShin;sourceFiles=@($soraBody,$soraClothes,$soraBoots);sourceHashes=$soraHashes;floor=470;floorDefinition='Exclusive bottom of solid pixels (alpha>100); faint native edge/shadow alpha can extend below.';frames=$soraRecords.ToArray();method='Complete canvases with independently drawn articulated legs, new curved shorts/calf contours and complete native PNG reference brushes. Integer body bob; optional articulated free arm painted first on complete canvases. New inbetweens use new joint/contour drawings, never pixel morphs or scaled poses. No part layers.';limitations=@($soraUpperLimit,'Garment volume, hip texture seams and shoe depth still need polish against the run-start benchmark.','Loop wrap and original start/stop joins need review and new complete poses.','Weapon foreground yaw is inherited and stylized, not certified3D.','No actual-browser or Godot playback test.')} | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $soraOut 'manifest.json') -Encoding UTF8
$soraG.Dispose();$soraBoard.Dispose();$soraSheetG.Dispose();$soraSheet.Dispose();$soraFont.Dispose();foreach($soraImage in @($soraLarge.ToArray())+@($soraSmall.ToArray())){$soraImage.Dispose()}
Write-Output "$soraCount new alternating-leg drawings saved; unfinished motion/art study."
