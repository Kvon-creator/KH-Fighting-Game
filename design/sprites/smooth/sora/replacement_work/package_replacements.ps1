$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
Add-Type -Path (Join-Path $PSScriptRoot 'AnimationPackaging.cs') -ReferencedAssemblies System.Drawing
$outputPath = Join-Path $PSScriptRoot 'ready'
New-Item -ItemType Directory -Path $outputPath -Force | Out-Null
$script:metrics = @{}

function Read-Cells([string]$Name,[int]$Columns,[int]$Count) {
    $sourcePath=Join-Path $PSScriptRoot $Name
    if(!(Test-Path -LiteralPath $sourcePath)) {
        $candidates=@(Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'ready') -File -Recurse -Filter $Name)
        if($candidates.Count -ne 1){throw "Expected one animation source: $Name"}
        $sourcePath=$candidates[0].FullName
    }
    $image = [System.Drawing.Bitmap]::FromFile($sourcePath)
    try {
        $boundary = [AnimationPackaging]::RowBoundary($image)
        for ($index=0;$index -lt $Count;$index++) {
            $column=$index % $Columns
            $row=[int][Math]::Floor($index/$Columns)
            $left=[int][Math]::Floor($column*$image.Width/$Columns)
            $right=[int][Math]::Floor(($column+1)*$image.Width/$Columns)
            $top=0;$bottom=$boundary
            if($row -eq 1){$top=$boundary;$bottom=$image.Height}
            $rectangle=New-Object System.Drawing.Rectangle($left,$top,($right-$left),($bottom-$top))
            $image.Clone($rectangle,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
        }
    } finally {$image.Dispose()}
}

