param([ValidatePattern('^flat_cycle_v[0-9]+$')][string]$LoopVersion='flat_cycle_v1',[ValidatePattern('^flat_stop_v[0-9]+$')][string]$StopVersion='flat_stop_v1')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraReady=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready'
$soraSource=Join-Path $soraReady 'run_start/direct_imagegen_trial/whole_figure_review_v3/frame_11.png'
$soraLoop=Join-Path $soraReady "run_loop/$LoopVersion"
$soraStop=Join-Path $soraReady "run_stop/$StopVersion"
foreach($soraDir in @($soraLoop,$soraStop)){if(Test-Path -LiteralPath $soraDir){throw "Preserve existing version: $soraDir"}}
$soraHash=(Get-FileHash -LiteralPath $soraSource -Algorithm SHA256).Hash.ToLowerInvariant()
Add-Type -AssemblyName System.Drawing
Add-Type -Path (Join-Path $PSScriptRoot 'FlatRunPainting.cs') -ReferencedAssemblies System.Drawing
function SoraPoint([double]$x,[double]$y){return [System.Drawing.PointF]::new($x,$y)}
function SoraGround([double]$x,[double]$angle){return SoraPoint $x (470-[FlatRunPainting]::ShoeBottom($angle))}
function SoraPose($phase,$bob,$pitch,$far,$fa,$near,$na,$elbow,$wrist,$grip,$wa,$lag,$hold=60,$second=$false){
    [pscustomobject]@{phase=$phase;bob=$bob;pitch=$pitch;far=$far;farAngle=$fa;near=$near;nearAngle=$na;elbow=$elbow;wrist=$wrist;grip=$grip;weaponAngle=$wa;lag=$lag;durationMs=$hold;secondHand=$second}
}
$soraLoopPoses=@(
    (SoraPose 'near contact' 0 0 (SoraPoint 187 350) 82 (SoraGround 337 0) 0 (SoraPoint 361 317) (SoraPoint 322 332) (SoraPoint 265 191) 14 -9),
    (SoraPose 'near compression' 4 0 (SoraPoint 193 358) 75 (SoraGround 319 0) 0 (SoraPoint 365 322) (SoraPoint 331 337) (SoraPoint 264 195) 15 -7),
    (SoraPose 'near passing' 2 0 (SoraPoint 259 370) 43 (SoraGround 296 0) 0 (SoraPoint 374 320) (SoraPoint 352 339) (SoraPoint 265 192) 14 -3),
    (SoraPose 'near late passing' -1 0 (SoraPoint 307 386) 10 (SoraGround 272 0) 0 (SoraPoint 385 311) (SoraPoint 375 330) (SoraPoint 266 188) 13 1),
    (SoraPose 'near heel-off' -3 0 (SoraPoint 333 391) -12 (SoraGround 246 15) 15 (SoraPoint 394 302) (SoraPoint 401 310) (SoraPoint 267 185) 12 5),
    (SoraPose 'near toe-off' -5 0 (SoraPoint 339 402) -15 (SoraGround 223 35) 35 (SoraPoint 399 294) (SoraPoint 418 289) (SoraPoint 268 182) 12 8),
    (SoraPose 'first flight' -10 0 (SoraPoint 336 414) -8 (SoraPoint 208 365) 70 (SoraPoint 395 290) (SoraPoint 420 279) (SoraPoint 267 178) 13 10),
    (SoraPose 'far pre-contact' -4 0 (SoraPoint 334 424) 0 (SoraPoint 194 348) 85 (SoraPoint 388 294) (SoraPoint 414 282) (SoraPoint 266 184) 14 8),
    (SoraPose 'far contact' 0 0 (SoraGround 330 0) 0 (SoraPoint 198 350) 82 (SoraPoint 378 302) (SoraPoint 402 291) (SoraPoint 265 191) 14 5),
    (SoraPose 'far compression' 4 0 (SoraGround 311 0) 0 (SoraPoint 207 358) 75 (SoraPoint 373 310) (SoraPoint 392 303) (SoraPoint 264 195) 15 1),
    (SoraPose 'far passing' 2 0 (SoraGround 287 0) 0 (SoraPoint 267 370) 43 (SoraPoint 368 316) (SoraPoint 374 318) (SoraPoint 265 192) 14 -3),
    (SoraPose 'far late passing' -1 0 (SoraGround 266 0) 0 (SoraPoint 315 386) 10 (SoraPoint 364 315) (SoraPoint 353 328) (SoraPoint 266 188) 13 -7),
    (SoraPose 'far heel-off' -3 0 (SoraGround 238 15) 15 (SoraPoint 341 391) -12 (SoraPoint 359 314) (SoraPoint 333 330) (SoraPoint 267 185) 12 -10),
    (SoraPose 'far toe-off' -5 0 (SoraGround 215 35) 35 (SoraPoint 350 402) -15 (SoraPoint 355 312) (SoraPoint 316 327) (SoraPoint 268 182) 12 -12),
    (SoraPose 'second flight' -10 0 (SoraPoint 208 365) 70 (SoraPoint 350 414) -8 (SoraPoint 354 309) (SoraPoint 307 322) (SoraPoint 267 178) 13 -12),
    (SoraPose 'near pre-contact' -4 0 (SoraPoint 194 348) 85 (SoraPoint 341 424) 0 (SoraPoint 356 313) (SoraPoint 313 327) (SoraPoint 266 184) 14 -11)
)
$soraStopPoses=@(
    $soraLoopPoses[0],
    (SoraPose 'braking compression' 6 0 (SoraPoint 194 363) 73 (SoraGround 337 0) 0 (SoraPoint 370 326) (SoraPoint 340 342) (SoraPoint 265 197) 16 -12 70),
    (SoraPose 'rear foot approaches' 7 -1 (SoraPoint 221 398) 32 (SoraGround 337 0) 0 (SoraPoint 376 323) (SoraPoint 354 338) (SoraPoint 265 198) 17 -12 70),
    (SoraPose 'rear foot catches' 5 -2 (SoraGround 236 0) 0 (SoraGround 337 0) 0 (SoraPoint 379 315) (SoraPoint 367 329) (SoraPoint 263 194) 16 -9 70),
    (SoraPose 'weight recovers' 1 -4 (SoraGround 236 0) 0 (SoraGround 337 0) 0 (SoraPoint 377 307) (SoraPoint 373 317) (SoraPoint 260 186) 11 -6 70),
    (SoraPose 'blade clears shoulder' -3 -6 (SoraGround 236 0) 0 (SoraGround 337 0) 0 (SoraPoint 370 297) (SoraPoint 367 302) (SoraPoint 258 177) 1 -2 70),
    (SoraPose 'carry lifts clear' -5 -8 (SoraPoint 227 411) 7 (SoraGround 337 0) 0 (SoraPoint 359 285) (SoraPoint 350 291) (SoraPoint 253 168) -16 2 70),
    (SoraPose 'blade turns forward' -6 -10 (SoraPoint 213 412) 3 (SoraGround 337 0) 0 (SoraPoint 347 277) (SoraPoint 330 283) (SoraPoint 248 173) -37 5 70),
    (SoraPose 'recovery step reaches' -6 -11 (SoraPoint 194 418) -3 (SoraGround 337 0) 0 (SoraPoint 335 275) (SoraPoint 310 278) (SoraPoint 244 204) -59 8 70),
    (SoraPose 'recovery heel plants' -5 -12 (SoraGround 180 0) 0 (SoraGround 337 0) 0 (SoraPoint 326 276) (SoraPoint 291 279) (SoraPoint 240 228) -80 10 70),
    (SoraPose 'guard lowers' -2 -13 (SoraGround 180 0) 0 (SoraGround 337 0) 0 (SoraPoint 320 281) (SoraPoint 275 280) (SoraPoint 238 232) -99 10 70),
    (SoraPose 'empty hand approaches' 1 -14 (SoraGround 180 0) 0 (SoraGround 337 0) 0 (SoraPoint 315 285) (SoraPoint 260 283) (SoraPoint 235 249) -115 8 70),
    (SoraPose 'second hand braces' 4 -15 (SoraGround 180 0) 0 (SoraGround 337 0) 0 (SoraPoint 311 296) (SoraPoint 252 297) (SoraPoint 232 274) -127 5 70 $true),
    (SoraPose 'guard settles' 7 -15 (SoraGround 180 0) 0 (SoraGround 337 0) 0 (SoraPoint 311 301) (SoraPoint 249 308) (SoraPoint 228 295) -134 2 80 $true),
    (SoraPose 'cloth follows through' 10 -14 (SoraGround 180 0) 0 (SoraGround 337 0) 0 (SoraPoint 310 306) (SoraPoint 247 319) (SoraPoint 225 310) -137 -1 80 $true),
    (SoraPose 'ready hold' 10 -14 (SoraGround 180 0) 0 (SoraGround 337 0) 0 (SoraPoint 310 306) (SoraPoint 247 319) (SoraPoint 225 310) -137 -2 140 $true)
)
$soraTorsoFollow=@(0,.6,.4,0,-.5,-.8,-.6,-.3,0,.6,.4,0,-.5,-.8,-.6,-.3)
for($soraIndex=0;$soraIndex -lt 16;$soraIndex++){$soraLoopPoses[$soraIndex].pitch=$soraTorsoFollow[$soraIndex]}
foreach($soraBatch in @([pscustomobject]@{dir=$soraLoop;poses=$soraLoopPoses;name='run_loop';loop=$true},[pscustomobject]@{dir=$soraStop;poses=$soraStopPoses;name='run_stop';loop=$false})){
    New-Item -ItemType Directory -Path $soraBatch.dir | Out-Null
    $soraRecords=[System.Collections.Generic.List[object]]::new()
    for($soraIndex=0;$soraIndex -lt $soraBatch.poses.Count;$soraIndex++){
        $soraPose=$soraBatch.poses[$soraIndex];$soraFile=('sora_{0}_{1:00}.png' -f $soraBatch.name,$soraIndex);$soraTarget=Join-Path $soraBatch.dir $soraFile
        if($soraBatch.name -eq 'run_stop' -and $soraIndex -eq 0){
            Copy-Item -LiteralPath (Join-Path $soraLoop 'sora_run_loop_00.png') -Destination $soraTarget
            $soraJoints=$soraLoopRecords[0].joints
        }else{
            $soraRaw=[FlatRunPainting]::Paint($soraSource,$soraTarget,$soraPose.pitch,$soraPose.bob,$soraPose.far,$soraPose.farAngle,$soraPose.near,$soraPose.nearAngle,$soraPose.elbow,$soraPose.wrist,$soraPose.grip,$soraPose.weaponAngle,$soraPose.lag,$soraPose.secondHand)
            $soraJoints=@($soraRaw | ForEach-Object {,@([Math]::Round($_.X,3),[Math]::Round($_.Y,3))})
        }
        $soraRecords.Add([pscustomobject][ordered]@{index=$soraIndex;file=$soraFile;phase=$soraPose.phase;durationMs=$soraPose.durationMs;bodyBob=$soraPose.bob;bodyPitch=$soraPose.pitch;joints=$soraJoints;shoeAngles=@($soraPose.farAngle,$soraPose.nearAngle);grip=@($soraPose.grip.X,$soraPose.grip.Y);weaponAngle=$soraPose.weaponAngle;sha256=(Get-FileHash -LiteralPath $soraTarget -Algorithm SHA256).Hash.ToLowerInvariant()})
    }
    if($soraBatch.name -eq 'run_loop'){$soraLoopRecords=$soraRecords.ToArray()}
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'FlatRunPainting.cs') -Destination (Join-Path $soraBatch.dir 'Painter_Source.cs')
    [ordered]@{status='complete flat-canvas motion draft; visual refinement and idle seam pending';animation=$soraBatch.name;frameCount=$soraRecords.Count;canvas=@(512,512);gameExport=@(128,128);loop=$soraBatch.loop;durationMs=($soraRecords | Measure-Object durationMs -Sum).Sum;method='New articulated shorts, calves, shoes, arms, cloth and connected weapon painted directly on a full source canvas; no individual production layers';source=$soraSource;sourceSha256=$soraHash;fixedProjectedThighLength=86;fixedProjectedShinLength=54;weapon='209-unit projected grip-to-tip, one rigid axis for guard/handle/collar/shaft/crown; far-arm same-shoulder carry behind protected source hair; foreground-facing projection held constant';frames=$soraRecords.ToArray();limitations=@('Head/jacket source detail retained; new fabric/boot/skin materials require visual comparison.','Drawing trajectories are provisional in-place display timing, not game physics.','Stop ends in a new braced guard; approved-idle alignment remains a separate join to refine.','Not integrated or tested in Godot.')} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $soraBatch.dir 'manifest.json') -Encoding UTF8
}
if((Get-FileHash -LiteralPath $soraSource -Algorithm SHA256).Hash.ToLowerInvariant() -ne $soraHash){throw 'Whole source changed'}
Write-Output 'Created16 alternating run poses and16 stop poses on complete canvases; originals preserved. Visual inspection still required.'
