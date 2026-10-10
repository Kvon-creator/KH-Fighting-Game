param([ValidatePattern('^flat_lift_pilot_v[0-9]+$')][string]$ReviewVersion='flat_lift_pilot_v5')
$ErrorActionPreference = 'Stop'
$soraRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if ($soraRoot -ne 'D:\KH Fighting Game') { throw "Unexpected workspace: $soraRoot" }
$soraSourcePath = Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready/run_start/direct_imagegen_trial/whole_figure_review_v3/frame_01.png'
$soraOutDir = Join-Path $soraRoot "design/sprites/smooth/sora/replacement_work/ready/run_start/sync_refinement_v2/$ReviewVersion"
$soraTargetPath = Join-Path $soraOutDir 'sora_lift_01_02_midpoint.png'
$soraBeforeHash = (Get-FileHash -LiteralPath $soraSourcePath -Algorithm SHA256).Hash.ToLowerInvariant()
Add-Type -AssemblyName System.Drawing
Add-Type -Path (Join-Path $PSScriptRoot 'FlatLiftPainting.cs') -ReferencedAssemblies System.Drawing
New-Item -ItemType Directory -Path $soraOutDir -Force | Out-Null
[FlatLiftPainting]::Paint($soraSourcePath,$soraTargetPath)
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'FlatLiftPainting.cs') -Destination (Join-Path $soraOutDir 'Painter_Source.cs')
if ((Get-FileHash -LiteralPath $soraSourcePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $soraBeforeHash) { throw 'Source changed' }
$soraManifest = [ordered]@{
    status='flat-canvas local painting pilot; visual inspection pending; not inserted'
    method='System.Drawing direct painting on one complete512px RGBA bitmap; no separate production layers'
    source='design/sprites/smooth/sora/replacement_work/ready/run_start/direct_imagegen_trial/whole_figure_review_v3/frame_01.png'
    sourceSha256=$soraBeforeHash
    target='sora_lift_01_02_midpoint.png'
    targetSha256=(Get-FileHash -LiteralPath $soraTargetPath -Algorithm SHA256).Hash.ToLowerInvariant()
    intent='Early-lift midpoint between source01 and02; grounded body retained, far shoulder/elbow/wrist/hand/weapon genuinely painted'
    gripCenter=@(218,257)
    shaftAngleDegrees=-115
    rigidGripToTipUnits=209
    connectedParts='guard, handle, collar, shaft, crown and pommel painted in one rigid local coordinate system directly into the whole sprite'
    preserves='Face/hair beyondx279, empty near arm and lower body belowy355 verified pixel-identical; source file hash unchanged'
    permission='User explicitly selected single flat canvas locally after two image-service output refusals'
    integration='No engine integration or final animation approval'
}
$soraManifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $soraOutDir 'manifest.json') -Encoding UTF8
