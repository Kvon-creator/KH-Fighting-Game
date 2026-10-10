param(
    [ValidateRange(1024, 65535)][int]$Port = 9222,
    [string]$BravePath = 'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe',
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
$workspaceRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../../../../..'))
if ($workspaceRoot.TrimEnd('\') -ine 'D:\KH Fighting Game') {
    throw "Unexpected workspace: $workspaceRoot. Check paths before launching."
}
$profilePath = [IO.Path]::GetFullPath((Join-Path $workspaceRoot ".local/browser-agent/brave-$Port"))
if (-not $profilePath.StartsWith($workspaceRoot.TrimEnd('\') + '\', [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Profile must remain inside the workspace.'
}
$endpoint = "http://127.0.0.1:$Port"
function Read-DebugEndpoint {
    try { return Invoke-RestMethod -Uri "$endpoint/json/version" -TimeoutSec 2 }
    catch { return $null }
}
$version = Read-DebugEndpoint
if (-not $version) {
    if ($CheckOnly) { throw "No browser debugging endpoint at $endpoint." }
    $probe = New-Object Net.Sockets.TcpClient
    try {
        $result = $probe.BeginConnect('127.0.0.1', $Port, $null, $null)
        if ($result.AsyncWaitHandle.WaitOne(500) -and $probe.Connected) {
            throw "Port $Port is occupied by a service that is not a browser debugging endpoint."
        }
    } finally { $probe.Dispose() }
    if (-not (Test-Path -LiteralPath $BravePath -PathType Leaf)) {
        throw "Brave executable not found: $BravePath. Supply -BravePath with its installed path."
    }
    New-Item -ItemType Directory -Path $profilePath -Force | Out-Null
    $launchArgs = @(
        "--remote-debugging-port=$Port",
        '--remote-debugging-address=127.0.0.1',
        ('--user-data-dir="' + $profilePath + '"'),
        '--no-first-run',
        '--new-window',
        'https://gemini.google.com/app'
    )
    # A visible window is intentional: the user signs in to Google themselves.
    Start-Process -FilePath $BravePath -ArgumentList $launchArgs | Out-Null
    for ($attempt = 0; $attempt -lt 20; $attempt++) {
        Start-Sleep -Milliseconds 500
        $version = Read-DebugEndpoint
        if ($version) { break }
    }
    if (-not $version) { throw "Brave launched, but the endpoint did not become ready at $endpoint." }
}
# Verify the listener belongs to this dedicated Brave profile before attaching.
$listeners = @(Get-NetTCPConnection -State Listen -LocalPort $Port)
if (-not $listeners.Count) { throw 'Cannot verify the debugging listener.' }
foreach ($listener in $listeners) {
    if ($listener.LocalAddress -notin @('127.0.0.1', '::1')) {
        throw 'Debugging listener is not restricted to loopback. Do not attach.'
    }
    $owner = Get-CimInstance Win32_Process -Filter ("ProcessId = " + $listener.OwningProcess)
    if ($owner.ExecutablePath -ine $BravePath -or
        -not $owner.CommandLine.Contains($profilePath)) {
        throw "Port $Port does not belong to the dedicated Brave profile. Do not attach."
    }
}
[pscustomobject]@{
    Endpoint = $endpoint
    Browser = $version.Browser
    Profile = $profilePath
    Agent = 'https://gemini.google.com/app'
    NextStep = 'Sign in to Gemini yourself in the separate Brave window, then tell Codex it is ready.'
} | ConvertTo-Json
