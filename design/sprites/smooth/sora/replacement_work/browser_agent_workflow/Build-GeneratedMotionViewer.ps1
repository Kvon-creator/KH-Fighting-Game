param([ValidatePattern('^motion_refinement_v[0-9]+$')][string]$Version='motion_refinement_v3')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraReady=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready'
$soraOut=Join-Path $soraReady "run_loop/direct_generation_retry_v1/$Version"
$soraStopOut=Join-Path $soraReady "run_stop/direct_generation_retry_v1/$Version"
if(Test-Path -LiteralPath (Join-Path $soraOut 'Review.html')){throw 'Preserve previous viewer'}
$soraRun=Get-Content -LiteralPath (Join-Path $soraOut 'manifest.json') -Raw | ConvertFrom-Json
$soraStop=Get-Content -LiteralPath (Join-Path $soraStopOut 'manifest.json') -Raw | ConvertFrom-Json
$soraRunData=ConvertTo-Json -InputObject @($soraRun.frames | ForEach-Object {@{file=$_.file;original="../whole_frame_review_v1/$($_.file)";durationMs=$_.durationMs;label="Run pose $($_.index)";source=[System.IO.Path]::GetFileName($_.source)}}) -Compress
$soraStopData=ConvertTo-Json -InputObject @($soraStop.frames | ForEach-Object {@{file="../../../run_stop/direct_generation_retry_v1/$Version/$($_.file)";original="../../../run_stop/direct_generation_retry_v1/whole_frame_review_v1/$($_.file)";durationMs=$_.durationMs;label="Stop study pose $($_.index)";source=[System.IO.Path]::GetFileName($_.source)}}) -Compress
$soraHtml=@'
<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sora movement refinement study</title>
<style>body{font:16px system-ui;background:#242b36;color:#f2f4f6;margin:24px;max-width:1160px}button,select{padding:9px;margin:3px;border:0;border-radius:5px}canvas{background:#fff;border:1px solid #606873}#views{display:flex;align-items:start;gap:20px;flex-wrap:wrap}.panel{margin:0}#original,#large{width:min(512px,85vw);height:auto}input[type=range]{width:800px;max-width:90vw}a{color:#a8d5ff}figcaption{padding:6px 0}#label{font-variant-numeric:tabular-nums}.note{color:#cbd3df;max-width:1000px}</style>
<h1>Sora movement refinement study</h1>
<p>The free arm now swings through the run poses. The stop study holds shoulder carry before clearing and lowering the weapon. Its entry matches run pose00.</p>
<p class="note">The stop uses selected complete poses; its braking footwork still needs new drawings. Jacket joins, alternating stride, weapon consistency and the idle transition remain under review. Earlier stop painting pilots have waist seams and are excluded here.</p>
<p><a href="Contact_Sheet.png">Run pose board</a> | <a href="../../../run_stop/direct_generation_retry_v1/__VERSION__/Contact_Sheet.png">Stop pose board</a> | <a href="Preview_512_Loop.gif">Run GIF</a> | <a href="../../../run_stop/direct_generation_retry_v1/__VERSION__/Preview_512_Once.gif">Stop GIF</a> | <a href="ART_REVIEW.md">Review notes</a></p>
<select id="kind"><option value="run">Run loop</option><option value="stop">Stop carry-order study</option><option value="join">Two loops into stop</option></select>
<button id="play">Play</button><button id="pause">Pause</button><button id="previous">Previous</button><button id="next">Next</button><button id="slow">Slow x3</button><label><input id="guide" type="checkbox" checked> Floor guide</label>
<div id="views"><figure class="panel"><figcaption>Original sheet order (same displayed index)</figcaption><canvas id="original" width="512" height="512"></canvas></figure><figure class="panel"><figcaption>Refinement study</figcaption><canvas id="large" width="512" height="512"></canvas><figcaption>128px export scale</figcaption><canvas id="small" width="128" height="128"></canvas></figure></div>
<p id="label"></p><input id="scrub" type="range" min="0" max="11" value="0">
<script>
const run=__RUN__,stop=__STOP__;const q=s=>document.querySelector(s),images=new Map();let timer=null,index=0,slow=false,playing=false;
const sequence=()=>q('#kind').value==='stop'?stop:q('#kind').value==='join'?[...run,...run,...stop]:run;
function paint(id,file){let img=images.get(file);if(!img){img=new Image();images.set(file,img);img.onload=draw;img.src=file;}const c=q(id),g=c.getContext('2d');g.fillStyle='#fff';g.fillRect(0,0,c.width,c.height);if(img.complete&&img.naturalWidth)g.drawImage(img,0,0,c.width,c.height);if(q('#guide').checked){g.strokeStyle='#8e9da9';g.lineWidth=1;g.setLineDash([4,4]);g.beginPath();g.moveTo(0,470*c.height/512);g.lineTo(c.width,470*c.height/512);g.stroke();g.setLineDash([]);}}
function draw(){const a=sequence(),f=a[index];paint('#original',f.original);paint('#large',f.file);paint('#small',f.file);q('#label').textContent=`${f.label}: ${index+1}/${a.length}, ${f.durationMs}ms; selected source ${f.source}`;q('#scrub').max=a.length-1;q('#scrub').value=index;}
function pause(){playing=false;if(timer!==null)clearTimeout(timer);timer=null;}
function schedule(){timer=setTimeout(tick,sequence()[index].durationMs*(slow?3:1));}
function tick(){const a=sequence();if(index===a.length-1){if(q('#kind').value!=='run'){pause();return;}index=0;}else index++;draw();schedule();}
q('#play').onclick=()=>{pause();playing=true;if(index===sequence().length-1)index=0;draw();schedule();};q('#pause').onclick=pause;
q('#kind').onchange=()=>{pause();index=0;draw();};q('#scrub').oninput=()=>{pause();index=+q('#scrub').value;draw();};
q('#previous').onclick=()=>{pause();index=Math.max(0,index-1);draw();};q('#next').onclick=()=>{pause();index=Math.min(sequence().length-1,index+1);draw();};
q('#slow').onclick=()=>{slow=!slow;q('#slow').textContent=slow?'Normal speed':'Slow x3';if(playing){clearTimeout(timer);schedule();}};q('#guide').onchange=draw;draw();
</script></html>
'@
$soraHtml=$soraHtml.Replace('__RUN__',$soraRunData).Replace('__STOP__',$soraStopData).Replace('__VERSION__',$Version)
[System.IO.File]::WriteAllText((Join-Path $soraOut 'Review.html'),$soraHtml.TrimEnd()+[Environment]::NewLine,[System.Text.UTF8Encoding]::new($false))
Write-Output 'Comparison viewer created; offline checks and visual review remain separate from actual-browser playback.'
