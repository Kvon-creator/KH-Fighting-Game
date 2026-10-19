param([ValidatePattern('^adjacent_guides_v[0-9]+$')][string]$Version='adjacent_guides_v1')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraReady=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready'
$soraTrial=Join-Path $soraReady 'run_loop/comfyui_trial'
$soraSources=Join-Path $soraReady 'run_loop/direct_generation_retry_v1/whole_frame_review_v1'
$soraPilot=Join-Path $soraTrial 'attempt_03/final_pose_v1.png'
$soraOriginal=Join-Path $soraTrial 'reference_v1/whole_pose_00_white.png'
$soraChecks=@(@($soraPilot,'3dd7b620289eaf707973cb71ec05d901637f5251c45d3745f180f657a77b7d2b'),@($soraOriginal,'a3681849fa6b2a235fd36622866057191f0d073d39ea9cff8b7e30764f6d9022'))
foreach($soraPair in $soraChecks){if((Get-FileHash -LiteralPath $soraPair[0] -Algorithm SHA256).Hash.ToLowerInvariant() -ne $soraPair[1]){throw 'Approved pilot/source changed'}}
$soraOut=Join-Path $soraTrial $Version
if(Test-Path -LiteralPath $soraOut){throw 'Preserve existing guide version'}
Add-Type -AssemblyName System.Drawing
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
public static class AdjacentRunGuide {
    static Color C(string h){return ColorTranslator.FromHtml(h);}
    static void Fill(Graphics g,GraphicsPath p,string c,float width){using(var b=new SolidBrush(C(c)))g.FillPath(b,p);if(width>0)using(var pen=new Pen(C("#251E19"),width)){pen.LineJoin=LineJoin.Round;g.DrawPath(pen,p);}}
    static void Poly(Graphics g,PointF[] points,string c,float width){using(var p=new GraphicsPath()){p.AddPolygon(points);Fill(g,p,c,width);}}
    static void Fist(Graphics g,float x,float y,float angle){
        var s=g.Save();g.TranslateTransform(x,y);g.RotateTransform(angle);
        Poly(g,new[]{new PointF(-8,-7),new PointF(7,-7),new PointF(9,3),new PointF(-8,4)},"#252A2C",1.8f);
        using(var p=new Pen(C("#DDA820"),2.1f))g.DrawLine(p,-7,-3,7,-3);
        using(var fist=new GraphicsPath()){
            fist.AddBezier(-7,0,-13,2,-15,8,-12,15);fist.AddBezier(-12,15,-9,22,4,23,10,18);
            fist.AddBezier(10,18,15,13,15,5,10,1);fist.AddBezier(10,1,5,-2,-1,-2,-7,0);fist.CloseFigure();Fill(g,fist,"#252C2E",2);
        }
        Poly(g,new[]{new PointF(-12,10),new PointF(-8,18),new PointF(2,21),new PointF(9,16),new PointF(0,13)},"#151B1D",0);
        using(var f=new GraphicsPath()){
            f.AddBezier(-9,6,-5,5,2,6,7,8);f.AddBezier(7,8,10,10,8,14,5,16);
            f.AddBezier(5,16,0,19,-7,16,-9,13);f.CloseFigure();Fill(g,f,"#F7B67D",1.2f);
        }
        using(var p=new Pen(C("#FFD5AC"),1.3f))g.DrawBezier(p,-8,8,-3,7,3,8,6,10);
        using(var p=new Pen(C("#794829"),1)){g.DrawLine(p,-4,8,-5,14);g.DrawLine(p,0,8,0,15);g.DrawLine(p,4,9,4,14);}
        using(var t=new GraphicsPath()){
            t.AddBezier(8,2,13,3,15,7,11,10);t.AddBezier(11,10,8,13,2,10,0,7);t.AddBezier(0,7,1,3,5,5,8,2);t.CloseFigure();Fill(g,t,"#FFC28E",1.3f);
        }
        using(var b=new SolidBrush(C("#899196")))g.FillEllipse(b,2,0,2,2);
        g.Restore(s);
    }
    static void Arm(Graphics g,int index,int bob){
        var state=g.Save();g.TranslateTransform(0,bob);
        // Each silhouette follows new shoulder/elbow/wrist landmarks, without scaling a prior arm.
        if(index==1){
            using(var skin=new GraphicsPath()){
                skin.AddBezier(321,266,311,268,302,275,300,283);
                skin.AddBezier(300,283,301,291,307,302,313,310);
                skin.AddBezier(313,310,316,314,324,312,325,306);
                skin.AddBezier(325,306,321,296,315,287,314,282);
                skin.AddBezier(314,282,320,278,327,276,328,272);skin.CloseFigure();Fill(g,skin,"#F6B57A",2.3f);
            }
            using(var sh=new GraphicsPath()){sh.AddBezier(301,281,304,291,312,306,317,309);sh.AddLine(317,309,323,306);sh.AddBezier(323,306,319,298,315,291,311,283);sh.CloseFigure();Fill(g,sh,"#D78B52",0);}
            using(var p=new Pen(C("#FFD1A3"),2.2f)){p.StartCap=p.EndCap=LineCap.Round;g.DrawBezier(p,307,281,308,287,311,292,313,296);}
            using(var sleeve=new GraphicsPath()){
                sleeve.AddBezier(355,243,344,240,330,247,319,258);sleeve.AddBezier(319,258,313,264,314,270,320,276);
                sleeve.AddBezier(320,276,334,279,349,266,354,256);sleeve.AddBezier(354,256,360,251,360,247,355,243);sleeve.CloseFigure();Fill(g,sleeve,"#283237",2.3f);
            }
            Poly(g,new[]{new PointF(339,247),new PointF(326,254),new PointF(321,264),new PointF(331,268),new PointF(344,257)},"#465156",0);
            using(var p=new Pen(C("#ECECE5"),3.7f))g.DrawBezier(p,317,265,316,270,320,274,325,275);
            using(var p=new Pen(C("#171F24"),1.2f))g.DrawBezier(p,336,251,332,254,328,258,327,262);
            Fist(g,319,307,-12);
        }else{
            using(var skin=new GraphicsPath()){
                skin.AddBezier(331,268,324,272,318,281,319,289);skin.AddBezier(319,289,321,296,332,300,348,306);
                skin.AddBezier(348,306,353,308,358,300,354,296);skin.AddBezier(354,296,343,291,334,288,333,285);
                skin.AddBezier(333,285,337,278,339,274,339,271);skin.CloseFigure();Fill(g,skin,"#F6B57A",2.3f);
            }
            Poly(g,new[]{new PointF(320,286),new PointF(325,294),new PointF(350,304),new PointF(355,298),new PointF(331,288)},"#D78B52",0);
            using(var p=new Pen(C("#FFD1A3"),2.0f)){p.StartCap=p.EndCap=LineCap.Round;g.DrawBezier(p,327,285,331,287,340,291,346,292);}
            using(var sleeve=new GraphicsPath()){
                sleeve.AddBezier(355,243,341,241,329,250,325,260);sleeve.AddBezier(325,260,322,267,325,274,332,279);
                sleeve.AddBezier(332,279,345,277,354,267,356,257);sleeve.AddBezier(356,257,360,248,355,243,355,243);sleeve.CloseFigure();Fill(g,sleeve,"#283237",2.3f);
            }
            Poly(g,new[]{new PointF(341,248),new PointF(332,257),new PointF(330,268),new PointF(337,271),new PointF(347,258)},"#465156",0);
            using(var p=new Pen(C("#ECECE5"),3.7f))g.DrawBezier(p,326,268,327,274,331,277,335,277);
            Fist(g,352,300,-53);
        }
        g.Restore(state);
    }
    public static void Paint(string pilotFile,string originalFile,string sourceFile,string guideFile,string maskFile,int index,int bob){
        using(var pilot=new Bitmap(pilotFile))using(var original=new Bitmap(originalFile))using(var source=new Bitmap(sourceFile))
        using(var canvas=new Bitmap(512,512,PixelFormat.Format24bppRgb))using(var mask=new Bitmap(512,512,PixelFormat.Format24bppRgb)){
            using(var g=Graphics.FromImage(canvas)){
                g.Clear(Color.White);g.DrawImageUnscaled(pilot,0,bob);g.SmoothingMode=SmoothingMode.AntiAlias;
                // Restore underlying jacket/belt from the complete original before the next arm drawing.
                var s=g.Save();using(var p=new GraphicsPath()){
                    p.AddPolygon(new[]{new PointF(277,258+bob),new PointF(331,241+bob),new PointF(358,246+bob),new PointF(353,282+bob),new PointF(328,329+bob),new PointF(277,328+bob)});
                    g.SetClip(p);g.DrawImageUnscaled(original,0,bob);
                }g.Restore(s);
                // Clear the former forward-sleeve edge and old lower silhouette before drawing replacements.
                g.FillRectangle(Brushes.White,351,243+bob,150,105);
                g.FillRectangle(Brushes.White,0,286+bob,512,226-bob);
                // Whole source01/02 supplies genuinely different shorts, knees, calves and feet.
                // This temporary path ends under the waist and excludes the old forward arm.
                s=g.Save();using(var p=new GraphicsPath()){
                    p.AddPolygon(new[]{new PointF(0,286+bob),new PointF(266,286+bob),new PointF(283,286+bob),new PointF(340,292+bob),new PointF(357,302+bob),new PointF(376,318+bob),new PointF(400,338+bob),new PointF(416,348+bob),new PointF(512,348+bob),new PointF(512,512),new PointF(0,512)});
                    g.SetClip(p);g.FillRectangle(Brushes.White,0,280,512,232);g.DrawImageUnscaled(source,0,0);
                }g.Restore(s);
                Arm(g,index,bob);
            }
            using(var g=Graphics.FromImage(mask)){
                g.Clear(Color.Black);g.SmoothingMode=SmoothingMode.AntiAlias;
                g.FillPolygon(Brushes.White,new[]{new PointF(278,254+bob),new PointF(322,238+bob),new PointF(362,240+bob),new PointF(376,274+bob),new PointF(382,325+bob),new PointF(345,341+bob),new PointF(286,338+bob),new PointF(275,297+bob)});
            }
            var protect=new[]{new Rectangle(125,100+bob,188,140),new Rectangle(298,100+bob,137,139),new Rectangle(404,177+bob,81,80)};
            for(int y=0;y<512;y++)for(int x=0;x<512;x++)foreach(var r in protect)if(r.Contains(x,y)){
                mask.SetPixel(x,y,Color.Black);canvas.SetPixel(x,y,pilot.GetPixel(x,y-bob));break;
            }
            canvas.Save(guideFile,ImageFormat.Png);mask.Save(maskFile,ImageFormat.Png);
        }
    }
}
'@
New-Item -ItemType Directory -Path $soraOut | Out-Null
$soraFrames=@()
foreach($soraIndex in @(1,2)){
    $soraName='pose_{0:d2}' -f $soraIndex
    $soraFolder=Join-Path $soraOut $soraName
    New-Item -ItemType Directory -Path $soraFolder | Out-Null
    $soraSource=Join-Path $soraSources ('sora_run_loop_{0:d2}.png' -f $soraIndex)
    $soraBob=if($soraIndex -eq 1){3}else{1}
    [AdjacentRunGuide]::Paint($soraPilot,$soraOriginal,$soraSource,(Join-Path $soraFolder 'whole_pose_guide.png'),(Join-Path $soraFolder 'temporary_selection.png'),$soraIndex,$soraBob)
    $soraFrames += [ordered]@{index=$soraIndex;phase=if($soraIndex -eq 1){'compression after approved contact'}else{'early passing after compression'};source=$soraSource;sourceSha256=(Get-FileHash -LiteralPath $soraSource -Algorithm SHA256).Hash.ToLowerInvariant();bodyShiftY=$soraBob;guide="$soraName/whole_pose_guide.png";guideSha256=(Get-FileHash -LiteralPath (Join-Path $soraFolder 'whole_pose_guide.png') -Algorithm SHA256).Hash.ToLowerInvariant();mask="$soraName/temporary_selection.png";maskSha256=(Get-FileHash -LiteralPath (Join-Path $soraFolder 'temporary_selection.png') -Algorithm SHA256).Hash.ToLowerInvariant();protectedRectangles=@(@(125,(100+$soraBob),188,140),@(298,(100+$soraBob),137,139),@(404,(177+$soraBob),81,80))}
}
[ordered]@{status='Complete flat chronological guides; inspect before model submission';approvedAnchor=$soraPilot;approvedAnchorSha256=$soraChecks[0][1];originalWholePose=$soraOriginal;method='Whole source canvases and temporary selections on a single flat output; new articulated free arms; unchanged-resolution original01/02 leg drawings; whole upper carry integer bob';componentProductionLayers=$false;scaledPoseCopies=$false;frames=$soraFrames} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $soraOut 'provenance.json') -Encoding UTF8
Write-Output "Two complete flat guides saved in $Version; visual review required."
