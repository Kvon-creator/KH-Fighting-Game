param([ValidatePattern('^gait_cycle_study_v[0-9]+$')][string]$Version='gait_cycle_study_v4')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraReady=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready'
$soraOut=Join-Path $soraReady "run_loop/direct_generation_retry_v1/$Version"
if(Test-Path -LiteralPath (Join-Path $soraOut 'Review.html')){throw 'Preserve previous viewer'}
$soraManifest=Get-Content -LiteralPath (Join-Path $soraOut 'manifest.json') -Raw | ConvertFrom-Json
$soraFrames=ConvertTo-Json -InputObject @($soraManifest.frames | ForEach-Object {
    $soraKey=[int][Math]::Floor($_.keyPosition)
    @{file=$_.file;game="frames_128/$($_.file)";phase=$_.phase;support=$_.support;durationMs=$_.durationMs;keyPosition=$_.keyPosition;original=('../whole_frame_review_v1/sora_run_loop_{0:00}.png' -f $soraKey);arm=('../motion_refinement_v4/sora_run_loop_{0:00}.png' -f $soraKey);gait=('../gait_cycle_study_v3/sora_run_loop_{0:00}.png' -f $soraKey)}
}) -Compress
$soraHtml=@'
<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sora alternating-stride refinement</title>
<style>body{font:16px system-ui;background:#242b36;color:#f4f5f8;margin:24px;max-width:1160px}button,select{padding:9px;margin:3px;border:0;border-radius:5px}canvas{background:#fff;border:1px solid #66707d}#views{display:flex;align-items:start;gap:20px;flex-wrap:wrap}figure{margin:0}#original,#large{width:min(512px,85vw);height:auto}input[type=range]{width:800px;max-width:90vw}a{color:#a8d5ff}figcaption{padding:6px 0}.note{color:#cbd3df;max-width:1000px}#label{font-variant-numeric:tabular-nums}</style>
<h1>Sora alternating-stride refinement</h1>
<p>Sixteen complete drawings: alternate supporting legs, compression, passing and flight, with a free-arm counter-swing. Four new joint poses bridge the largest gaps. The cycle remains 960ms.</p>
<p class="note">Comparison panels use the same cycle time; earlier drawings have different leg roles. Garment volume, sleeve joins, torso/chain follow-through and start/stop transitions still need refinement against the run-start benchmark. This is an art study, pending motion and quality approval.</p>
<p><a href="Contact_Sheet.png">New pose board</a> | <a href="Preview_512_Loop.gif">New loop GIF</a> | <a href="Sprite_Sheet_512.png">Transparent sheet</a> | <a href="ART_REVIEW.md">Review notes</a> | <a href="../motion_refinement_v4/Original_Refinement_Comparison.png">Original/arm/stop comparison</a> | <a href="../../../run_start/sync_refinement_v2/flat_lift_pilot_v5/full_start_study/Run_Start_13_Once.gif">Run-start quality benchmark</a> | <a href="../../../run_stop/direct_generation_retry_v1/motion_refinement_v4/Preview_512_Once.gif">Preserved stop study</a></p>
<select id="kind" aria-label="Comparison"><option value="arm">Previous free-arm study</option><option value="original">Original generated drawings</option><option value="gait">Twelve-pose stride before new transitions</option></select>
<button id="play">Play</button><button id="pause">Pause</button><button id="previous">Previous</button><button id="next">Next</button><button id="slow">Slow x3</button><label><input id="guide" type="checkbox" checked> Solid-sole floor</label>
<div id="views"><figure><figcaption id="comparisonCaption">Previous free-arm study</figcaption><canvas id="original" width="512" height="512"></canvas></figure><figure><figcaption>New stride refinement</figcaption><canvas id="large" width="512" height="512"></canvas><figcaption>Actual transparent 128px export</figcaption><canvas id="small" width="128" height="128"></canvas></figure></div>
<p id="label"></p><input id="scrub" aria-label="Frame" type="range" min="0" max="15" value="0">
<p class="note">The floor follows solid pixels (alpha above 100); faint source edge/shadow alpha extends a few pixels lower. No game integration or actual-browser playback test is included.</p>
<script>
const frames=__FRAMES__;const q=s=>document.querySelector(s),images=new Map();let timer=null,index=0,slow=false,playing=false;
function imageFor(file){let img=images.get(file);if(!img){img=new Image();images.set(file,img);img.onload=draw;img.src=file;}return img;}
function paint(id,file){const img=imageFor(file),c=q(id),g=c.getContext('2d');g.fillStyle='#fff';g.fillRect(0,0,c.width,c.height);if(img.complete&&img.naturalWidth)g.drawImage(img,0,0,c.width,c.height);if(q('#guide').checked){g.strokeStyle='#8e9da9';g.lineWidth=1;g.setLineDash([4,4]);g.beginPath();g.moveTo(0,470*c.height/512);g.lineTo(c.width,470*c.height/512);g.stroke();g.setLineDash([]);}}
function draw(){const f=frames[index];paint('#original',f[q('#kind').value]);paint('#large',f.file);paint('#small',f.game);q('#comparisonCaption').textContent=q('#kind').value==='arm'?'Previous free-arm study':q('#kind').value==='original'?'Original generated drawings':'Twelve-pose stride before new transitions';q('#label').textContent=`${index+1}/${frames.length}: ${f.phase}; support ${f.support}; ${f.durationMs}ms; previous key ${f.keyPosition}`;q('#scrub').max=frames.length-1;q('#scrub').value=index;}
function pause(){playing=false;if(timer!==null)clearTimeout(timer);timer=null;}
function schedule(){timer=setTimeout(tick,frames[index].durationMs*(slow?3:1));}
function tick(){index=(index+1)%frames.length;draw();schedule();}
q('#play').onclick=()=>{pause();playing=true;draw();schedule();};q('#pause').onclick=pause;
q('#kind').onchange=draw;q('#scrub').oninput=()=>{pause();index=+q('#scrub').value;draw();};
q('#previous').onclick=()=>{pause();index=Math.max(0,index-1);draw();};q('#next').onclick=()=>{pause();index=Math.min(frames.length-1,index+1);draw();};
q('#slow').onclick=()=>{slow=!slow;q('#slow').textContent=slow?'Normal speed':'Slow x3';if(playing){clearTimeout(timer);schedule();}};q('#guide').onchange=draw;
for(const f of frames)for(const key of ['file','game','arm','original','gait'])imageFor(f[key]);draw();
</script></html>
'@
[System.IO.File]::WriteAllText((Join-Path $soraOut 'Review.html'),$soraHtml.Replace('__FRAMES__',$soraFrames).TrimEnd()+[Environment]::NewLine,[System.Text.UTF8Encoding]::new($false))
Write-Output 'Gait comparison viewer saved; actual playback remains untested.'
