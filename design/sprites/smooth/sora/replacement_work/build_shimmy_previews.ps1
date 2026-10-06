$ErrorActionPreference='Stop'
$workPath=$PSScriptRoot
$packagingText=Get-Content -Raw -LiteralPath (Join-Path $workPath 'package_replacements.ps1')
$setupEnd=$packagingText.IndexOf('$duckCells=')
if($setupEnd -lt 0){throw 'Packaging function boundary missing'}
. ([scriptblock]::Create($packagingText.Substring(0,$setupEnd).Replace('$PSScriptRoot','$workPath')))
$cells=@(Read-Cells 'shimmy_forward_source.png' 5 10)
$scale=384.0/[AnimationPackaging]::Bounds($cells[0]).Height
$forward=@(Save-Frames $cells 'sora_shimmy_forward' $scale)
$reverseOrder=@(0,9,8,7,6,5,4,3,2,1)
$backward=@()
for($index=0;$index -lt 10;$index++) {
    $poseIndex=$reverseOrder[$index]
    $backward+=$forward[$poseIndex]
    $filename=('sora_shimmy_backward_{0:00}.png' -f $index)
    $forward[$poseIndex].Save((Join-Path $outputPath $filename),[System.Drawing.Imaging.ImageFormat]::Png)
    $script:metrics[$filename]=$script:metrics[('sora_shimmy_forward_{0:00}.png' -f $poseIndex)]
}
$forwardDelays=@(90,90,90,90,90,90,90,90,90,90)
$backwardDelays=@(100,100,100,100,100,100,100,100,100,100)
Save-Sheet $forward 5 'sora_shimmy_forward_sheet.png'
Save-Sheet $backward 5 'sora_shimmy_backward_sheet.png'
[AnimationPackaging]::Gif((Join-Path $outputPath 'sora_shimmy_forward_preview.gif'),[System.Drawing.Bitmap[]]$forward,[int[]]$forwardDelays)
[AnimationPackaging]::Gif((Join-Path $outputPath 'sora_shimmy_backward_preview.gif'),[System.Drawing.Bitmap[]]$backward,[int[]]$backwardDelays)
$manifest=@{
    character='Sora';art_style='smooth cel-shaded';canvas_size=@(512,512);ground_baseline_y=470;body_anchor=@(256,470)
    status='art preview; no movement-controller integration'
    animation_source='ten generated articulated footwork drawings; not scaled copies of a static pose'
    packaging='one constant uniform scale for entire batch, with translation to floor contact'
    animations=@{
        forward=@{total_frames=10;loop=$true;total_duration_ms=900;sprite_sheet='sora_shimmy_forward_sheet.png';frames=@(Frame-List 'sora_shimmy_forward' $forwardDelays)}
        backward=@{total_frames=10;loop=$true;total_duration_ms=1000;sprite_sheet='sora_shimmy_backward_sheet.png';source='forward footwork poses in reverse order';source_pose_order=$reverseOrder;frames=@(Frame-List 'sora_shimmy_backward' $backwardDelays)}
    }
    limitations=@('Guard and gait need user visual review.','A separately generated backward draft is not used; its front-foot follow-through was inadequate and its correction was blocked.','Backward uses shared drawings; it is not ten independently generated backward-only poses.','Weapon sockets are not measured yet.','Not tested in Godot.')
}
$manifest|ConvertTo-Json -Depth 10|Set-Content -LiteralPath (Join-Path $outputPath 'sora_shimmy_manifest.json') -Encoding UTF8
$activePath=Split-Path -Parent $workPath
Get-ChildItem -LiteralPath $outputPath -File|Where-Object {$_.Name -like 'sora_shimmy_*'}|ForEach-Object {Copy-Item -LiteralPath $_.FullName -Destination $activePath -Force}
# Reuse the reviewed viewer controls with the two new frame sequences.
$html=Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $workPath 'templates/Animation_Previews.html')
$html=$html.Replace('Sora animation review','Sora shimmy review')
$html=[regex]::Replace($html,'<h1>[^<]*</h1>','<h1>Sora guarded shimmies</h1>')
$html=$html.Replace('Pause and step to inspect each newly drawn pose. Crouch rises by reversing the eight lowering poses.','Pause and step to inspect the footwork. Backward retreat uses the newly drawn forward poses in reverse order.')
$html=$html.Replace('Standing breathing idle','Forward guarded shimmy')
$html=[regex]::Replace($html,'10 drawings . 1.48-second loop','10 drawings | 0.9-second loop')
$html=[regex]::Replace($html,'Stand . crouch . stand','Backward guarded shimmy')
$html=[regex]::Replace($html,'8 drawings . 14 playback positions . 2.08-second loop','10 shared drawings | 1-second loop')
$html=$html.Replace("urls:urls('sora_stand_idle',10),order:[0,1,2,3,4,5,6,7,8,9],delays:[150,130,130,150,180,150,130,130,150,180]", "urls:urls('sora_shimmy_forward',10),order:[0,1,2,3,4,5,6,7,8,9],delays:[90,90,90,90,90,90,90,90,90,90]")
$html=$html.Replace("urls:urls('sora_crouch_down',8),order:[0,1,2,3,4,5,6,7,6,5,4,3,2,1],delays:[450,90,90,90,90,90,90,550,90,90,90,90,90,90]", "urls:urls('sora_shimmy_backward',10),order:[0,1,2,3,4,5,6,7,8,9],delays:[100,100,100,100,100,100,100,100,100,100]")
$html=$html.Replace("const phase=s.id==='duck'?(s.index===0?'Standing hold':s.index===7?'Crouched hold':s.index<7?'Lowering':'Rising'):'Breathing';", "const phase=s.id==='duck'?'Retreat':'Advance';")
$html=$html.Replace('Active game sprites have not been replaced in this preview step.','These files are in the primary smooth-sprite folder; they have not been integrated into Godot.')
Set-Content -LiteralPath (Join-Path $activePath 'Shimmy_Previews.html') -Value $html -Encoding UTF8
foreach($bitmap in @($forward)+@($cells)){$bitmap.Dispose()}
Get-ChildItem -LiteralPath $activePath -File|Where-Object {$_.Name -like '*shimmy*'}|Select-Object Name,Length
& (Join-Path $PSScriptRoot 'organize_animation_flows.ps1')
