$ErrorActionPreference='Stop'
$workRoot=[IO.Path]::GetFullPath($PSScriptRoot)
$soraRoot=Split-Path -Parent $workRoot
$readyRoot=Join-Path $workRoot 'ready'
$allowedRoot=$workRoot+[IO.Path]::DirectorySeparatorChar

function Flow-Folder([string]$Name) {
    switch -Regex ($Name) {
        '^(sora_stand_idle_|stand_idle_source|sora_smooth_stand_guard|pose_0)' {return 'standing_idle'}
        '^(sora_crouch_down_|sora_duck_down_sheet)' {return 'crouch_cycle/duck_down'}
        '^sora_crouch_up_' {return 'crouch_cycle/stand_up'}
        '^(sora_crouch_idle_|crouch_idle_source|sora_smooth_crouch_guard|pose_7)' {return 'crouch_cycle/crouching_idle'}
        '^(sora_crouch_(sheet|manifest|full_cycle)|sora_duck_full_cycle|duck_sheet_(draft|source))' {return 'crouch_cycle'}
        '^(sora_shimmy_forward_|shimmy_forward_source)' {return 'shimmy_forward'}
        '^(sora_shimmy_backward_|shimmy_backward_draft)' {return 'shimmy_backward'}
        '^(sora_smooth_attack_windup|windup_source|windup_packaged)' {return 'attack_windup'}
        '^(Animation_Previews\.html|Shimmy_Previews\.html|approved_preview_manifest\.json|sora_shimmy_manifest\.json|packaging_metrics\.json|Shimmy_Generation_Prompts\.md|PRODUCTION_STATUS\.md)$' {return '.'}
    }
    return $null
}

# Keep shared viewer templates available for rebuilding future batches.
$templates=Join-Path $workRoot 'templates'
New-Item -ItemType Directory -Path $templates -Force|Out-Null
$templatePath=Join-Path $templates 'Animation_Previews.html'
if(!(Test-Path -LiteralPath $templatePath)) {
    Copy-Item -LiteralPath (Join-Path $readyRoot 'Animation_Previews.html') -Destination $templatePath
}

