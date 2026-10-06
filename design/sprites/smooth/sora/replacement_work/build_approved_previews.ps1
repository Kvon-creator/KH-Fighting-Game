$ErrorActionPreference='Stop'
$packagingText=Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'package_replacements.ps1')
$setupEnd=$packagingText.IndexOf('$duckCells=')
if($setupEnd -lt 0){throw 'Packaging function boundary missing'}
$workPath=$PSScriptRoot
. ([scriptblock]::Create($packagingText.Substring(0,$setupEnd).Replace('$PSScriptRoot','$workPath')))

$duckCells=@(Read-Cells 'duck_sheet_source.png' 4 8)
$duckScale=384.0/[AnimationPackaging]::Bounds($duckCells[0]).Height
$duck=@(Save-Frames $duckCells 'sora_crouch_down' $duckScale)
$standCells=@(Read-Cells 'stand_idle_source.png' 5 10)
$standScale=384.0/[AnimationPackaging]::Bounds($standCells[0]).Height
$stand=@(Save-Frames $standCells 'sora_stand_idle' $standScale)
$standDelays=@(150,130,130,150,180,150,130,130,150,180)
$duckOrder=@(0,1,2,3,4,5,6,7,6,5,4,3,2,1)
$duckDelays=@(450,90,90,90,90,90,90,550,90,90,90,90,90,90)
$cycle=@()
foreach($index in $duckOrder){$cycle+=$duck[$index]}
Save-Sheet $stand 5 'sora_stand_idle_sheet.png'
Save-Sheet $duck 4 'sora_duck_down_sheet.png'
[AnimationPackaging]::Gif((Join-Path $outputPath 'sora_stand_idle_preview.gif'),[System.Drawing.Bitmap[]]$stand,[int[]]$standDelays)
[AnimationPackaging]::Gif((Join-Path $outputPath 'sora_duck_full_cycle_preview.gif'),[System.Drawing.Bitmap[]]$cycle,[int[]]$duckDelays)
$manifest=@{
    status='review preview, no Godot integration';canvas_size=@(512,512);ground_baseline_y=470
    source_art=@('duck_sheet_source.png','stand_idle_source.png')
    packaging='Each generated sheet uses one constant uniform display scale. Frames are not synthesized by scaling a single pose. Frame translation aligns floor contact.'
    standing_idle=@{loop=$true;frame_count=10;durations_ms=$standDelays;frames=@(Frame-List 'sora_stand_idle' $standDelays)}
    duck_cycle=@{loop=$true;unique_drawings=8;playback_samples=14;order=$duckOrder;durations_ms=$duckDelays;rise='Same newly drawn poses in reverse order';frames=@(Frame-List 'sora_crouch_down' @(90,90,90,90,90,90,90,90))}
    limitations=@('Generated hand, chain and linework details may need cleanup.','No additional intermediate drawings or motion interpolation were fabricated.','No active game assets replaced in this preview step.')
}
$manifest|ConvertTo-Json -Depth 10|Set-Content -LiteralPath (Join-Path $outputPath 'approved_preview_manifest.json') -Encoding UTF8
foreach($bitmap in @($duck)+@($stand)+@($duckCells)+@($standCells)){$bitmap.Dispose()}
Get-ChildItem -LiteralPath $outputPath -File | Select-Object Name,Length
& (Join-Path $PSScriptRoot 'organize_animation_flows.ps1')
