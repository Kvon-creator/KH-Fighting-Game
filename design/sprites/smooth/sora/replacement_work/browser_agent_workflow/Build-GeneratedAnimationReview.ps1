param([ValidatePattern('^direct_generation_retry_v[0-9]+$')][string]$Version='direct_generation_retry_v1')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraReady=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready'
$soraPlans=[ordered]@{}
foreach($soraAnimation in @('run_loop','run_stop')){
    $soraFolder=Join-Path $soraReady "$soraAnimation/$Version"
    if(Test-Path -LiteralPath (Join-Path $soraFolder 'whole_frame_review_v1')){throw 'Preserve existing whole-frame review'}
    $soraRelative="design/sprites/smooth/sora/replacement_work/ready/$soraAnimation/$Version/sora_${soraAnimation}_generated_original.png"
    $soraRaw=& python (Join-Path $PSScriptRoot 'inspect_generated_retry.py') $soraRelative
    if($LASTEXITCODE -ne 0){throw 'Read-only native-sheet inspection failed'}
    $soraPlan=$soraRaw | ConvertFrom-Json
    if($soraPlan.completeFigureFrames.Count -ne 12){throw 'Twelve complete figures not established'}
    if($soraPlan.transparentPixelCount -eq 0){throw 'Native alpha is missing'}
    if(@($soraPlan.completeFigureFrames | Where-Object edgeClippingRisk).Count -gt 0){throw 'Inspect native edge clipping before export'}
    $soraRaw | Set-Content -LiteralPath (Join-Path $soraFolder 'Native_Inspection.json') -Encoding UTF8
    $soraPlans[$soraAnimation]=$soraPlan
}
Add-Type -AssemblyName System.Drawing
Add-Type -Path (Join-Path $PSScriptRoot '../AnimationPackaging.cs') -ReferencedAssemblies System.Drawing
$soraAll=[ordered]@{}
foreach($soraAnimation in @('run_loop','run_stop')){
    $soraFolder=Join-Path $soraReady "$soraAnimation/$Version"
    $soraOut=Join-Path $soraFolder 'whole_frame_review_v1'
    New-Item -ItemType Directory -Path $soraOut,(Join-Path $soraOut 'frames_128') | Out-Null
    $soraPlan=$soraPlans[$soraAnimation]
    $soraSource=[System.Drawing.Bitmap]::new($soraPlan.path)
    # Uniform export scale follows the original accepted run-start extraction.
    $soraScale=1.1792207792207792
    $soraRight=($soraPlan.completeFigureFrames | ForEach-Object {($_.bounds[2]-$_.nativeEyeX)*$soraScale} | Measure-Object -Maximum).Maximum
    $soraLeft=($soraPlan.completeFigureFrames | ForEach-Object {($_.nativeEyeX-$_.bounds[0])*$soraScale} | Measure-Object -Maximum).Maximum
    $soraAnchor=[Math]::Min(386,500-$soraRight)
    if($soraAnchor-$soraLeft -lt 12){throw 'Whole-figure export would clip; inspect instead of changing individual scale'}
    $soraBoard=[System.Drawing.Bitmap]::new(1024,840)
    $soraBoardG=[System.Drawing.Graphics]::FromImage($soraBoard);$soraBoardG.Clear([System.Drawing.Color]::White)
    $soraBoardG.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $soraSheet=[System.Drawing.Bitmap]::new(2048,1536,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $soraSheetG=[System.Drawing.Graphics]::FromImage($soraSheet)
    $soraFont=[System.Drawing.Font]::new('Arial',10)
    $soraRecords=[System.Collections.Generic.List[object]]::new()
    $soraLarge=[System.Collections.Generic.List[System.Drawing.Bitmap]]::new()
    $soraSmall=[System.Collections.Generic.List[System.Drawing.Bitmap]]::new()
    foreach($soraFrame in $soraPlan.completeFigureFrames){
        $soraIndex=[int]$soraFrame.index;$soraB=$soraFrame.bounds
        $soraWidth=($soraB[2]-$soraB[0])*$soraScale;$soraHeight=($soraB[3]-$soraB[1])*$soraScale
        $soraClearance=0
        # These offsets illustrate the requested run timing; generated limb roles
        # and actual contacts are not yet certified as a coherent gait.
        if($soraAnimation -eq 'run_loop'){
            if($soraIndex -in @(4,10)){$soraClearance=14}
            elseif($soraIndex -in @(5,11)){$soraClearance=2}
        }
        $soraX=$soraAnchor-($soraFrame.nativeEyeX-$soraB[0])*$soraScale
        $soraY=470-$soraClearance-$soraHeight
        if($soraY -lt 12){throw 'Whole-figure export would clip above canvas'}
        $soraImage=[System.Drawing.Bitmap]::new(512,512,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
        $soraG=[System.Drawing.Graphics]::FromImage($soraImage)
        $soraG.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $soraG.PixelOffsetMode=[System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
        $soraDestination=[System.Drawing.RectangleF]::new($soraX,$soraY,$soraWidth,$soraHeight)
        $soraSourceBounds=[System.Drawing.RectangleF]::new($soraB[0],$soraB[1],$soraB[2]-$soraB[0],$soraB[3]-$soraB[1])
        $soraG.DrawImage($soraSource,$soraDestination,$soraSourceBounds,[System.Drawing.GraphicsUnit]::Pixel)
        $soraG.Dispose()
        $soraFile=('sora_{0}_{1:00}.png' -f $soraAnimation,$soraIndex)
        $soraTarget=Join-Path $soraOut $soraFile
        $soraImage.Save($soraTarget,[System.Drawing.Imaging.ImageFormat]::Png)
        $soraCol=$soraIndex%4;$soraRow=[Math]::Floor($soraIndex/4)
        $soraSheetG.DrawImageUnscaled($soraImage,$soraCol*512,$soraRow*512)
        $soraBoardG.DrawImage($soraImage,[int]($soraCol*256),[int]($soraRow*280),256,256)
        $soraBoardG.DrawString(('Generated pose{0:00}' -f $soraIndex),$soraFont,[System.Drawing.Brushes]::Black,$soraCol*256+8,$soraRow*280+257)
        $soraGame=[System.Drawing.Bitmap]::new(128,128,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
        $soraG=[System.Drawing.Graphics]::FromImage($soraGame);$soraG.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $soraG.DrawImage($soraImage,0,0,128,128);$soraG.Dispose()
        $soraGame.Save((Join-Path $soraOut "frames_128/$soraFile"),[System.Drawing.Imaging.ImageFormat]::Png)
        foreach($soraSize in @(512,128)){
            $soraFlat=[System.Drawing.Bitmap]::new($soraSize,$soraSize)
            $soraG=[System.Drawing.Graphics]::FromImage($soraFlat);$soraG.Clear([System.Drawing.Color]::White)
            $soraG.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
            $soraG.DrawImage($soraImage,0,0,$soraSize,$soraSize);$soraG.Dispose()
            if($soraSize -eq 512){$soraLarge.Add($soraFlat)}else{$soraSmall.Add($soraFlat)}
        }
        $soraDuration=if($soraAnimation -eq 'run_loop'){80}else{100}
        $soraRecords.Add([pscustomobject][ordered]@{index=$soraIndex;file=$soraFile;durationMs=$soraDuration;nativeBounds=$soraB;uniformScale=$soraScale;placement=@($soraX,$soraY);blueFaceAnchorPixels=$soraFrame.blueEyePixels;provisionalClearance=$soraClearance;sha256=(Get-FileHash -LiteralPath $soraTarget -Algorithm SHA256).Hash.ToLowerInvariant()})
        $soraGame.Dispose();$soraImage.Dispose()
    }
    $soraBoard.Save((Join-Path $soraOut 'Contact_Sheet.png'),[System.Drawing.Imaging.ImageFormat]::Png)
    $soraSheet.Save((Join-Path $soraOut 'Sprite_Sheet_512.png'),[System.Drawing.Imaging.ImageFormat]::Png)
    foreach($soraSize in @(512,128)){
        $soraFrames=if($soraSize -eq 512){$soraLarge.ToArray()}else{$soraSmall.ToArray()}
        $soraSuffix=if($soraAnimation -eq 'run_loop'){'Loop'}else{'Once'}
        $soraGif=Join-Path $soraOut "Preview_${soraSize}_${soraSuffix}.gif"
        [AnimationPackaging]::Gif($soraGif,$soraFrames,[int[]]@($soraRecords | ForEach-Object durationMs))
        if($soraAnimation -eq 'run_stop'){
            $soraBytes=[System.IO.File]::ReadAllBytes($soraGif)
            if([System.Text.Encoding]::ASCII.GetString($soraBytes,16,11) -ne 'NETSCAPE2.0'){throw 'Unexpected GIF header'}
            [System.IO.File]::WriteAllBytes($soraGif,[byte[]]($soraBytes[0..12]+$soraBytes[32..($soraBytes.Length-1)]))
        }
        $soraCheck=[System.Drawing.Image]::FromFile($soraGif)
        if($soraCheck.GetFrameCount([System.Drawing.Imaging.FrameDimension]::Time) -ne 12){throw 'Wrong GIF count'}
        $soraCheck.Dispose()
    }
    $soraManifest=[ordered]@{status='AI whole-frame generation review; not approved motion or game integration';animation=$soraAnimation;frameCount=12;canvas=@(512,512);gameExport=@(128,128);loop=($soraAnimation -eq 'run_loop');source=$soraPlan.path;sourceSha256=$soraPlan.fileSha256;method='Complete generated figures extracted by alpha connectivity; one uniform resolution scale, temporary whole-figure selections, no body/weapon layers or new pose drawings';durationMs=($soraRecords | Measure-Object durationMs -Sum).Sum;faceAnchorIsEstimate=$true;floorOffsetsAreProvisional=$true;frames=$soraRecords.ToArray();limitations=@('Limb-role alternation, free-arm swing, source-to-loop and wrap continuity need visual correction.','Stop begins with early lowered blade; shoulder-carry order edit was refused.','Loop/stop entry drawings differ; they are not a seamless shared entry.','Projected weapon geometry and final idle alignment remain unverified.','No Godot or actual-browser playback test.')}
    $soraManifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $soraOut 'manifest.json') -Encoding UTF8
    $soraAll[$soraAnimation]=$soraManifest
    $soraSource.Dispose();$soraBoardG.Dispose();$soraBoard.Dispose();$soraSheetG.Dispose();$soraSheet.Dispose();$soraFont.Dispose()
    foreach($soraBitmap in @($soraLarge.ToArray())+@($soraSmall.ToArray())){$soraBitmap.Dispose()}
    if((Get-FileHash -LiteralPath $soraPlan.path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $soraPlan.fileSha256){throw 'Native generated source changed'}
}
$soraLoop=ConvertTo-Json -InputObject @($soraAll.run_loop.frames | ForEach-Object {@{file=$_.file;durationMs=$_.durationMs}}) -Compress
$soraStop=ConvertTo-Json -InputObject @($soraAll.run_stop.frames | ForEach-Object {@{file="../../../run_stop/$Version/whole_frame_review_v1/"+$_.file;durationMs=$_.durationMs}}) -Compress
$soraHtml=@'
<!doctype html><html lang="en"><meta charset="utf-8"><title>Sora generated animation trial</title>
<style>body{font:16px system-ui;background:#242b36;color:#f2f4f6;margin:24px}button,select{padding:9px;margin:3px;border:0;border-radius:5px}canvas{background:#fff;border:1px solid #606873}#views{display:flex;align-items:end;gap:20px;flex-wrap:wrap}#large{width:min(512px,85vw);height:auto}input{width:510px;max-width:90vw}a{color:#a8d5ff}</style>
<h1>Sora: generated run and stop trial</h1><p>New complete-frame artwork. Motion remains under review: run alternation and stop carry order need correction. The two entries differ.</p>
<p><a href="../sora_run_loop_generated_original_White_Review.png">Native run sheet on white</a> | <a href="../../../run_stop/__VERSION__/sora_run_stop_generated_original_White_Review.png">Native stop sheet on white</a></p>
<select id="kind"><option value="run">Run loop:12 poses</option><option value="stop">Run stop:12 poses</option></select><button id="play">Play</button><button id="pause">Pause</button><button id="slow">Slow x3</button>
<div id="views"><canvas id="large" width="512" height="512"></canvas><canvas id="small" width="128" height="128"></canvas></div><p id="label"></p><input id="scrub" type="range" min="0" max="11" value="0">
<script>
const run=__RUN__,stop=__STOP__;const q=s=>document.querySelector(s),images=new Map();let timer=null,index=0,slow=false,playing=false;const sequence=()=>q('#kind').value==='stop'?stop:run;
function draw(){const f=sequence()[index];let img=images.get(f.file);if(!img){img=new Image();img.src=f.file;images.set(f.file,img);img.onload=draw;}for(const id of ['#large','#small']){const c=q(id),g=c.getContext('2d');g.fillStyle='#fff';g.fillRect(0,0,c.width,c.height);if(img.complete&&img.naturalWidth)g.drawImage(img,0,0,c.width,c.height);}q('#label').textContent=`Generated pose ${index+1}/12 — chronology and contacts remain provisional`;q('#scrub').value=index;}
function pause(){playing=false;if(timer)clearTimeout(timer);timer=null;}function tick(){const a=sequence();if(index===a.length-1){if(q('#kind').value==='stop'){pause();return;}index=0;}else index++;draw();timer=setTimeout(tick,a[index].durationMs*(slow?3:1));}
q('#play').onclick=()=>{pause();playing=true;if(index===sequence().length-1)index=0;draw();timer=setTimeout(tick,sequence()[index].durationMs*(slow?3:1));};q('#pause').onclick=pause;q('#kind').onchange=()=>{pause();index=0;draw();};q('#scrub').oninput=()=>{pause();index=+q('#scrub').value;draw();};q('#slow').onclick=()=>{slow=!slow;q('#slow').textContent=slow?'Normal speed':'Slow x3';if(playing)q('#play').onclick();};draw();
</script></html>
'@
$soraHtml=$soraHtml.Replace('__RUN__',$soraLoop).Replace('__STOP__',$soraStop).Replace('__VERSION__',$Version)
[System.IO.File]::WriteAllText((Join-Path $soraReady "run_loop/$Version/whole_frame_review_v1/Review.html"),$soraHtml.TrimEnd()+[Environment]::NewLine,[System.Text.UTF8Encoding]::new($false))
Write-Output 'Both12-pose complete-frame review packages created. Native sources unchanged; motion remains unapproved.'
