param([ValidatePattern('^quality_(pilot|refinement)_v[0-9]+$')][string]$Version='quality_pilot_v1',[switch]$Pilot)
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraReady=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready'
$soraSource=Join-Path $soraReady 'run_start/direct_imagegen_trial/whole_figure_review_v3/frame_11.png'
$soraArms=Join-Path $soraReady 'run_start/direct_imagegen_trial/whole_figure_review_v3/frame_08.png'
$soraHashes=@($soraSource,$soraArms | ForEach-Object {(Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash.ToLowerInvariant()})
foreach($soraAnimation in @('run_loop','run_stop')){if(Test-Path -LiteralPath (Join-Path $soraReady "$soraAnimation/$Version")){throw 'Preserve existing quality pass; choose a new version'}}
Add-Type -AssemblyName System.Drawing
Add-Type -Path @((Join-Path $PSScriptRoot 'FlatRunPainting.cs'),(Join-Path $PSScriptRoot 'ReferenceSurfacePainting.cs')) -ReferencedAssemblies System.Drawing
function SoraPoint([double]$x,[double]$y){[System.Drawing.PointF]::new($x,$y)}
function SoraGround([double]$x,[double]$angle){SoraPoint $x (470-[ReferenceSurfacePainting]::ShoeBottom($soraSource,$angle))}
$soraFar=@((SoraPoint 145 338),(SoraPoint 158 344),(SoraPoint 235 362),(SoraPoint 286 376),(SoraPoint 310 380),(SoraPoint 329 388),(SoraPoint 334 392),(SoraPoint 331 ((SoraGround 331 0).Y-2)),(SoraGround 325 0),(SoraGround 310 0),(SoraGround 285 0),(SoraGround 262 0),(SoraGround 237 15),(SoraGround 215 35),(SoraPoint 175 346),(SoraPoint 152 334))
$soraNear=@((SoraGround 347 0),(SoraGround 331 0),(SoraGround 308 0),(SoraGround 280 0),(SoraGround 252 15),(SoraGround 225 35),(SoraPoint 173 346),(SoraPoint 166 334),(SoraPoint 165 338),(SoraPoint 178 344),(SoraPoint 246 362),(SoraPoint 298 376),(SoraPoint 322 380),(SoraPoint 345 388),(SoraPoint 345 392),(SoraPoint 348 ((SoraGround 348 0).Y-2)))
$soraStopFar=@($soraFar[0],(SoraPoint 160 343),(SoraPoint 206 380),(SoraGround 238 0),(SoraGround 238 0),(SoraGround 238 0),(SoraPoint 223 396),(SoraPoint 204 398),(SoraPoint 183 403),(SoraGround 175 0),(SoraGround 175 0),(SoraGround 175 0),(SoraGround 175 0),(SoraGround 175 0),(SoraGround 175 0),(SoraGround 175 0))
foreach($soraAnimation in @('run_loop','run_stop')){
    $soraPriorVersion=if($soraAnimation -eq 'run_loop'){'flat_cycle_v5'}else{'flat_stop_v5'}
    $soraPrior=Get-Content -LiteralPath (Join-Path $soraReady "$soraAnimation/$soraPriorVersion/manifest.json") -Raw | ConvertFrom-Json
    $soraIndices=if($Pilot){if($soraAnimation -eq 'run_loop'){@(0,2,6)}else{@(3,8,15)}}else{@(0..15)}
    $soraOut=Join-Path $soraReady "$soraAnimation/$Version"
    New-Item -ItemType Directory -Path $soraOut | Out-Null
    $soraRecords=[System.Collections.Generic.List[object]]::new()
    foreach($soraIndex in $soraIndices){
        $soraOld=$soraPrior.frames[$soraIndex]
        $soraFarPoint=if($soraAnimation -eq 'run_loop'){$soraFar[$soraIndex]}else{$soraStopFar[$soraIndex]}
        $soraNearPoint=if($soraAnimation -eq 'run_loop'){$soraNear[$soraIndex]}else{SoraGround 347 0}
        $soraElbow=SoraPoint $soraOld.joints[3][0] $soraOld.joints[3][1]
        # The prior manifest stores leg joints; free-arm controls are retained from the painter's review poses.
        $soraLoopElbows=@(@(361,317),@(365,322),@(374,320),@(385,311),@(394,302),@(399,294),@(395,290),@(388,294),@(378,302),@(373,310),@(368,316),@(364,315),@(359,314),@(355,312),@(354,309),@(356,313))
        $soraLoopWrists=@(@(322,332),@(331,337),@(352,339),@(375,330),@(401,310),@(418,289),@(420,279),@(414,282),@(402,291),@(392,303),@(374,318),@(353,328),@(333,330),@(316,327),@(307,322),@(313,327))
        $soraStopElbows=@(@(361,317),@(370,326),@(376,323),@(379,315),@(377,307),@(370,297),@(359,285),@(347,277),@(335,275),@(326,276),@(320,281),@(315,285),@(311,296),@(311,301),@(310,306),@(310,306))
        $soraStopWrists=@(@(322,332),@(340,342),@(354,338),@(367,329),@(373,317),@(367,302),@(350,291),@(330,283),@(310,278),@(291,279),@(275,280),@(260,283),@(252,297),@(249,308),@(247,319),@(247,319))
        $soraArmElbows=if($soraAnimation -eq 'run_loop'){$soraLoopElbows}else{$soraStopElbows};$soraArmWrists=if($soraAnimation -eq 'run_loop'){$soraLoopWrists}else{$soraStopWrists}
        $soraElbow=SoraPoint $soraArmElbows[$soraIndex][0] $soraArmElbows[$soraIndex][1];$soraWrist=SoraPoint $soraArmWrists[$soraIndex][0] $soraArmWrists[$soraIndex][1]
        $soraGrip=SoraPoint $soraOld.grip[0] $soraOld.grip[1];$soraLag=if($soraIndex -lt 8){-6+$soraIndex}else{5-($soraIndex-8)}
        $soraFile=('sora_{0}_{1:00}.png' -f $soraAnimation,$soraIndex);$soraTarget=Join-Path $soraOut $soraFile
        if(-not $Pilot -and $soraAnimation -eq 'run_stop' -and $soraIndex -eq 0){Copy-Item -LiteralPath (Join-Path $soraReady "run_loop/$Version/sora_run_loop_00.png") -Destination $soraTarget;$soraJoints=$soraLoopRecords[0].joints}
        else{
            $soraRaw=[FlatRunPainting]::PaintRefined($soraSource,$soraArms,$soraTarget,$soraOld.bodyPitch,$soraOld.bodyBob,$soraFarPoint,$soraOld.shoeAngles[0],$soraNearPoint,$soraOld.shoeAngles[1],$soraElbow,$soraWrist,$soraGrip,$soraOld.weaponAngle,$soraLag)
            $soraJoints=@($soraRaw | ForEach-Object {,@([Math]::Round($_.X,3),[Math]::Round($_.Y,3))})
        }
        $soraRecords.Add([pscustomobject][ordered]@{index=$soraIndex;file=$soraFile;phase=$soraOld.phase;durationMs=$soraOld.durationMs;bodyBob=$soraOld.bodyBob;bodyPitch=$soraOld.bodyPitch;joints=$soraJoints;shoeAngles=$soraOld.shoeAngles;grip=$soraOld.grip;weaponAngle=$soraOld.weaponAngle;freeElbow=@($soraElbow.X,$soraElbow.Y);freeWrist=@($soraWrist.X,$soraWrist.Y);sha256=(Get-FileHash -LiteralPath $soraTarget -Algorithm SHA256).Hash.ToLowerInvariant()})
    }
    if($soraAnimation -eq 'run_loop'){$soraLoopRecords=$soraRecords.ToArray()}
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'FlatRunPainting.cs') -Destination (Join-Path $soraOut 'Pose_Painter_Source.cs')
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'ReferenceSurfacePainting.cs') -Destination (Join-Path $soraOut 'Surface_Painter_Source.cs')
    [ordered]@{status='quality refinement draft; visual inspection required';animation=$soraAnimation;frameCount=$soraRecords.Count;canvas=@(512,512);gameExport=@(128,128);loop=($soraAnimation -eq 'run_loop');durationMs=($soraRecords | Measure-Object durationMs -Sum).Sum;pilot=[bool]$Pilot;method='One complete RGBA canvas; full original PNGs used as reference brushes with new joint poses and direct repainting; no cropped component bitmaps, part PNGs or production layers';qualityBenchmark='run_start/sync_refinement_v2/flat_lift_pilot_v5/full_start_study/Run_Start_13_Once.gif';sourcePaths=@($soraSource,$soraArms);sourceHashes=$soraHashes;projectedNearThigh=[ReferenceSurfacePainting]::NearThigh;projectedFarThigh=[ReferenceSurfacePainting]::FarThigh;projectedShin=[ReferenceSurfacePainting]::Shin;weapon='Shared209-unit connected blade axis; constant native guard/grip material; shoulder carry on far arm';frames=$soraRecords.ToArray();limitations=@('Reference-based surface projection requires seam, occlusion and fold review.','Skin, chain and final idle join require further drawing.','No Godot or browser playback test.')} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $soraOut 'manifest.json') -Encoding UTF8
}
Write-Output 'Reference-quality complete-frame candidates created; inspect before promotion.'
