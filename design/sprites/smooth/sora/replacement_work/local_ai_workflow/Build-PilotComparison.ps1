param([ValidatePattern('^attempt_[0-9]{2,}$')][string]$Attempt='attempt_01',[ValidatePattern('^(candidate_[0-9]{2}|final_pose_v[0-9]+)\.png$')][string]$Candidate='candidate_00.png',[switch]$OriginalReference)
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraOut=Join-Path $soraRoot "design/sprites/smooth/sora/replacement_work/ready/run_loop/comfyui_trial/$Attempt"
$soraReceipt=Get-Content -LiteralPath (Join-Path $soraOut 'receipt.json') -Raw | ConvertFrom-Json
if($soraReceipt.status -ne 'generated_pending_review' -or $soraReceipt.files.Count -ne 1){throw 'Collect one real whole-pose candidate before comparison'}
$soraReference=[System.IO.Path]::GetFullPath((Join-Path $soraRoot $soraReceipt.reference))
if(-not $soraReference.StartsWith($soraRoot+'\',[System.StringComparison]::OrdinalIgnoreCase)){throw 'Reference escaped workspace'}
$soraCandidate=Join-Path $soraOut $Candidate;$soraExpectedCandidate=$soraReceipt.files[0].sha256;$soraExpectedReference=$soraReceipt.referenceSha256
if($Candidate -ne 'candidate_00.png'){
    $soraRefinement=Get-Content -LiteralPath (Join-Path $soraOut 'refinement_manifest.json') -Raw | ConvertFrom-Json
    if($soraRefinement.file -ne $Candidate -or $soraRefinement.sourceNativeSha256 -ne $soraReceipt.files[0].sha256){throw 'Refinement provenance differs'}
    $soraExpectedCandidate=$soraRefinement.sha256
}
if($OriginalReference){$soraReference=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready/run_loop/comfyui_trial/reference_v1/whole_pose_00_white.png';$soraExpectedReference='a3681849fa6b2a235fd36622866057191f0d073d39ea9cff8b7e30764f6d9022'}
if((Get-FileHash -LiteralPath $soraCandidate -Algorithm SHA256).Hash.ToLowerInvariant() -ne $soraExpectedCandidate){throw 'Candidate hash differs'}
if((Get-FileHash -LiteralPath $soraReference -Algorithm SHA256).Hash.ToLowerInvariant() -ne $soraExpectedReference){throw 'Reference hash differs'}
$soraBoardName=if($Candidate -eq 'candidate_00.png'){'Original_Candidate_Comparison.png'}else{'Original_Final_Comparison.png'}
$soraTarget=Join-Path $soraOut $soraBoardName
if(Test-Path -LiteralPath $soraTarget){throw 'Preserve comparison'}
Add-Type -AssemblyName System.Drawing
$soraOriginal=[System.Drawing.Bitmap]::new($soraReference);$soraNew=[System.Drawing.Bitmap]::new($soraCandidate)
if($soraOriginal.Size.Width -ne 512 -or $soraOriginal.Size.Height -ne 512 -or $soraNew.Width -ne 512 -or $soraNew.Height -ne 512){throw 'Unexpected complete canvas sizes'}
$soraBoard=[System.Drawing.Bitmap]::new(1024,570,[System.Drawing.Imaging.PixelFormat]::Format24bppRgb);$soraGraphics=[System.Drawing.Graphics]::FromImage($soraBoard);$soraGraphics.Clear([System.Drawing.Color]::White)
$soraFont=[System.Drawing.Font]::new('Arial',13);$soraSmall=[System.Drawing.Font]::new('Arial',10)
$soraGraphics.DrawImageUnscaled($soraOriginal,0,30);$soraGraphics.DrawImageUnscaled($soraNew,512,30)
$soraGraphics.DrawString('Original whole pose (reference)',$soraFont,[System.Drawing.Brushes]::Black,12,6)
$soraCandidateLabel=if($Candidate -eq 'candidate_00.png'){'Local AI candidate (pending review)'}else{'Refined flat pilot (user approval pending)'}
$soraGraphics.DrawString($soraCandidateLabel,$soraFont,[System.Drawing.Brushes]::Black,524,6)
$soraGraphics.DrawString('One complete backward-arm pilot; original legs held. Full running cycle and final artwork approval pending.',$soraSmall,[System.Drawing.Brushes]::Black,12,546)
$soraBoard.Save($soraTarget,[System.Drawing.Imaging.ImageFormat]::Png)
$soraGraphics.Dispose();$soraBoard.Dispose();$soraOriginal.Dispose();$soraNew.Dispose();$soraFont.Dispose();$soraSmall.Dispose()
Write-Output 'Native-size whole-canvas comparison saved; visual review remains required.'