function Save-Frames($Cells,[string]$Prefix,[double]$Scale) {
    $firstBounds=[AnimationPackaging]::Bounds($Cells[0])
    $fixedCenter=($firstBounds.Left+$firstBounds.Right)/2
    $index=0
    foreach($cell in $Cells) {
        $bounds=[AnimationPackaging]::Bounds($cell)
        $bitmap=New-Object System.Drawing.Bitmap(512,512,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
        $graphics=[System.Drawing.Graphics]::FromImage($bitmap)
        try {
            $graphics.Clear([System.Drawing.Color]::Transparent)
            $graphics.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
            $graphics.PixelOffsetMode=[System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
            # A SINGLE constant scale for each generated batch; never scale one pose into another.
            $offsetX=[int][Math]::Round(256-$fixedCenter*$Scale)
            $offsetY=[int][Math]::Round(470-($bounds.Bottom-1)*$Scale)
            $destination=New-Object System.Drawing.Rectangle($offsetX,$offsetY,([int][Math]::Round($cell.Width*$Scale)),([int][Math]::Round($cell.Height*$Scale)))
            $graphics.DrawImage($cell,$destination,0,0,$cell.Width,$cell.Height,[System.Drawing.GraphicsUnit]::Pixel)
        } finally {$graphics.Dispose()}
        $filename=('{0}_{1:00}.png' -f $Prefix,$index)
        $bitmap.Save((Join-Path $outputPath $filename),[System.Drawing.Imaging.ImageFormat]::Png)
        $finalBounds=[AnimationPackaging]::Bounds($bitmap)
        if($finalBounds.Left -lt 2 -or $finalBounds.Right -gt 510 -or $finalBounds.Top -lt 2 -or $finalBounds.Bottom -gt 480){throw "Clipped or misaligned sprite: $filename"}
        $script:metrics[$filename]=@{visible_bounds=@($finalBounds.X,$finalBounds.Y,$finalBounds.Width,$finalBounds.Height);batch_scale=$Scale;source_pose_index=$index}
        $bitmap
        $index++
    }
}

function Save-Sheet($Frames,[int]$Columns,[string]$Filename) {
    $rows=[int][Math]::Ceiling($Frames.Count/$Columns)
    $sheet=New-Object System.Drawing.Bitmap(($Columns*512),($rows*512),[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $graphics=[System.Drawing.Graphics]::FromImage($sheet)
    try {
        $graphics.Clear([System.Drawing.Color]::Transparent)
        for($index=0;$index -lt $Frames.Count;$index++) {
            $graphics.DrawImageUnscaled($Frames[$index],(($index%$Columns)*512),([int][Math]::Floor($index/$Columns)*512))
        }
        $sheet.Save((Join-Path $outputPath $Filename),[System.Drawing.Imaging.ImageFormat]::Png)
    } finally {$graphics.Dispose();$sheet.Dispose()}
}

function Frame-List([string]$Prefix,$Durations) {
    for($index=0;$index -lt $Durations.Count;$index++) {
        $filename=('{0}_{1:00}.png' -f $Prefix,$index)
        @{filename=$filename;duration_ms=$Durations[$index];body_anchor=@(256,470);visible_bounds=$script:metrics[$filename].visible_bounds}
    }
}

$duckCells=@(Read-Cells 'duck_sheet_source.png' 4 8)
$duckScale=384.0/[AnimationPackaging]::Bounds($duckCells[0]).Height
$duck=@(Save-Frames $duckCells 'sora_crouch_down' $duckScale)
$standCells=@(Read-Cells 'stand_idle_source.png' 5 10)
$standScale=384.0/[AnimationPackaging]::Bounds($standCells[0]).Height
$stand=@(Save-Frames $standCells 'sora_stand_idle' $standScale)
$crouchCells=@(Read-Cells 'crouch_idle_source.png' 2 4)
$crouchHeight=[AnimationPackaging]::Bounds($duck[7]).Height
$crouchScale=$crouchHeight/[double][AnimationPackaging]::Bounds($crouchCells[0]).Height
$crouch=@(Save-Frames $crouchCells 'sora_crouch_idle' $crouchScale)

$up=@()
for($index=0;$index -lt 8;$index++) {
    $filename=('sora_crouch_up_{0:00}.png' -f $index)
    $duck[7-$index].Save((Join-Path $outputPath $filename),[System.Drawing.Imaging.ImageFormat]::Png)
    $up += $duck[7-$index]
    $script:metrics[$filename]=$script:metrics[('sora_crouch_down_{0:00}.png' -f (7-$index))]
}
$duck[0].Save((Join-Path $outputPath 'sora_smooth_stand_guard.png'),[System.Drawing.Imaging.ImageFormat]::Png)
$duck[7].Save((Join-Path $outputPath 'sora_smooth_crouch_guard.png'),[System.Drawing.Imaging.ImageFormat]::Png)

$windup=@();$windupCell=@()
if(Test-Path -LiteralPath (Join-Path $PSScriptRoot 'windup_source.png')) {
    $windupCell=[System.Drawing.Bitmap]::FromFile((Join-Path $PSScriptRoot 'windup_source.png'))
    $windupScale=400.0/[AnimationPackaging]::Bounds($windupCell).Height
    $windup=@(Save-Frames @($windupCell) 'windup_packaged' $windupScale)
    $windup[0].Save((Join-Path $outputPath 'sora_smooth_attack_windup.png'),[System.Drawing.Imaging.ImageFormat]::Png)
}
# The temporary packaged pose stays in the work area and is not an active sprite.

$standDelays=@(150,130,130,150,180,150,130,130,150,180)
$transitionDelays=@(60,50,50,50,50,50,60,80)
$crouchDelays=@(180,160,180,160)
Save-Sheet $stand 5 'sora_stand_idle_sheet.png'
$fullCycle=@($duck)+@($crouch)+@($up)
Save-Sheet $fullCycle 5 'sora_crouch_sheet.png'
[AnimationPackaging]::Gif((Join-Path $outputPath 'sora_stand_idle_preview.gif'),[System.Drawing.Bitmap[]]$stand,[int[]]$standDelays)
[AnimationPackaging]::Gif((Join-Path $outputPath 'sora_crouch_idle_preview.gif'),[System.Drawing.Bitmap[]]$crouch,[int[]]$crouchDelays)
[AnimationPackaging]::Gif((Join-Path $outputPath 'sora_crouch_full_cycle_preview.gif'),[System.Drawing.Bitmap[]]$fullCycle,[int[]](@($transitionDelays)+@($crouchDelays)+@($transitionDelays)))

$common=@{character='Sora';art_style='smooth cel-shaded';canvas_size=@(512,512);ground_baseline_y=470;body_anchor=@(256,470);production='individually generated pose drawings, uniformly packaged per batch';preview_background='opaque dark blue-gray; PNG sprites retain alpha';validation_status='structural checks and visual sheet review; not tested in Godot';attachment_points_status='weapon and anatomical sockets not yet measured';limitations=@('Generated linework and grip details may require artist cleanup.','Standing-up sequence reverses the newly drawn duck poses.','No gameplay integration is supplied.')}
$standManifest=$common.Clone()
$standManifest.animation='standing_breathing_idle';$standManifest.total_frames=10;$standManifest.loop=$true
$standManifest.total_duration_ms=($standDelays|Measure-Object -Sum).Sum
$standManifest.sprite_sheet=@{filename='sora_stand_idle_sheet.png';columns=5;rows=2;dimensions=@(2560,1024);order='row-major'}
$standManifest.frames=@(Frame-List 'sora_stand_idle' $standDelays)
$standManifest|ConvertTo-Json -Depth 10|Set-Content -LiteralPath (Join-Path $outputPath 'sora_stand_idle_manifest.json') -Encoding UTF8
$crouchManifest=$common.Clone()
$crouchManifest.animation='crouching_transitions_and_idle';$crouchManifest.sprite_sheet='sora_crouch_sheet.png'
$crouchManifest.sheet_layout=@{columns=5;rows=4;order='duck_down 00-07, crouching_idle 00-03, stand_up 00-07'}
$crouchManifest.animations=@{
duck_down=@{total_frames=8;loop=$false;total_duration_ms=($transitionDelays|Measure-Object -Sum).Sum;frames=@(Frame-List 'sora_crouch_down' $transitionDelays)}
crouching_idle=@{total_frames=4;loop=$true;total_duration_ms=($crouchDelays|Measure-Object -Sum).Sum;frames=@(Frame-List 'sora_crouch_idle' $crouchDelays)}
stand_up=@{total_frames=8;loop=$false;total_duration_ms=($transitionDelays|Measure-Object -Sum).Sum;source='duck_down artwork in reverse order';frames=@(Frame-List 'sora_crouch_up' $transitionDelays)}
}
$crouchManifest|ConvertTo-Json -Depth 10|Set-Content -LiteralPath (Join-Path $outputPath 'sora_crouch_manifest.json') -Encoding UTF8
$script:metrics|ConvertTo-Json -Depth 6|Set-Content -LiteralPath (Join-Path $PSScriptRoot 'packaging_metrics.json') -Encoding UTF8
foreach($bitmap in @($duck)+@($stand)+@($crouch)+@($windup)+@($duckCells)+@($standCells)+@($crouchCells)+@($windupCell)) {$bitmap.Dispose()}
Get-ChildItem -LiteralPath $outputPath -File|Group-Object Extension|Select-Object Name,Count
& (Join-Path $PSScriptRoot 'organize_animation_flows.ps1')
