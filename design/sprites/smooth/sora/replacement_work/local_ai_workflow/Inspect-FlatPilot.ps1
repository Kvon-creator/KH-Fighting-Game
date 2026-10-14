param([ValidatePattern('^attempt_[0-9]{2,}$')][string]$Attempt='attempt_02',[ValidatePattern('^(candidate_[0-9]{2}|final_pose_v[0-9]+)\.png$')][string]$Candidate='candidate_00.png')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
function SoraPath([string]$Relative){
    $soraFull=[System.IO.Path]::GetFullPath((Join-Path $soraRoot $Relative))
    if(-not $soraFull.StartsWith($soraRoot+'\',[System.StringComparison]::OrdinalIgnoreCase)){throw 'Path escaped workspace'}
    return $soraFull
}
$soraOut=SoraPath "design/sprites/smooth/sora/replacement_work/ready/run_loop/comfyui_trial/$Attempt"
$soraReceipt=Get-Content -LiteralPath (Join-Path $soraOut 'receipt.json') -Raw | ConvertFrom-Json
if($soraReceipt.status -ne 'generated_pending_review' -or $soraReceipt.files.Count -ne 1 -or -not $soraReceipt.mask){throw 'Collect one complete selected-canvas result before checking'}
$soraSource=SoraPath $soraReceipt.reference;$soraSelection=SoraPath $soraReceipt.mask
$soraNative=Join-Path $soraOut 'candidate_00.png';$soraCandidate=Join-Path $soraOut $Candidate
foreach($soraCheck in @(@($soraSource,$soraReceipt.referenceSha256),@($soraSelection,$soraReceipt.maskSha256),@($soraNative,$soraReceipt.files[0].sha256),@((SoraPath $soraReceipt.sourceSheet),$soraReceipt.sourceSheetSha256))){if((Get-FileHash -LiteralPath $soraCheck[0] -Algorithm SHA256).Hash.ToLowerInvariant() -ne $soraCheck[1]){throw 'Source/selection/native image hash changed'}}
$soraProtectedSource=$soraSource;$soraCandidateSha=$soraReceipt.files[0].sha256
if($Candidate -ne 'candidate_00.png'){
    $soraRefinement=Get-Content -LiteralPath (Join-Path $soraOut 'refinement_manifest.json') -Raw | ConvertFrom-Json
    $soraProtectedSource=SoraPath $soraRefinement.protectedReference;$soraCandidateSha=$soraRefinement.sha256
    if($soraRefinement.file -ne $Candidate -or $soraRefinement.sourceNativeSha256 -ne $soraReceipt.files[0].sha256 -or (Get-FileHash -LiteralPath $soraCandidate -Algorithm SHA256).Hash.ToLowerInvariant() -ne $soraCandidateSha -or (Get-FileHash -LiteralPath $soraProtectedSource -Algorithm SHA256).Hash.ToLowerInvariant() -ne $soraRefinement.protectedReferenceSha256){throw 'Refinement/protected baseline differs'}
}
Add-Type -AssemblyName System.Drawing
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System;
using System.Drawing;
public class SoraFlatPixels {
    public int selectedPixels, changedSelectedPixels, outsidePixels, changedOutsidePixels;
    public int[] changedProtectedRectangles=new int[3];
}
public static class SoraFlatPixelCheck {
    public static SoraFlatPixels Inspect(string source,string selection,string candidate,string protectedSource){
        var result=new SoraFlatPixels();
        using(var a=new Bitmap(source))using(var m=new Bitmap(selection))using(var b=new Bitmap(candidate))using(var p=new Bitmap(protectedSource)){
            if(a.Width!=512||a.Height!=512||b.Size!=a.Size||m.Size!=a.Size)throw new Exception("Unexpected canvas size");
            var protectedRects=new[]{new Rectangle(125,100,188,140),new Rectangle(298,100,137,139),new Rectangle(404,177,81,80)};
            for(int y=0;y<512;y++)for(int x=0;x<512;x++){
                var ca=a.GetPixel(x,y);var cb=b.GetPixel(x,y);bool changed=ca.R!=cb.R||ca.G!=cb.G||ca.B!=cb.B;
                if(m.GetPixel(x,y).R==0){result.outsidePixels++;if(changed)result.changedOutsidePixels++;}
                else{result.selectedPixels++;if(changed)result.changedSelectedPixels++;}
                var cp=p.GetPixel(x,y);bool protectedChanged=cp.R!=cb.R||cp.G!=cb.G||cp.B!=cb.B;
                if(protectedChanged)for(int i=0;i<protectedRects.Length;i++)if(protectedRects[i].Contains(x,y))result.changedProtectedRectangles[i]++;
            }
        }
        return result;
    }
}
'@
$soraResult=[SoraFlatPixelCheck]::Inspect($soraSource,$soraSelection,$soraCandidate,$soraProtectedSource)
$soraPassed=$soraResult.changedOutsidePixels -eq 0 -and $soraResult.changedSelectedPixels -gt 0 -and @($soraResult.changedProtectedRectangles | Where-Object {$_ -ne 0}).Count -eq 0
$soraReport=[ordered]@{attempt=$Attempt;candidate=$Candidate;candidateSha256=$soraCandidateSha;nativeImageSha256=$soraReceipt.files[0].sha256;sourceAndSelectionHashesVerified=$true;canvas=@(512,512);pixels=$soraResult;protectedReference=$soraProtectedSource;protectedRegions='Original carrying grip/arm, head and connected weapon';preservationPassed=$soraPassed;visualArtAndPoseReview='required; preservation does not certify correct anatomy or movement';finalUserApproval='pending';gameplayTested=$false}
$soraReportName=if($Candidate -eq 'candidate_00.png'){'Pixel_Preservation_QA.json'}else{'Final_Preservation_QA.json'}
$soraTarget=Join-Path $soraOut $soraReportName
if(Test-Path -LiteralPath $soraTarget){throw 'Preserve previous QA record'}
$soraReport | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $soraTarget -Encoding UTF8
$soraReport | ConvertTo-Json -Depth 5
if(-not $soraPassed){throw 'Flat-canvas pixel preservation failed; inspect the saved report'}
