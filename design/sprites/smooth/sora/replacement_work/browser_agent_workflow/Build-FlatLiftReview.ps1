param([ValidatePattern('^flat_lift_pilot_v[0-9]+$')][string]$ReviewVersion='flat_lift_pilot_v5')
$ErrorActionPreference = 'Stop'
$soraRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if ($soraRoot -ne 'D:\KH Fighting Game') { throw "Unexpected workspace: $soraRoot" }
$soraBase = Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready/run_start'
$soraOutDir = Join-Path $soraBase "sync_refinement_v2/$ReviewVersion"
$soraBoardPath = Join-Path $soraOutDir 'Three_Pose_Review.png'
if (Test-Path -LiteralPath $soraBoardPath) { throw 'Preserve this review; choose a new version' }
Add-Type -AssemblyName System.Drawing
Add-Type -Path (Join-Path $PSScriptRoot '../AnimationPackaging.cs') -ReferencedAssemblies System.Drawing
$soraPaths = @(
    (Join-Path $soraBase 'direct_imagegen_trial/whole_figure_review_v3/frame_01.png'),
    (Join-Path $soraOutDir 'sora_lift_01_02_midpoint.png'),
    (Join-Path $soraBase 'direct_imagegen_trial/whole_figure_review_v3/frame_02.png')
)
$soraSourceHashes = @($soraPaths | ForEach-Object { (Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash })
$soraLabels = @('01: original predecessor','01.5: local flat-canvas pilot','02: original successor')
$soraFrames = @($soraPaths | ForEach-Object { [System.Drawing.Bitmap]::new($_) })
$soraFont = [System.Drawing.Font]::new('Arial',13)
$soraSmallFont = [System.Drawing.Font]::new('Arial',8)
$soraOpaque = [System.Collections.Generic.List[System.Drawing.Bitmap]]::new()
foreach($soraSize in @(512,128)) {
    $soraBoard = [System.Drawing.Bitmap]::new(3*$soraSize,$soraSize+30)
    $soraGraphics = [System.Drawing.Graphics]::FromImage($soraBoard)
    $soraGraphics.Clear([System.Drawing.Color]::White)
    $soraGraphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $soraGifFrames = [System.Collections.Generic.List[System.Drawing.Bitmap]]::new()
    for($soraIndex=0;$soraIndex -lt 3;$soraIndex++) {
        $soraGraphics.DrawImage($soraFrames[$soraIndex],$soraIndex*$soraSize,0,$soraSize,$soraSize)
        $soraLabel = if($soraSize -eq 128){@('01','01.5: pilot','02')[$soraIndex]}else{$soraLabels[$soraIndex]}
        $soraLabelFont = if($soraSize -eq 128){$soraSmallFont}else{$soraFont}
        $soraGraphics.DrawString($soraLabel,$soraLabelFont,[System.Drawing.Brushes]::Black,$soraIndex*$soraSize+6,$soraSize+4)
        $soraFlat = [System.Drawing.Bitmap]::new($soraSize,$soraSize)
        $soraFlatGraphics = [System.Drawing.Graphics]::FromImage($soraFlat)
        $soraFlatGraphics.Clear([System.Drawing.Color]::White)
        $soraFlatGraphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $soraFlatGraphics.DrawImage($soraFrames[$soraIndex],0,0,$soraSize,$soraSize)
        $soraFlatGraphics.Dispose()
        $soraGifFrames.Add($soraFlat)
    }
    $soraBoardFile = if($soraSize -eq 128){'Three_Pose_128_Review.png'}else{'Three_Pose_Review.png'}
    $soraBoard.Save((Join-Path $soraOutDir $soraBoardFile),[System.Drawing.Imaging.ImageFormat]::Png)
    $soraGraphics.Dispose()
    $soraBoard.Dispose()
    $soraGifFile = if($soraSize -eq 128){'Lift_Three_Pose_128_Once.gif'}else{'Lift_Three_Pose_Once.gif'}
    $soraGifPath = Join-Path $soraOutDir $soraGifFile
    [AnimationPackaging]::Gif($soraGifPath,$soraGifFrames.ToArray(),[int[]]@(180,180,180))
    $soraGifBytes = [System.IO.File]::ReadAllBytes($soraGifPath)
    if ($soraGifBytes[13] -ne 0x21 -or $soraGifBytes[14] -ne 0xFF -or [System.Text.Encoding]::ASCII.GetString($soraGifBytes,16,11) -ne 'NETSCAPE2.0') { throw 'Unexpected GIF packaging' }
    # Newly created diagnostic GIF only: remove the repeat extension for a one-pass lift.
    [System.IO.File]::WriteAllBytes($soraGifPath,[byte[]]($soraGifBytes[0..12]+$soraGifBytes[32..($soraGifBytes.Length-1)]))
    $soraGifCheck = [System.Drawing.Image]::FromFile($soraGifPath)
    if ($soraGifCheck.GetFrameCount([System.Drawing.Imaging.FrameDimension]::Time) -ne 3) { throw 'Wrong lift preview frame count' }
    $soraGifCheck.Dispose()
    foreach($soraFlat in $soraGifFrames){$soraFlat.Dispose()}
}
$soraPreservedFacePixels = 0
for($soraY=120;$soraY -lt 256;$soraY++) { for($soraX=268;$soraX -lt 440;$soraX++) {
    if($soraFrames[0].GetPixel($soraX,$soraY).ToArgb() -ne $soraFrames[1].GetPixel($soraX,$soraY).ToArgb()) { $soraPreservedFacePixels++ }
}}
if($soraPreservedFacePixels -ne 0){throw 'Face/hair inspection area changed'}
for($soraIndex=0;$soraIndex -lt 3;$soraIndex++) {
    if((Get-FileHash -LiteralPath $soraPaths[$soraIndex] -Algorithm SHA256).Hash -ne $soraSourceHashes[$soraIndex]){throw 'Review changed input PNG'}
}
foreach($soraFrame in $soraFrames){$soraFrame.Dispose()}
$soraFont.Dispose()
$soraSmallFont.Dispose()
[ordered]@{
    status='three-pose local pilot review; original endpoints still need weapon/chain consistency'
    frameCount=3
    containsNewPaintedPose=$true
    onePass=$true
    durationMs=540
    unchangedFaceHairPixelsVerified=$true
    sourcesPreserved=$true
    noIndividualProductionLayers=$true
    integration='Not inserted into the final run-start sequence'
    inputs=$soraPaths
    hashes=$soraSourceHashes
} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $soraOutDir 'review_manifest.json') -Encoding UTF8
Write-Output 'Three-pose512/128 boards and one-pass GIFs created;3 GIF frames and face/source preservation verified.'
