param([ValidatePattern('^flat_cycle_v[0-9]+$')][string]$LoopVersion='flat_cycle_v2',[ValidatePattern('^flat_stop_v[0-9]+$')][string]$StopVersion='flat_stop_v2')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraReady=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready'
$soraLoopDir=Join-Path $soraReady "run_loop/$LoopVersion"
$soraStopDir=Join-Path $soraReady "run_stop/$StopVersion"
foreach($soraDir in @($soraLoopDir,$soraStopDir)){if(Test-Path -LiteralPath (Join-Path $soraDir 'Contact_Sheet.png')){throw "Review already exists: $soraDir"}}
Add-Type -AssemblyName System.Drawing
Add-Type -Path (Join-Path $PSScriptRoot '../AnimationPackaging.cs') -ReferencedAssemblies System.Drawing
$soraFont=[System.Drawing.Font]::new('Arial',10)
$soraAll=[ordered]@{}
foreach($soraDir in @($soraLoopDir,$soraStopDir)){
    $soraManifest=Get-Content -LiteralPath (Join-Path $soraDir 'manifest.json') -Raw | ConvertFrom-Json
    $soraAll[$soraManifest.animation]=$soraManifest
    $soraBoard=[System.Drawing.Bitmap]::new(1024,1120)
    $soraBoardG=[System.Drawing.Graphics]::FromImage($soraBoard);$soraBoardG.Clear([System.Drawing.Color]::White)
    $soraSheet=[System.Drawing.Bitmap]::new(2048,2048,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $soraSheetG=[System.Drawing.Graphics]::FromImage($soraSheet)
    $soraGameSheet=[System.Drawing.Bitmap]::new(512,512,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $soraGameG=[System.Drawing.Graphics]::FromImage($soraGameSheet)
    foreach($soraG in @($soraBoardG,$soraGameG)){$soraG.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic}
    $soraLargeGif=[System.Collections.Generic.List[System.Drawing.Bitmap]]::new()
    $soraSmallGif=[System.Collections.Generic.List[System.Drawing.Bitmap]]::new()
    New-Item -ItemType Directory -Path (Join-Path $soraDir 'frames_128') | Out-Null
    foreach($soraFrame in $soraManifest.frames){
        $soraInput=Join-Path $soraDir $soraFrame.file
        if((Get-FileHash -LiteralPath $soraInput -Algorithm SHA256).Hash.ToLowerInvariant() -ne $soraFrame.sha256){throw 'Input changed'}
        $soraImage=[System.Drawing.Bitmap]::new($soraInput)
        $soraCol=$soraFrame.index%4;$soraRow=[Math]::Floor($soraFrame.index/4)
        $soraSheetG.DrawImageUnscaled($soraImage,$soraCol*512,$soraRow*512)
        $soraGameG.DrawImage($soraImage,[int]($soraCol*128),[int]($soraRow*128),128,128)
        $soraBoardG.DrawImage($soraImage,[int]($soraCol*256),[int]($soraRow*280),256,256)
        $soraBoardG.DrawString(('{0:00}: {1}' -f $soraFrame.index,$soraFrame.phase),$soraFont,[System.Drawing.Brushes]::Black,$soraCol*256+8,$soraRow*280+257)
        foreach($soraSize in @(512,128)){
            $soraFlat=[System.Drawing.Bitmap]::new($soraSize,$soraSize);$soraG=[System.Drawing.Graphics]::FromImage($soraFlat)
            $soraG.Clear([System.Drawing.Color]::White);$soraG.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
            $soraG.DrawImage($soraImage,0,0,$soraSize,$soraSize);$soraG.Dispose()
            if($soraSize -eq 512){$soraLargeGif.Add($soraFlat)}else{$soraSmallGif.Add($soraFlat)}
        }
        $soraGame=[System.Drawing.Bitmap]::new(128,128,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
        $soraG=[System.Drawing.Graphics]::FromImage($soraGame);$soraG.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $soraG.DrawImage($soraImage,0,0,128,128);$soraG.Dispose();$soraGame.Save((Join-Path $soraDir ('frames_128/'+$soraFrame.file)),[System.Drawing.Imaging.ImageFormat]::Png);$soraGame.Dispose();$soraImage.Dispose()
    }
    $soraBoard.Save((Join-Path $soraDir 'Contact_Sheet.png'),[System.Drawing.Imaging.ImageFormat]::Png)
    $soraSheet.Save((Join-Path $soraDir 'Sprite_Sheet_512.png'),[System.Drawing.Imaging.ImageFormat]::Png)
    $soraGameSheet.Save((Join-Path $soraDir 'Sprite_Sheet_128.png'),[System.Drawing.Imaging.ImageFormat]::Png)
    foreach($soraSize in @(512,128)){
        $soraFrames=if($soraSize -eq 512){$soraLargeGif.ToArray()}else{$soraSmallGif.ToArray()}
        $soraSuffix=if($soraManifest.loop){'Loop'}else{'Once'}
        $soraGif=Join-Path $soraDir ("Preview_${soraSize}_${soraSuffix}.gif")
        [AnimationPackaging]::Gif($soraGif,$soraFrames,[int[]]@($soraManifest.frames | ForEach-Object {$_.durationMs}))
        if(-not $soraManifest.loop){$soraBytes=[System.IO.File]::ReadAllBytes($soraGif)
            if([System.Text.Encoding]::ASCII.GetString($soraBytes,16,11) -ne 'NETSCAPE2.0'){throw 'Unexpected GIF header'}
            [System.IO.File]::WriteAllBytes($soraGif,[byte[]]($soraBytes[0..12]+$soraBytes[32..($soraBytes.Length-1)]))
        }
        $soraCheck=[System.Drawing.Image]::FromFile($soraGif)
        if($soraCheck.GetFrameCount([System.Drawing.Imaging.FrameDimension]::Time) -ne 16){throw 'Wrong preview frame count'}
        $soraCheck.Dispose()
    }
    foreach($soraG in @($soraBoardG,$soraSheetG,$soraGameG)){$soraG.Dispose()}
    foreach($soraB in @($soraBoard,$soraSheet,$soraGameSheet)){$soraB.Dispose()}
    foreach($soraB in $soraLargeGif){$soraB.Dispose()};foreach($soraB in $soraSmallGif){$soraB.Dispose()}
}
$soraFont.Dispose()
$soraLoopData=ConvertTo-Json -InputObject @($soraAll.run_loop.frames | ForEach-Object {[ordered]@{file=$_.file;durationMs=$_.durationMs;phase=$_.phase}}) -Compress
$soraStopData=ConvertTo-Json -InputObject @($soraAll.run_stop.frames | ForEach-Object {[ordered]@{file="../../run_stop/$StopVersion/"+$_.file;durationMs=$_.durationMs;phase=$_.phase}}) -Compress
$soraHtml=@'
<!doctype html><html lang="en"><meta charset="utf-8"><title>Sora run and stop review</title>
<style>body{font:16px system-ui;background:#242b36;color:#f2f4f6;margin:24px}h1{font-size:23px}button,select{padding:9px;margin:3px;border-radius:5px;border:0}#views{display:flex;align-items:end;gap:24px;flex-wrap:wrap}figure{margin:14px 0}canvas{background:#fff;border:1px solid #606873}input{width:510px;max-width:90vw}small{color:#c2cad6}#large{width:min(512px,85vw);height:auto}</style>
<h1>Sora: full run and run stop</h1><p>16 alternating strides, then 16 braking and guard-recovery drawings.</p>
<select id="kind"><option value="run">Run loop</option><option value="stop">Run stop</option></select>
<button id="play">Play</button><button id="join">Run twice → stop</button><button id="pause">Pause</button><button id="slow">Slow: off</button>
<div id="views"><figure><canvas id="large" width="512" height="512"></canvas><figcaption>Working art</figcaption></figure><figure><canvas id="small" width="128" height="128"></canvas><figcaption>128-pixel export size</figcaption></figure></div>
<input type="range" id="scrub" min="0" max="15" value="0"><p id="label"></p>
<small>Flat-canvas motion draft. Compare the loop seam, foot contacts and shoulder carry. Final idle join and material refinement remain; no Godot integration.</small>
<script>
const run=__RUN__,stop=__STOP__;
const images=new Map(),large=document.querySelector('#large'),small=document.querySelector('#small'),kind=document.querySelector('#kind'),scrub=document.querySelector('#scrub'),label=document.querySelector('#label');
let sequence=run,index=0,timer=null,slow=false,joinMode=false;
for(const f of [...run,...stop]){const img=new Image();img.src=f.file;img.onload=()=>{if(sequence[index]===f)draw()};images.set(f.file,img);}
function halt(){clearTimeout(timer);timer=null;joinMode=false;}
function draw(){const f=sequence[index],img=images.get(f.file);for(const c of [large,small]){const g=c.getContext('2d');g.fillStyle='white';g.fillRect(0,0,c.width,c.height);if(img.complete&&img.naturalWidth)g.drawImage(img,0,0,c.width,c.height);}scrub.value=index%16;label.textContent=`${joinMode?'Run → stop':kind.value==='run'?'Run':'Stop'} · ${String(index%16).padStart(2,'0')} · ${f.phase} · ${f.durationMs}ms`;}
function tick(){draw();timer=setTimeout(()=>{if(index+1<sequence.length){index++;tick();}else if(!joinMode&&kind.value==='run'){index=0;tick();}else{timer=null;joinMode=false;}},sequence[index].durationMs*(slow?3:1));}
kind.onchange=()=>{halt();sequence=kind.value==='run'?run:stop;index=0;draw();};
scrub.oninput=()=>{halt();sequence=kind.value==='run'?run:stop;index=Number(scrub.value);draw();};
document.querySelector('#play').onclick=()=>{halt();sequence=kind.value==='run'?run:stop;if(index>=sequence.length-1)index=0;tick();};
document.querySelector('#join').onclick=()=>{halt();sequence=[...run,...run,...stop];index=0;joinMode=true;tick();};
document.querySelector('#pause').onclick=halt;
document.querySelector('#slow').onclick=()=>{slow=!slow;document.querySelector('#slow').textContent=`Slow: ${slow?'on':'off'}`;};draw();
</script></html>
'@
$soraHtml=$soraHtml.Replace('__RUN__',$soraLoopData).Replace('__STOP__',$soraStopData)
Set-Content -LiteralPath (Join-Path $soraLoopDir 'Review.html') -Value $soraHtml -Encoding UTF8
if((Get-FileHash -LiteralPath (Join-Path $soraLoopDir 'sora_run_loop_00.png') -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath (Join-Path $soraStopDir 'sora_run_stop_00.png') -Algorithm SHA256).Hash){throw 'Loop-to-stop entry changed'}
Write-Output 'Packaged512/128 PNG sheets, individual128 exports,16-frame previews and a combined scrubber. Shared loop/stop entry verified.'
