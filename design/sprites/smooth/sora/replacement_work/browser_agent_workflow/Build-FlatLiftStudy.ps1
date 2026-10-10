param([ValidatePattern('^flat_lift_pilot_v[0-9]+$')][string]$ReviewVersion='flat_lift_pilot_v5')
$ErrorActionPreference = 'Stop'
$soraRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if ($soraRoot -ne 'D:\KH Fighting Game') { throw "Unexpected workspace: $soraRoot" }
$soraBase = Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready/run_start'
$soraPrevious = Join-Path $soraBase 'sync_refinement_v1/timing_review_v1'
$soraPilotDir = Join-Path $soraBase "sync_refinement_v2/$ReviewVersion"
$soraOutDir = Join-Path $soraPilotDir 'full_start_study'
if ((Test-Path -LiteralPath $soraOutDir) -and @(Get-ChildItem -LiteralPath $soraOutDir -Force).Count -gt 0) { throw 'Preserve existing study; choose a new version' }
$soraOldManifest = Get-Content -LiteralPath (Join-Path $soraPrevious 'manifest.json') -Raw | ConvertFrom-Json
$soraPilot = Join-Path $soraPilotDir 'sora_lift_01_02_midpoint.png'
$soraOriginal = Join-Path $soraBase 'direct_imagegen_trial/attempt_03/sora_run_start_original.png'
$soraOriginalHash = (Get-FileHash -LiteralPath $soraOriginal -Algorithm SHA256).Hash.ToLowerInvariant()
if ($soraOriginalHash -ne '6108be48aa93f736514c1860f1a9966de1998b0800814156c681321cb779530e') { throw 'Selected original changed' }
Add-Type -AssemblyName System.Drawing
Add-Type -Path (Join-Path $PSScriptRoot '../AnimationPackaging.cs') -ReferencedAssemblies System.Drawing
New-Item -ItemType Directory -Path $soraOutDir -Force | Out-Null
$soraRecords = [System.Collections.Generic.List[object]]::new()
foreach($soraOld in $soraOldManifest.frames) {
    $soraPath = Join-Path $soraPrevious $soraOld.file
    $soraHash = (Get-FileHash -LiteralPath $soraPath -Algorithm SHA256).Hash.ToLowerInvariant()
    if($soraHash -ne $soraOld.sha256){throw 'Registered source changed'}
    $soraDuration = if($soraOld.index -eq 1){40}else{[int]$soraOld.durationMs}
    $soraRecords.Add([pscustomobject][ordered]@{index=$soraRecords.Count;sourceIndex=$soraOld.index;sourcePath=$soraPath;phase=$soraOld.phase;durationMs=$soraDuration;file=('frame_{0:00}.png' -f $soraRecords.Count);sha256=$soraHash})
    if($soraOld.index -eq 1) {
        $soraRecords.Add([pscustomobject][ordered]@{index=$soraRecords.Count;sourceIndex=1.5;sourcePath=$soraPilot;phase='Local early-lift midpoint';durationMs=40;file=('frame_{0:00}.png' -f $soraRecords.Count);sha256=(Get-FileHash -LiteralPath $soraPilot -Algorithm SHA256).Hash.ToLowerInvariant()})
    }
}
if($soraRecords.Count -ne 13){throw 'Expected12 original drawings and1 locally painted intermediate'}
$soraDurationSum = ($soraRecords | Measure-Object -Property durationMs -Sum).Sum
if($soraDurationSum -ne $soraOldManifest.sequenceDurationMs){throw 'Study changed overall display duration'}
foreach($soraRecord in $soraRecords) {
    Copy-Item -LiteralPath $soraRecord.sourcePath -Destination (Join-Path $soraOutDir $soraRecord.file)
    if((Get-FileHash -LiteralPath (Join-Path $soraOutDir $soraRecord.file) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $soraRecord.sha256){throw 'Copied complete pose changed'}
}
foreach($soraSize in @(512,128)) {
    $soraGifFrames = [System.Collections.Generic.List[System.Drawing.Bitmap]]::new()
    foreach($soraRecord in $soraRecords) {
        $soraImage = [System.Drawing.Bitmap]::new((Join-Path $soraOutDir $soraRecord.file))
        $soraFlat = [System.Drawing.Bitmap]::new($soraSize,$soraSize)
        $soraGraphics = [System.Drawing.Graphics]::FromImage($soraFlat)
        $soraGraphics.Clear([System.Drawing.Color]::White)
        $soraGraphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $soraGraphics.DrawImage($soraImage,0,0,$soraSize,$soraSize)
        $soraGraphics.Dispose()
        $soraImage.Dispose()
        $soraGifFrames.Add($soraFlat)
    }
    $soraGifName = if($soraSize -eq 128){'Run_Start_13_128_Once.gif'}else{'Run_Start_13_Once.gif'}
    $soraGifPath = Join-Path $soraOutDir $soraGifName
    [AnimationPackaging]::Gif($soraGifPath,$soraGifFrames.ToArray(),[int[]]@($soraRecords | ForEach-Object {$_.durationMs}))
    $soraBytes = [System.IO.File]::ReadAllBytes($soraGifPath)
    if([System.Text.Encoding]::ASCII.GetString($soraBytes,16,11) -ne 'NETSCAPE2.0'){throw 'Unexpected repeat extension'}
    [System.IO.File]::WriteAllBytes($soraGifPath,[byte[]]($soraBytes[0..12]+$soraBytes[32..($soraBytes.Length-1)]))
    $soraCheck = [System.Drawing.Image]::FromFile($soraGifPath)
    if($soraCheck.GetFrameCount([System.Drawing.Imaging.FrameDimension]::Time) -ne 13){throw 'Wrong study frame count'}
    $soraCheck.Dispose()
    foreach($soraFlat in $soraGifFrames){$soraFlat.Dispose()}
}
$soraData = ConvertTo-Json -InputObject $soraRecords.ToArray() -Depth 5 -Compress
$soraHtml = Get-Content -LiteralPath (Join-Path $soraPrevious 'Review.html') -Raw
$soraDataPattern = '(?s)const frames=.*?;\r?\nconst large='
if(([regex]::Matches($soraHtml,$soraDataPattern)).Count -ne 1){throw 'Existing HTML data declaration changed'}
$soraHtml = [regex]::Replace($soraHtml,$soraDataPattern,"const frames=$soraData;`nconst large=")
$soraHtml = $soraHtml.Replace('max="11"','max="12"').Replace('<h1>Sora: run start</h1>','<h1>Sora: early-lift study</h1>')
$soraHtml = $soraHtml.Replace('12 complete poses. Play once, or scrub to compare the lift and first step.','13 poses with one locally painted intermediate. Compare the new lift with its neighbors; the remaining weapon and pose gaps still need refinement.')
$soraHtml = $soraHtml.Replace('Artwork quality is retained. New intermediate drawings and consistent weapon projection are still needed at the larger gaps.','Draft study:12 original drawings and1 flat-canvas pilot. Original endpoint chains, guard projection, the later lift and first-step gaps remain unfinished.')
Set-Content -LiteralPath (Join-Path $soraOutDir 'Review.html') -Value $soraHtml -Encoding UTF8
[ordered]@{status='13-pose study only; not final sequence approval';frameCount=13;newDrawingCount=1;sourceDrawingsRetained=12;durationMs=$soraDurationSum;onePass=$true;noIndividualProductionLayers=$true;originalSha256=$soraOriginalHash;frames=$soraRecords.ToArray();timing='Original01 duration80 split into40+40 with a new pose, total860ms retained; GIF resolution10ms';integration='No engine assets replaced'} | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath (Join-Path $soraOutDir 'manifest.json') -Encoding UTF8
if((Get-FileHash -LiteralPath $soraOriginal -Algorithm SHA256).Hash.ToLowerInvariant() -ne $soraOriginalHash){throw 'Original changed during packaging'}
Write-Output '13-pose study created;12 original drawings preserved,1 new flat-canvas midpoint,860ms display timing,13-frame one-pass GIFs verified.'
