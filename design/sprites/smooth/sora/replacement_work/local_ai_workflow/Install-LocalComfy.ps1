param([switch]$Install)
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraPlan=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'setup_plan.json') -Raw | ConvertFrom-Json
function SoraPath([string]$Relative){
    $soraFull=[System.IO.Path]::GetFullPath((Join-Path $soraRoot $Relative))
    if(-not $soraFull.StartsWith($soraRoot+'\',[System.StringComparison]::OrdinalIgnoreCase)){throw 'Path escaped workspace'}
    return $soraFull
}
function SoraVerify([string]$File,[long]$Bytes,[string]$Sha){
    if((Get-Item -LiteralPath $File).Length -ne $Bytes){throw "Size mismatch; preserved $File"}
    if((Get-FileHash -LiteralPath $File -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Sha){throw "Hash mismatch; preserved $File"}
}
function SoraDownload([string]$Uri,[string]$File,[long]$Bytes,[string]$Sha){
    if(-not (Test-Path -LiteralPath $File)){
        # No automatic network retries or partial-file overwrites. Verify before use.
        & curl.exe --fail --location --proto '=https' --proto-redir '=https' --output $File $Uri
        if($LASTEXITCODE -ne 0){throw "Download failed; any partial file preserved at $File"}
    }
    SoraVerify $File $Bytes $Sha
}
if(-not $Install){$soraPlan | ConvertTo-Json -Depth 8;return}
# Run -Install only after the user authorizes this specific prepared installation.
$soraArchive=SoraPath $soraPlan.runtime.archive;$soraDestination=SoraPath $soraPlan.runtime.installRoot
$soraPortable=SoraPath $soraPlan.runtime.portableRoot
if(Test-Path -LiteralPath $soraDestination){throw 'Preserve existing installation/partial extraction; inspect it before retrying'}
$soraDrive=Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='D:'"
if($soraDrive.FreeSpace -lt 16GB){throw 'At least16GiB free required for this prepared portable installation'}
$soraSeven=(Get-Command 7z.exe -ErrorAction Stop).Source
New-Item -ItemType Directory -Force -Path (Split-Path $soraArchive -Parent) | Out-Null
SoraDownload $soraPlan.runtime.url $soraArchive $soraPlan.runtime.sizeBytes $soraPlan.runtime.sha256
$soraListing=(& $soraSeven l -slt $soraArchive) -join "`n"
if($LASTEXITCODE -ne 0){throw 'Archive listing failed'}
$soraParts=$soraListing -split '----------\r?\n',2
if($soraParts.Count -ne 2){throw 'Unrecognized archive listing'}
$soraEntries=$soraParts[1]
if($soraEntries -match '(?m)^(Symbolic Link|Hard Link) ='){throw 'Archive links require inspection'}
foreach($soraMatch in [regex]::Matches($soraEntries,'(?m)^Path = (.+)$')){
    $soraEntry=$soraMatch.Groups[1].Value.Trim()
    if([System.IO.Path]::IsPathRooted($soraEntry) -or $soraEntry -match ':' -or ($soraEntry -split '[\\/]') -contains '..'){throw 'Unsafe archive entry'}
    $soraEntryPath=[System.IO.Path]::GetFullPath((Join-Path $soraDestination $soraEntry))
    if(-not $soraEntryPath.StartsWith($soraDestination+'\',[System.StringComparison]::OrdinalIgnoreCase)){throw 'Archive entry escaped target'}
}
$soraExpanded=0L
foreach($soraMatch in [regex]::Matches($soraEntries,'(?m)^Size = (\d+)\r?$')){$soraExpanded+=[long]$soraMatch.Groups[1].Value}
$soraDrive=Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='D:'"
if($soraDrive.FreeSpace -lt ($soraExpanded+$soraPlan.model.sizeBytes+3GB)){throw 'Insufficient space after inspected archive expansion'}
New-Item -ItemType Directory -Path $soraDestination | Out-Null
& $soraSeven x $soraArchive "-o$soraDestination" -y
if($LASTEXITCODE -ne 0){throw 'Extraction failed; partial installation preserved'}
$soraPython=Join-Path $soraPortable 'python_embeded/python.exe'
if(-not (Test-Path -LiteralPath $soraPython)){throw 'Portable archive layout differs from prepared plan'}
$soraCheckpoint=Join-Path $soraPortable "ComfyUI/models/checkpoints/$($soraPlan.model.file)"
SoraDownload $soraPlan.model.url $soraCheckpoint $soraPlan.model.sizeBytes $soraPlan.model.sha256
$soraProbe=(& $soraPython -s (Join-Path $PSScriptRoot 'check_cuda.py')) -join "`n"
if($LASTEXITCODE -ne 0){throw 'Portable torch probe failed; installation preserved'}
$soraReceipt=[ordered]@{installedAtUtc=[DateTime]::UtcNow.ToString('o');runtime=$soraPlan.runtime;model=$soraPlan.model;torchProbe=$soraProbe;archiveExpandedBytes=$soraExpanded;status='Installed; generation and artwork not yet validated'}
$soraReceipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $soraDestination 'installation_receipt.json') -Encoding UTF8
Write-Output $soraProbe
Write-Output 'Pinned local runtime/model installed. No image generated or existing asset replaced.'
