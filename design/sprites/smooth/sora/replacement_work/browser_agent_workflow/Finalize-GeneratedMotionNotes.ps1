param([ValidatePattern('^motion_refinement_v[0-9]+$')][string]$Version='motion_refinement_v4')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
if($Version -ne 'motion_refinement_v4'){throw 'These review notes describe version4 only'}
$soraReady=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready'
foreach($soraAnimation in @('run_loop','run_stop')){
    $soraTarget=Join-Path $soraReady "$soraAnimation/direct_generation_retry_v1/$Version/ART_REVIEW.md"
    if(Test-Path -LiteralPath $soraTarget){throw 'Preserve previous review notes'}
    $soraText=Get-Content -LiteralPath (Join-Path $soraReady "$soraAnimation/direct_generation_retry_v1/motion_refinement_v3/ART_REVIEW.md") -Raw
    $soraText=$soraText.Replace('motion_refinement_v3',$Version).Replace('motion studies1/2','motion studies1/2/3')
    $soraLines=$soraText -split "`r?`n",2
    $soraAddition=if($soraAnimation -eq 'run_loop'){'Version4 lowers the forward free hand in poses03-07 so it stays below the carried blade. This removes the unintended appearance of a second weapon grip. Version3 remains preserved; arm timing, anatomy and the full gait are still under review.'}else{'Version4 uses the updated complete loop poses, including the lowered forward free hand in selected loop05. Carry-order selection and the remaining braking/weapon limits below are unchanged.'}
    $soraText=$soraLines[0]+"`n`n"+$soraAddition+"`n"+$soraLines[1]
    [System.IO.File]::WriteAllText($soraTarget,$soraText,[System.Text.UTF8Encoding]::new($false))
}
Write-Output 'Version4 review notes created; earlier notes preserved.'
