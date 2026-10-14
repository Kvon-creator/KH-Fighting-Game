param([ValidatePattern('^attempt_[0-9]{2,}$')][string]$Attempt='attempt_02')
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
$soraCandidate=Join-Path $soraOut 'candidate_00.png'
foreach($soraCheck in @(@($soraSource,$soraReceipt.referenceSha256),@($soraSelection,$soraReceipt.maskSha256),@($soraCandidate,$soraReceipt.files[0].sha256),@((SoraPath $soraReceipt.sourceSheet),$soraReceipt.sourceSheetSha256))){if((Get-FileHash -LiteralPath $soraCheck[0] -Algorithm SHA256).Hash.ToLowerInvariant() -ne $soraCheck[1]){throw 'Source/selection/native image hash changed'}}
Add-Type -AssemblyName System.Drawing
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System;
using System.Drawing;
public class SoraFlatPixels {
    public int selectedPixels, changedSelectedPixels, outsidePixels, changedOutsidePixels;
    public int[] changedProtectedRectangles=new int[3];
}
public static class SoraFlatPixelCheck {
    public static SoraFlatPixels Inspect(string source,string selection,string candidate){
        var result=new SoraFlatPixels();
        using(var a=new Bitmap(source))using(var m=new Bitmap(selection))using(var b=new Bitmap(candidate)){
            if(a.Width!=512||a.Height!=512||b.Size!=a.Size||m.Size!=a.Size)throw new Exception("Unexpected canvas size");
            var protectedRects=new[]{new Rectangle(125,100,188,140),new Rectangle(298,100,137,139),new Rectangle(395,177,90,86)};
            for(int y=0;y<512;y++)for(int x=0;x<512;x++){
                var ca=a.GetPixel(x,y);var cb=b.GetPixel(x,y);bool changed=ca.R!=cb.R||ca.G!=cb.G||ca.B!=cb.B;
                if(m.GetPixel(x,y).R==0){result.outsidePixels++;if(changed)result.changedOutsidePixels++;}
                else{result.selectedPixels++;if(changed)result.changedSelectedPixels++;}
                if(changed)for(int i=0;i<protectedRects.Length;i++)if(protectedRects[i].Contains(x,y))result.changedProtectedRectangles[i]++;
            }
        }
        return result;
    }
}
'@
$soraResult=[SoraFlatPixelCheck]::Inspect($soraSource,$soraSelection,$soraCandidate)
$soraPassed=$soraResult.changedOutsidePixels -eq 0 -and $soraResult.changedSelectedPixels -gt 0 -and @($soraResult.changedProtectedRectangles | Where-Object {$_ -ne 0}).Count -eq 0
$soraReport=[ordered]@{attempt=$Attempt;nativeImageSha256=$soraReceipt.files[0].sha256;sourceAndSelectionHashesVerified=$true;canvas=@(512,512);pixels=$soraResult;protectedRegions='Original carrying grip/arm, head and connected weapon';preservationPassed=$soraPassed;visualArtAndPoseReview='required; preservation does not certify correct anatomy or movement';finalUserApproval='pending';gameplayTested=$false}
$soraTarget=Join-Path $soraOut 'Pixel_Preservation_QA.json'
if(Test-Path -LiteralPath $soraTarget){throw 'Preserve previous QA record'}
$soraReport | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $soraTarget -Encoding UTF8
$soraReport | ConvertTo-Json -Depth 5
if(-not $soraPassed){throw 'Flat-canvas pixel preservation failed; inspect the saved report'}
