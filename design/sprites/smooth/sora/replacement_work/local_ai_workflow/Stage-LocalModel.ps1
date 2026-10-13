param([Parameter(Mandatory=$true)][int]$ExtractorPid)
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraPlan=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'setup_plan.json') -Raw | ConvertFrom-Json
$soraStage=[System.IO.Path]::GetFullPath((Join-Path $soraRoot ('.local/downloads/'+$soraPlan.model.file)))
$soraTarget=[System.IO.Path]::GetFullPath((Join-Path $soraRoot ($soraPlan.runtime.portableRoot+'/ComfyUI/models/checkpoints/'+$soraPlan.model.file)))
foreach($soraPath in @($soraStage,$soraTarget)){if(-not $soraPath.StartsWith($soraRoot+'\',[System.StringComparison]::OrdinalIgnoreCase)){throw 'Model path escaped workspace'}}
if(-not (Test-Path -LiteralPath $soraStage)){
    & curl.exe --fail --location --proto '=https' --proto-redir '=https' --output $soraStage $soraPlan.model.url
    if($LASTEXITCODE -ne 0){throw "Model download failed; partial file preserved: $soraStage"}
}
if((Get-Item -LiteralPath $soraStage).Length -ne $soraPlan.model.sizeBytes){throw 'Staged model size mismatch; preserved'}
if((Get-FileHash -LiteralPath $soraStage -Algorithm SHA256).Hash.ToLowerInvariant() -ne $soraPlan.model.sha256){throw 'Staged model SHA256 mismatch; preserved'}
$soraExtractor=Get-Process -Id $ExtractorPid -ErrorAction SilentlyContinue
if($soraExtractor -and $soraExtractor.ProcessName -eq '7z' -and -not (Test-Path -LiteralPath $soraTarget)){
    # Same-volume placement is quick. The existing installer waits for this extractor,
    # then checks the completed checkpoint hash before using it. No partial target.
    New-Item -ItemType Directory -Force -Path (Split-Path $soraTarget -Parent) | Out-Null
    Move-Item -LiteralPath $soraStage -Destination $soraTarget
    Write-Output 'Verified model placed while extraction is active; installer will verify it again.'
}else{
    Write-Output "Verified model retained in staging; extraction ended or target already exists: $soraStage"
}
