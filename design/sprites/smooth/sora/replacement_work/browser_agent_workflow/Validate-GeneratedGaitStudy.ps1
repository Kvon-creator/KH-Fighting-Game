param([ValidatePattern('^gait_cycle_study_v[0-9]+$')][string]$Version='gait_cycle_study_v5')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw 'Unexpected workspace'}
$soraReady=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready'
$soraOut=Join-Path $soraReady "run_loop/direct_generation_retry_v1/$Version"
$soraManifest=Get-Content -LiteralPath (Join-Path $soraOut 'manifest.json') -Raw | ConvertFrom-Json
Add-Type -AssemblyName System.Drawing
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
using System.Collections.Generic;
public static class GaitRasterInspection {
  static byte[] Pixels(Bitmap b) {
    var d=b.LockBits(new Rectangle(0,0,b.Width,b.Height),ImageLockMode.ReadOnly,PixelFormat.Format32bppArgb);
    try {var a=new byte[b.Width*b.Height*4];for(int y=0;y<b.Height;y++)Marshal.Copy(IntPtr.Add(d.Scan0,y*d.Stride),a,y*b.Width*4,b.Width*4);return a;}
    finally {b.UnlockBits(d);}
  }
  public static int[] Inspect(string file,int size) {
    using(var b=new Bitmap(file)) {
      if(b.Width!=size||b.Height!=size||!Image.IsAlphaPixelFormat(b.PixelFormat))throw new Exception("Invalid RGBA export: "+file);
      var p=Pixels(b);int left=size,top=size,right=0,bottom=0,solid=0,min=255,max=0;
      for(int y=0;y<size;y++)for(int x=0;x<size;x++){int a=p[(y*size+x)*4+3];min=Math.Min(min,a);max=Math.Max(max,a);if(a>0){left=Math.Min(left,x);top=Math.Min(top,y);right=Math.Max(right,x+1);bottom=Math.Max(bottom,y+1);}if(a>100)solid=Math.Max(solid,y+1);}
      if(min!=0||max!=255||left<=0||top<=0||right>=size||bottom>=size)throw new Exception("Alpha/margin failure: "+file);
      var visited=new bool[size*size];var queue=new Queue<int>();var components=new List<int>();
      for(int i=0;i<visited.Length;i++) {
        if(visited[i]||p[i*4+3]<=100)continue;visited[i]=true;queue.Enqueue(i);int count=0;
        while(queue.Count>0){int j=queue.Dequeue();count++;int x=j%size,y=j/size;for(int dy=-1;dy<=1;dy++)for(int dx=-1;dx<=1;dx++){int nx=x+dx,ny=y+dy;if(nx<0||ny<0||nx>=size||ny>=size)continue;int k=ny*size+nx;if(!visited[k]&&p[k*4+3]>100){visited[k]=true;queue.Enqueue(k);}}}
        if(count>8)components.Add(count);
      }
      if(size==512&&components.Count!=1)throw new Exception("Detached opaque component: "+file);
      return new[]{left,top,right,bottom,solid};
    }
  }
  public static void Upper(string file,string stage,string native,int shift,int top) {
    using(var b=new Bitmap(file))using(var s=new Bitmap(stage))using(var n=new Bitmap(native)) {
      var p=Pixels(b);var a=Pixels(s);var original=Pixels(n);
      for(int y=0;y<top;y++)for(int x=0;x<512;x++)for(int c=0;c<4;c++){
        int sy=y-shift;byte expected=sy<0?(byte)(c==3?0:255):a[(sy*512+x)*4+c];
        if(p[(y*512+x)*4+c]!=expected)throw new Exception("Upper-body bob mismatch");
      }
      for(int y=0;y<270;y++)for(int x=0;x<512;x++) {
        bool protect=x<280||y<223||(y>=207&&y<259&&x>=410&&x<485);
        if(protect)for(int c=0;c<4;c++)if(a[(y*512+x)*4+c]!=original[(y*512+x)*4+c])throw new Exception("Protected native carry/face/blade changed");
      }
    }
  }
  public static void Gif(string file,int size,int[] durations) {
    using(var image=Image.FromFile(file)){
      if(image.Width!=size||image.Height!=size||image.GetFrameCount(FrameDimension.Time)!=durations.Length)throw new Exception("GIF size/count mismatch");
      var delay=image.GetPropertyItem(0x5100).Value;
      for(int i=0;i<durations.Length;i++)if(BitConverter.ToInt32(delay,i*4)*10!=durations[i])throw new Exception("GIF timing mismatch");
      if(BitConverter.ToUInt16(image.GetPropertyItem(0x5101).Value,0)!=0)throw new Exception("GIF repeat mismatch");
    }
  }
}
'@
function Get-SoraDistance($a,$b){[Math]::Sqrt([Math]::Pow($a[0]-$b[0],2)+[Math]::Pow($a[1]-$b[1],2))}
if($soraManifest.frameCount -ne $soraManifest.frames.Count){throw 'Manifest count mismatch'}
if(($soraManifest.frames | Measure-Object durationMs -Sum).Sum -ne 960){throw 'Cycle duration changed'}
for($soraIndex=0;$soraIndex -lt $soraManifest.sourceFiles.Count;$soraIndex++){
    if((Get-FileHash -LiteralPath $soraManifest.sourceFiles[$soraIndex]).Hash.ToLowerInvariant() -ne $soraManifest.sourceHashes[$soraIndex]){throw 'Brush source changed'}
}
$soraProtected=@{
 'run_start/sync_refinement_v2/flat_lift_pilot_v5/full_start_study/Run_Start_13_Once.gif'='1f9f81975ea11f747e8956e72e9705968ae5fdb8379e5622bc785c7aad747d41'
 'standing_idle/sora_stand_idle_00.png'='baf8959c0e0d42b74bf7f6100a83ccf5c208a9decd5b98b95110f3129fbacdc7'
 'run_loop/direct_generation_retry_v1/sora_run_loop_generated_original.png'='9d919b4f317981b331010a1ddb049a7807fb8f21ba214d82a40b04291c9065c7'
 'run_stop/direct_generation_retry_v1/sora_run_stop_generated_original.png'='89b6f8044e80f33f0ee8010acdf44942a0185ee82f8bb5a0adf5b1dad88d552e'
}
foreach($soraItem in $soraProtected.GetEnumerator()){if((Get-FileHash -LiteralPath (Join-Path $soraReady $soraItem.Key)).Hash.ToLowerInvariant() -ne $soraItem.Value){throw "Protected source changed: $($soraItem.Key)"}}
$soraRows=@();$soraSteps=@()
foreach($soraFrame in $soraManifest.frames){
 $soraFile=Join-Path $soraOut $soraFrame.file
 if((Get-FileHash -LiteralPath $soraFile).Hash.ToLowerInvariant() -ne $soraFrame.sha256){throw 'Frame hash mismatch'}
 $soraBounds=[GaitRasterInspection]::Inspect($soraFile,512)
 [GaitRasterInspection]::Inspect((Join-Path $soraOut "frames_128/$($soraFrame.file)"),128) | Out-Null
 if($soraBounds[4] -ne $soraFrame.supportOpaqueBottom){throw 'Recorded sole mismatch'}
 if($soraFrame.support -eq 'none'){if($soraBounds[4] -ge 470){throw 'Flight lacks clearance'}}elseif($soraBounds[4] -ne 470){throw 'Support sole displaced'}
 $soraExpectedSupport=if($soraFrame.keyPosition -lt 5){'far'}elseif($soraFrame.keyPosition -ge 6 -and $soraFrame.keyPosition -le 10){'near'}else{'none'}
 if($soraFrame.support -ne $soraExpectedSupport){throw 'Support phase mismatch'}
 $soraStage=Join-Path $soraOut $soraFrame.upperWholeCanvasStage
 if((Get-FileHash -LiteralPath $soraStage).Hash.ToLowerInvariant() -ne $soraFrame.upperStageSha256){throw 'Arm-stage hash mismatch'}
 [GaitRasterInspection]::Upper($soraFile,$soraStage,$soraManifest.sourceFiles[1],$soraFrame.bodyShiftY,$soraFrame.protectedUpperExclusiveY)
 $soraLegs=@(@(0,1,$soraManifest.nearThigh),@(1,2,$soraManifest.nearShin),@(3,4,$soraManifest.farThigh),@(4,5,$soraManifest.farShin))
 foreach($soraLeg in $soraLegs){if([Math]::Abs((Get-SoraDistance $soraFrame.joints[$soraLeg[0]] $soraFrame.joints[$soraLeg[1]])-$soraLeg[2]) -ge .002){throw 'Leg-guide length mismatch'}}
 foreach($soraArm in @(@('shoulder','elbow','upperLength'),@('elbow','wrist','forearmLength'))){if([Math]::Abs((Get-SoraDistance $soraFrame.arm.($soraArm[0]) $soraFrame.arm.($soraArm[1]))-$soraFrame.arm.($soraArm[2])) -ge .002){throw 'Arm-guide length mismatch'}}
 $soraNext=$soraManifest.frames[($soraFrame.index+1)%$soraManifest.frameCount]
 $soraSteps+=@{from=$soraFrame.index;to=$soraNext.index;nearAnkleDistance=(Get-SoraDistance $soraFrame.joints[2] $soraNext.joints[2]);farAnkleDistance=(Get-SoraDistance $soraFrame.joints[5] $soraNext.joints[5])}
 $soraRows+=@{index=$soraFrame.index;keyPosition=$soraFrame.keyPosition;bounds=$soraBounds;support=$soraFrame.support;solidFlightClearance=(470-$soraBounds[4])}
}
if(@($soraManifest.frames.sha256 | Select-Object -Unique).Count -ne $soraManifest.frameCount){throw 'Duplicate complete pose'}
foreach($soraSize in @(512,128)){[GaitRasterInspection]::Gif((Join-Path $soraOut "Preview_${soraSize}_Loop.gif"),$soraSize,[int[]]$soraManifest.frames.durationMs)}
$soraHtml=Get-Content -LiteralPath (Join-Path $soraOut 'Review.html') -Raw
$soraViewerFrames=[regex]::Match($soraHtml,'const frames=(.*?);const q=').Groups[1].Value | ConvertFrom-Json
if($soraViewerFrames.Count -ne $soraManifest.frameCount){throw 'Viewer count mismatch'}
foreach($soraFrame in $soraViewerFrames){foreach($soraField in @('file','game','original','arm','gait','previous')){if(-not(Test-Path -LiteralPath (Join-Path $soraOut $soraFrame.$soraField))){throw "Viewer asset missing: $soraField"}}}
foreach($soraLink in [regex]::Matches($soraHtml,'href="([^"]+)"')){if(-not(Test-Path -LiteralPath (Join-Path $soraOut $soraLink.Groups[1].Value))){throw 'Review link missing'}}
$soraPrevious=Get-Content -LiteralPath (Join-Path $soraReady 'run_loop/direct_generation_retry_v1/gait_cycle_study_v4/manifest.json') -Raw | ConvertFrom-Json
$soraPreserved=0
foreach($soraFrame in $soraPrevious.frames){$soraMatching=@($soraManifest.frames | Where-Object keyPosition -eq $soraFrame.keyPosition);if($soraMatching.Count -ne 1 -or $soraMatching[0].sha256 -ne $soraFrame.sha256){throw 'Previous drawing changed'};$soraPreserved++}
$soraReport=[ordered]@{version=$Version;frameCount=$soraManifest.frameCount;durationMs=960;distinctRgbaExports=$true;alphaMarginsAndConnectedOpaqueFigure=$true;supportFlightAndGuideLengths=$true;protectedNativeCarryFaceBladeAndUpperBob=$true;sourceBenchmarkIdleHashesUnchanged=$true;previousDrawingsPreserved=$soraPreserved;gifTimingAndRepeat=$true;viewerAssetsAndLinksExist=$true;frames=$soraRows;cyclicAnkleStepMeasurements=$soraSteps;limitations=@('Viewer controls have not been executed in a browser or JavaScript runtime.','No Godot integration or playback test.','Geometry/export checks do not establish final artwork or natural-motion approval.')}
if(Test-Path -LiteralPath (Join-Path $soraOut 'QA_Report.json')){throw 'Preserve previous QA report'}
$soraReport | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $soraOut 'QA_Report.json') -Encoding UTF8
Write-Output "PASS: $($soraManifest.frameCount) poses; $soraPreserved previous drawings preserved; RGBA, floor, guides, protected pixels, provenance, GIFs and viewer links. Controls/browser/Godot untested."
