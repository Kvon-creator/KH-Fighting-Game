$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraPlan=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'setup_plan.json') -Raw | ConvertFrom-Json
$soraPortable=[System.IO.Path]::GetFullPath((Join-Path $soraRoot $soraPlan.runtime.portableRoot))
if(-not $soraPortable.StartsWith($soraRoot+'\',[System.StringComparison]::OrdinalIgnoreCase)){throw 'Runtime escaped workspace'}
$soraPython=Join-Path $soraPortable 'python_embeded/python.exe'
if(-not (Test-Path -LiteralPath $soraPython)){throw 'Prepared runtime is not installed'}
try{$soraExisting=Invoke-RestMethod -Uri ($soraPlan.endpoint+'/system_stats') -TimeoutSec 3}catch{$soraExisting=$null}
if($soraExisting){if(-not $soraExisting.system -or $null -eq $soraExisting.devices){throw 'Port8188 does not identify a ComfyUI server'};Write-Output 'Existing ComfyUI server detected; inspect it before using';return}
$soraLogs=Join-Path $soraRoot '.local/comfyui-session';New-Item -ItemType Directory -Force -Path $soraLogs | Out-Null
# These settings affect this short-lived launcher and its child, not user/system settings.
$soraCache=Join-Path $soraRoot '.local/comfyui-cache'
New-Item -ItemType Directory -Force -Path $soraCache | Out-Null
$env:HF_HOME=Join-Path $soraCache 'huggingface'
$env:TORCH_HOME=Join-Path $soraCache 'torch'
$env:CUDA_CACHE_PATH=Join-Path $soraCache 'cuda'
$env:HF_HUB_OFFLINE='1';$env:TRANSFORMERS_OFFLINE='1';$env:PYTHONNOUSERSITE='1'
$soraStamp=[DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss_fff')
$soraArgs=@('-s','ComfyUI/main.py','--listen','127.0.0.1','--port','8188','--disable-auto-launch','--offline','--disable-all-custom-nodes','--disable-dynamic-vram','--lowvram','--cpu-vae','--cache-none','--use-split-cross-attention','--reserve-vram','0.7')
$soraProcess=Start-Process -FilePath $soraPython -ArgumentList $soraArgs -WorkingDirectory $soraPortable -WindowStyle Hidden -RedirectStandardOutput (Join-Path $soraLogs "$soraStamp.stdout.log") -RedirectStandardError (Join-Path $soraLogs "$soraStamp.stderr.log") -PassThru
[ordered]@{pid=$soraProcess.Id;endpoint=$soraPlan.endpoint;arguments=$soraArgs;stdout="$soraStamp.stdout.log";stderr="$soraStamp.stderr.log";status='starting; API/generation unverified'} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $soraLogs "$soraStamp.launch.json") -Encoding UTF8
Write-Output "ComfyUI launch requested, PID$($soraProcess.Id). Read status before generating."
