$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraPlan=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'setup_plan.json') -Raw | ConvertFrom-Json
function SoraPath([string]$Relative){
    $soraFull=[System.IO.Path]::GetFullPath((Join-Path $soraRoot $Relative))
    if(-not $soraFull.StartsWith($soraRoot+'\',[System.StringComparison]::OrdinalIgnoreCase)){throw 'Path escaped workspace'}
    return $soraFull
}
$soraArchive=SoraPath $soraPlan.runtime.archive
$soraDestination=SoraPath $soraPlan.runtime.installRoot
$soraPortable=SoraPath $soraPlan.runtime.portableRoot
if(Get-Process -Name 7z -ErrorAction SilentlyContinue){throw 'A 7z process is active; inspect before runtime repair'}
if(Test-Path -LiteralPath (Join-Path $soraDestination 'installation_receipt.json')){throw 'Installation receipt already exists; inspect instead of repeating repair'}
if((Get-Item -LiteralPath $soraArchive).Length -ne $soraPlan.runtime.sizeBytes -or (Get-FileHash -LiteralPath $soraArchive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $soraPlan.runtime.sha256){throw 'Pinned archive differs; preserved'}
$soraSeven=(Get-Command 7z.exe -ErrorAction Stop).Source
$soraListing=(& $soraSeven l -slt $soraArchive) -join "`n"
if($LASTEXITCODE -ne 0){throw 'Archive listing failed'}
if($soraListing -match '(?m)^(Symbolic Link|Hard Link) ='){throw 'Archive links require inspection'}
Add-Type -TypeDefinition @'
using System;
using System.IO;
using System.Collections.Generic;
using System.Text.RegularExpressions;
public class SoraExtractionIssue {
    public string path, reason, expectedCrc, actualCrc;
    public long expectedBytes, actualBytes;
}
public class SoraExtractionAudit {
    public int checkedFiles, validFiles;
    public List<SoraExtractionIssue> issues=new List<SoraExtractionIssue>();
}
public static class SoraPortableAudit {
    static readonly uint[] table=MakeTable();
    static uint[] MakeTable(){var t=new uint[256];for(uint n=0;n<256;n++){uint c=n;for(int k=0;k<8;k++)c=(c&1)!=0?0xedb88320U^(c>>1):c>>1;t[n]=c;}return t;}
    static string Crc(string file){
        uint c=0xffffffffU;byte[] b=new byte[1024*1024];
        using(var s=new FileStream(file,FileMode.Open,FileAccess.Read,FileShare.Read,1024*1024,FileOptions.SequentialScan)){
            int n;while((n=s.Read(b,0,b.Length))>0)for(int i=0;i<n;i++)c=table[(c^b[i])&255]^(c>>8);
        }
        return (c^0xffffffffU).ToString("X8");
    }
    static string Field(string block,string name){return Regex.Match(block,"(?m)^"+Regex.Escape(name)+" = (.*)$").Groups[1].Value.Trim();}
    public static SoraExtractionAudit Audit(string listing,string destination,string[] only){
        var result=new SoraExtractionAudit();
        HashSet<string> selected=only==null?null:new HashSet<string>(only,StringComparer.OrdinalIgnoreCase);
        var parts=Regex.Split(listing,"----------\\r?\\n",RegexOptions.None,TimeSpan.FromSeconds(5));
        if(parts.Length!=2)throw new Exception("Unrecognized archive listing");
        foreach(var block in Regex.Split(parts[1],"\\r?\\n\\r?\\n")){
            string entry=Field(block,"Path");if(entry=="")continue;
            if(Path.IsPathRooted(entry)||entry.Contains(":")||Array.IndexOf(entry.Split('\\','/'),"..")>=0)throw new Exception("Unsafe archive entry");
            string full=Path.GetFullPath(Path.Combine(destination,entry));
            if(!full.StartsWith(destination+"\\",StringComparison.OrdinalIgnoreCase))throw new Exception("Archive entry escaped target");
            if(Field(block,"Attributes").StartsWith("D"))continue;
            if(selected!=null&&!selected.Contains(entry))continue;
            long bytes=long.Parse(Field(block,"Size"));string expected=Field(block,"CRC");
            if(expected==""&&bytes==0)expected="00000000";
            if(!Regex.IsMatch(expected,"^[0-9A-Fa-f]{8}$"))throw new Exception("Missing archive CRC");
            result.checkedFiles++;
            var issue=new SoraExtractionIssue{path=entry,expectedBytes=bytes,expectedCrc=expected};
            if(!File.Exists(full)){issue.reason="missing";result.issues.Add(issue);}
            else {
                issue.actualBytes=new FileInfo(full).Length;
                if(issue.actualBytes!=bytes){issue.reason="size_mismatch";result.issues.Add(issue);}
                else {issue.actualCrc=Crc(full);if(!String.Equals(issue.actualCrc,expected,StringComparison.OrdinalIgnoreCase)){issue.reason="crc_mismatch";result.issues.Add(issue);}else result.validFiles++;}
            }
            if(result.checkedFiles%5000==0)Console.WriteLine("Verified "+result.checkedFiles+" archive files");
        }
        return result;
    }
}
'@
$soraRecovery=SoraPath ('.local/comfyui-recovery/'+[DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss_fff'))
New-Item -ItemType Directory -Path $soraRecovery | Out-Null
Write-Output 'Auditing every existing runtime file against the verified archive CRC; no artwork is involved.'
$soraBefore=[SoraPortableAudit]::Audit($soraListing,$soraDestination,$null)
$soraBefore | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $soraRecovery 'audit_before.json') -Encoding UTF8
Write-Output "Existing files validated: $($soraBefore.validFiles); missing/damaged: $($soraBefore.issues.Count)"
if(@($soraBefore.issues | Where-Object reason -eq 'crc_mismatch').Count -gt 8){throw 'Unexpected broad CRC mismatch; inspect saved audit before changing runtime files'}
if($soraBefore.issues.Count -gt 0){
    $soraNeeded=3GB
    foreach($soraIssue in $soraBefore.issues){$soraNeeded+=$soraIssue.expectedBytes+$soraIssue.actualBytes}
    if(([System.IO.DriveInfo]::new('D:\')).AvailableFreeSpace -lt $soraNeeded){throw 'Insufficient room for preserved damaged files and runtime repair'}
    foreach($soraIssue in $soraBefore.issues){
        if($soraIssue.reason -ne 'missing'){
            $soraOriginal=[System.IO.Path]::GetFullPath((Join-Path $soraDestination $soraIssue.path))
            $soraCopy=[System.IO.Path]::GetFullPath((Join-Path (Join-Path $soraRecovery 'preserved') $soraIssue.path))
            if(-not $soraOriginal.StartsWith($soraDestination+'\',[System.StringComparison]::OrdinalIgnoreCase) -or -not $soraCopy.StartsWith($soraRecovery+'\',[System.StringComparison]::OrdinalIgnoreCase)){throw 'Preservation path escaped runtime/recovery folder'}
            New-Item -ItemType Directory -Force -Path (Split-Path $soraCopy -Parent) | Out-Null
            Copy-Item -LiteralPath $soraOriginal -Destination $soraCopy
        }
    }
    $soraTargets=@($soraBefore.issues | ForEach-Object path)
    $soraList=Join-Path $soraRecovery 'repair_entries.txt'
    [System.IO.File]::WriteAllLines($soraList,[string[]]$soraTargets,[System.Text.UTF8Encoding]::new($false))
    # Restore only missing/damaged package entries, after preserving damaged bytes.
    & $soraSeven x $soraArchive "@$soraList" "-o$soraDestination" -scsUTF-8 -aoa -y
    if($LASTEXITCODE -ne 0){throw 'Targeted extraction failed; audit and damaged originals preserved'}
    $soraAfter=[SoraPortableAudit]::Audit($soraListing,$soraDestination,[string[]]$soraTargets)
    $soraAfter | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $soraRecovery 'audit_repaired.json') -Encoding UTF8
    if($soraAfter.issues.Count -ne 0 -or $soraAfter.validFiles -ne $soraTargets.Count){throw 'Repaired runtime entries did not verify'}
}
$soraPython=Join-Path $soraPortable 'python_embeded/python.exe'
if(-not (Test-Path -LiteralPath $soraPython)){throw 'Runtime remains incomplete'}
$soraCheckpoint=Join-Path $soraPortable ('ComfyUI/models/checkpoints/'+$soraPlan.model.file)
if((Get-Item -LiteralPath $soraCheckpoint).Length -ne $soraPlan.model.sizeBytes -or (Get-FileHash -LiteralPath $soraCheckpoint -Algorithm SHA256).Hash.ToLowerInvariant() -ne $soraPlan.model.sha256){throw 'Pinned model differs; preserved'}
$soraProbe=(& $soraPython -s (Join-Path $PSScriptRoot 'check_cuda.py')) -join "`n"
if($LASTEXITCODE -ne 0){throw 'Portable torch probe failed; repaired runtime preserved'}
$soraProbe | ConvertFrom-Json | Out-Null
$soraRecoverySummary=[ordered]@{clientWorkDate='2026-10-14';recoveryFolder=$soraRecovery;archiveFilesVerified=$soraBefore.checkedFiles;initialValid=$soraBefore.validFiles;repairedCount=$soraBefore.issues.Count;allArchiveFilesVerified=$true;modelSizeAndSha256Verified=$true;torchProbe=$soraProbe;generationStatus='not submitted';artworkApproval='pending'}
$soraRecoverySummary | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'Runtime_Validation.json') -Encoding UTF8
[ordered]@{installedAtUtc=[DateTime]::UtcNow.ToString('o');runtime=$soraPlan.runtime;model=$soraPlan.model;torchProbe=$soraProbe;archiveExpandedBytes=5580961635;recovery=$soraRecoverySummary;status='Installed and integrity checked; generation and artwork not yet validated'} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $soraDestination 'installation_receipt.json') -Encoding UTF8
Write-Output $soraProbe
Write-Output 'Runtime recovery and checkpoint integrity verified. No image generated or existing sprite replaced.'
