param(
    [Parameter(Mandatory=$true)][string]$PromptFile,
    [ValidateSet('run_start','run_loop','run_stop')][string]$Animation = 'run_loop',
    [ValidateRange(1,999)][int]$Attempt = 2,
    [ValidateRange(1024,65535)][int]$Port = 9222
)
$ErrorActionPreference = 'Stop'
$workspaceRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../../../../..'))
if($workspaceRoot.TrimEnd('\') -ine 'D:\KH Fighting Game'){throw 'Check workspace paths before running.'}
$output = Join-Path $workspaceRoot ('design/sprites/smooth/sora/replacement_work/ready/' + $Animation + '/gemini_browser_trial/attempt_' + $Attempt.ToString('00'))
$driver = Join-Path $PSScriptRoot 'gemini_cdp.mjs'
# The Node driver validates prompt/output paths and resumes collection safely.
& node $driver exchange --port $Port --prompt $PromptFile --output $output
exit $LASTEXITCODE