$files=@(Get-ChildItem -LiteralPath $readyRoot -File)+@(Get-ChildItem -LiteralPath $workRoot -File)+@(Get-ChildItem -LiteralPath $soraRoot -File)
$targets=@{}
$checks=@{}
$moved=0
foreach($file in $files) {
    $folder=Flow-Folder $file.Name
    if($null -eq $folder){continue}
    $targetFolder=[IO.Path]::GetFullPath((Join-Path $readyRoot $folder))
    $target=[IO.Path]::GetFullPath((Join-Path $targetFolder $file.Name))
    if(!$target.StartsWith($allowedRoot,[StringComparison]::OrdinalIgnoreCase)){throw "Destination outside replacement_work: $target"}
    if(!$file.FullName.StartsWith($soraRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw "Source outside Sora directory: $($file.FullName)"}
    New-Item -ItemType Directory -Path $targetFolder -Force|Out-Null
    $targets[$file.Name]=$target
    if($file.Extension -in @('.png','.gif')){$checks[$target]=(Get-FileHash -LiteralPath $file.FullName).Hash}
    if($file.FullName -eq $target){continue}
    if(Test-Path -LiteralPath $target) {
        $sourceHash=(Get-FileHash -LiteralPath $file.FullName).Hash
        $targetHash=(Get-FileHash -LiteralPath $target).Hash
        if($sourceHash -ne $targetHash){throw "Conflicting copies; preserved both for review: $($file.Name)"}
    }
    Move-Item -LiteralPath $file.FullName -Destination $target -Force
    $moved++
}
foreach($file in Get-ChildItem -LiteralPath $readyRoot -File -Recurse) {
    if($file.Name -ne 'Preview.html'){$targets[$file.Name]=$file.FullName}
}

function Relative-Path([string]$Owner,[string]$Target) {
    $from=New-Object Uri($Owner+[IO.Path]::DirectorySeparatorChar)
    $to=New-Object Uri($Target)
    return [Uri]::UnescapeDataString($from.MakeRelativeUri($to).ToString())
}
function Update-References($Value,[string]$Owner) {
    if($Value -is [string]) {
        if($Value -match '\.(png|gif|json|html)$') {
            $name=[IO.Path]::GetFileName($Value.Replace('/','\'))
            if($targets.ContainsKey($name)){return (Relative-Path $Owner $targets[$name])}
        }
        return $Value
    }
    if($Value -is [array]) {
        $items=@()
        foreach($item in $Value){$items+=,(Update-References $item $Owner)}
        return ,$items
    }
    if($Value -is [pscustomobject]) {
        foreach($property in $Value.PSObject.Properties){$property.Value=Update-References $property.Value $Owner}
        return $Value
    }
    return $Value
}
foreach($file in Get-ChildItem -LiteralPath $readyRoot -File -Recurse -Filter '*.json') {
    $data=Get-Content -Raw -Encoding UTF8 -LiteralPath $file.FullName|ConvertFrom-Json
    $data=Update-References $data $file.DirectoryName
    $data|ConvertTo-Json -Depth 20|Set-Content -LiteralPath $file.FullName -Encoding UTF8
}

# Make both combined review pages resolve their newly nested frame paths.
$overview=Join-Path $readyRoot 'Animation_Previews.html'
$html=Get-Content -Raw -Encoding UTF8 -LiteralPath $overview
$html=$html.Replace("urls('sora_stand_idle',10)","urls('standing_idle/sora_stand_idle',10)")
$html=$html.Replace("urls('sora_crouch_down',8)","urls('crouch_cycle/duck_down/sora_crouch_down',8)")
Set-Content -LiteralPath $overview -Value $html -Encoding UTF8
$shimmyOverview=Join-Path $readyRoot 'Shimmy_Previews.html'
$shimmyHtml=Get-Content -Raw -Encoding UTF8 -LiteralPath $shimmyOverview
$shimmyHtml=$shimmyHtml.Replace("urls('sora_shimmy_forward',10)","urls('shimmy_forward/sora_shimmy_forward',10)")
$shimmyHtml=$shimmyHtml.Replace("urls('sora_shimmy_backward',10)","urls('shimmy_backward/sora_shimmy_backward',10)")
Set-Content -LiteralPath $shimmyOverview -Value $shimmyHtml -Encoding UTF8

# Each individual flow gets its own independent preview page.
$previewSpecs=@(
    @{folder='standing_idle';html=$html;id='stand'},
    @{folder='crouch_cycle';html=$html;id='duck'},
    @{folder='shimmy_forward';html=$shimmyHtml;id='stand'},
    @{folder='shimmy_backward';html=$shimmyHtml;id='duck'}
)
foreach($spec in $previewSpecs) {
    $page=$spec.html
    $cards=[regex]::Matches($page,'<article>.*?</article>',[Text.RegularExpressions.RegexOptions]::Singleline)
    $stateMatch=[regex]::Match($page,"const states=\[(.*?)\];",[Text.RegularExpressions.RegexOptions]::Singleline)
    $states=[regex]::Matches($stateMatch.Groups[1].Value,"\{id:'(stand|duck)'.*?\}")
    if($cards.Count -ne 2 -or $states.Count -ne 2){throw 'Unexpected viewer structure'}
    $selection=0
    if($spec.id -eq 'duck'){$selection=1}
    $page=[regex]::Replace($page,'<section>.*?</section>',('<section>'+$cards[$selection].Value+'</section>'),[Text.RegularExpressions.RegexOptions]::Singleline)
    $page=$page.Replace($stateMatch.Value,('const states=['+$states[$selection].Value+'];'))
    $page=$page.Replace($spec.folder+'/','')
    $page=$page.Replace('grid-template-columns:repeat(2,minmax(0,1fr))','grid-template-columns:minmax(0,512px)')
    Set-Content -LiteralPath (Join-Path (Join-Path $readyRoot $spec.folder) 'Preview.html') -Value $page -Encoding UTF8
}

# Extract a local manifest for each crouch subflow and shimmy direction.
$crouchManifest=Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $readyRoot 'crouch_cycle/sora_crouch_manifest.json')|ConvertFrom-Json
$shimmyManifest=Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $readyRoot 'sora_shimmy_manifest.json')|ConvertFrom-Json
$manifestSpecs=@(
    @{folder='crouch_cycle/duck_down';name='sora_crouch_down_manifest.json';animation=$crouchManifest.animations.duck_down},
    @{folder='crouch_cycle/crouching_idle';name='sora_crouch_idle_manifest.json';animation=$crouchManifest.animations.crouching_idle},
    @{folder='crouch_cycle/stand_up';name='sora_crouch_up_manifest.json';animation=$crouchManifest.animations.stand_up},
    @{folder='shimmy_forward';name='sora_shimmy_forward_manifest.json';animation=$shimmyManifest.animations.forward},
    @{folder='shimmy_backward';name='sora_shimmy_backward_manifest.json';animation=$shimmyManifest.animations.backward}
)
foreach($spec in $manifestSpecs) {
    $owner=Join-Path $readyRoot $spec.folder
    $local=[pscustomobject]@{character='Sora';canvas_size=@(512,512);ground_baseline_y=470;animation_name=$spec.folder;animation=$spec.animation;status='art only; not integrated in Godot'}
    $local=Update-References $local $owner
    $local|ConvertTo-Json -Depth 20|Set-Content -LiteralPath (Join-Path $owner $spec.name) -Encoding UTF8
}
foreach($entry in $checks.GetEnumerator()) {
    if((Get-FileHash -LiteralPath $entry.Key).Hash -ne $entry.Value){throw "Image bytes changed: $($entry.Key)"}
}
Write-Output "Moved/consolidated $moved files. Verified $($checks.Count) unique image files unchanged."
Get-ChildItem -LiteralPath $readyRoot -Directory|ForEach-Object {[pscustomobject]@{Flow=$_.Name;Files=(Get-ChildItem -LiteralPath $_.FullName -Recurse -File|Measure-Object).Count}}
