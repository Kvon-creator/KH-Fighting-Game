param([ValidateSet('attempt_04','attempt_05')][string]$Attempt,[ValidatePattern('^final_pose_v[0-9]+$')][string]$Version='final_pose_v2')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraTrial=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready/run_loop/comfyui_trial'
$soraOut=Join-Path $soraTrial $Attempt
$soraReceipt=Get-Content -LiteralPath (Join-Path $soraOut 'receipt.json') -Raw | ConvertFrom-Json
if($soraReceipt.status -ne 'generated_pending_review' -or $soraReceipt.files.Count -ne 1){throw 'Collect native pose first'}
$soraIndex=if($Attempt -eq 'attempt_04'){1}else{2};$soraBob=if($soraIndex -eq 1){3}else{1}
$soraNative=Join-Path $soraOut 'candidate_00.png'
$soraGuide=[System.IO.Path]::GetFullPath((Join-Path $soraRoot $soraReceipt.reference))
$soraMask=[System.IO.Path]::GetFullPath((Join-Path $soraRoot $soraReceipt.mask))
foreach($soraPath in @($soraGuide,$soraMask)){if(-not $soraPath.StartsWith($soraRoot+'\',[System.StringComparison]::OrdinalIgnoreCase)){throw 'Reference escaped workspace'}}
foreach($soraPair in @(@($soraNative,$soraReceipt.files[0].sha256),@($soraGuide,$soraReceipt.referenceSha256),@($soraMask,$soraReceipt.maskSha256))){if((Get-FileHash -LiteralPath $soraPair[0] -Algorithm SHA256).Hash.ToLowerInvariant() -ne $soraPair[1]){throw 'Native/input/selection hash differs'}}
$soraTarget=Join-Path $soraOut "$Version.png"
if(Test-Path -LiteralPath $soraTarget){throw 'Preserve existing refinement'}
Add-Type -AssemblyName System.Drawing
Add-Type -Path (Join-Path $PSScriptRoot 'AdjacentRunPainting.cs') -ReferencedAssemblies System.Drawing
[AdjacentRunGuide]::Finish($soraNative,$soraGuide,$soraMask,$soraTarget,$soraIndex,$soraBob)
$soraManifest=if($Version -eq 'final_pose_v1'){'refinement_manifest.json'}else{"${Version}_manifest.json"}
if(Test-Path -LiteralPath (Join-Path $soraOut $soraManifest)){throw 'Preserve existing refinement manifest'}
[ordered]@{file="$Version.png";sha256=(Get-FileHash -LiteralPath $soraTarget -Algorithm SHA256).Hash.ToLowerInvariant();sourceNativeSha256=$soraReceipt.files[0].sha256;guide=$soraReceipt.reference;guideSha256=$soraReceipt.referenceSha256;maskSha256=$soraReceipt.maskSha256;method='Whole-canvas flat finish: correct expanded sleeve/cuff, indistinct fist and chest-panel drift from complete guide; directly repaint articulated arm and seams; retain model waist blending and source protection';componentProductionLayers=$false;bodyShiftY=$soraBob;finalUserApproval='approved treatment, new individual pose not separately reviewed'} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $soraOut $soraManifest) -Encoding UTF8
Write-Output "$Attempt flat-finished pose saved. Native output preserved."
