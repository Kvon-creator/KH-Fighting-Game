param([ValidateSet('reference_v3','reference_v4','reference_v5')][string]$Version='reference_v3',[ValidateSet('reference_v2','reference_v4','reference_v5')][string]$SelectionVersion='reference_v2')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraTrial=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready/run_loop/comfyui_trial'
$soraOriginal=Join-Path $soraTrial 'reference_v1/whole_pose_00_white.png'
$soraSelection=Join-Path $soraTrial "$SelectionVersion/temporary_selection.png"
if((Get-FileHash -LiteralPath $soraOriginal -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'a3681849fa6b2a235fd36622866057191f0d073d39ea9cff8b7e30764f6d9022'){throw 'Original whole pose changed'}
$soraFolder=Join-Path $soraTrial $Version
if(Test-Path -LiteralPath (Join-Path $soraFolder 'whole_pose_backward_arm_guide.png')){throw 'Preserve existing flat guide'}
New-Item -ItemType Directory -Force -Path $soraFolder | Out-Null
Add-Type -AssemblyName System.Drawing
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
public static class SoraFlatArmGuide {
    static Color C(string hex){return ColorTranslator.FromHtml(hex);}
    static void Fill(Graphics g,GraphicsPath p,string color,float outline){using(var b=new SolidBrush(C(color)))g.FillPath(b,p);if(outline>0)using(var pen=new Pen(C("#241D18"),outline)){pen.LineJoin=LineJoin.Round;g.DrawPath(pen,p);}}
    public static int Paint(string source,string selection,string target){
        using(var a=new Bitmap(source))using(var m=new Bitmap(selection))using(var b=new Bitmap(512,512,PixelFormat.Format24bppRgb)){
            using(var g=Graphics.FromImage(b)){
                g.DrawImageUnscaled(a,0,0);g.SmoothingMode=SmoothingMode.AntiAlias;
                using(var erase=new GraphicsPath()){
                    erase.AddPolygon(new[]{new PointF(346,242),new PointF(397,239),new PointF(489,249),new PointF(499,337),new PointF(430,340),new PointF(347,306),new PointF(335,277)});
                    Fill(g,erase,"#FFFFFF",0);
                }
                using(var sleeve=new GraphicsPath()){
                    sleeve.AddBezier(354,242,334,239,314,246,308,257);
                    sleeve.AddBezier(308,257,304,263,306,270,317,276);
                    sleeve.AddBezier(317,276,333,278,346,269,352,258);
                    sleeve.AddBezier(352,258,359,251,359,246,354,242);sleeve.CloseFigure();Fill(g,sleeve,"#242D32",2.4f);
                }
                using(var shade=new GraphicsPath()){
                    shade.AddPolygon(new[]{new PointF(336,244),new PointF(321,249),new PointF(315,260),new PointF(326,264),new PointF(341,258)});Fill(g,shade,"#414B50",0);
                }
                using(var skin=new GraphicsPath()){
                    skin.AddBezier(314,265,305,261,294,263,288,270);
                    skin.AddBezier(288,270,283,276,287,281,289,287);
                    skin.AddBezier(289,287,290,294,292,299,295,304);
                    skin.AddBezier(295,304,298,307,305,304,305,298);
                    skin.AddBezier(305,298,307,287,300,280,307,275);
                    skin.AddBezier(307,275,313,273,317,269,314,265);skin.CloseFigure();Fill(g,skin,"#F6B173",2.4f);
                }
                using(var shadow=new GraphicsPath()){
                    shadow.AddPolygon(new[]{new PointF(288,274),new PointF(292,281),new PointF(297,301),new PointF(304,298),new PointF(301,284),new PointF(295,274)});Fill(g,shadow,"#D68A50",0);
                }
                using(var highlight=new Pen(C("#FFCEA0"),2.2f)){highlight.StartCap=LineCap.Round;highlight.EndCap=LineCap.Round;g.DrawBezier(highlight,294,269,302,268,307,268,310,267);g.DrawLine(highlight,291,280,295,289);}
                using(var hem=new Pen(C("#ECECE6"),3.8f)){g.DrawBezier(hem,307,262,309,268,314,272,319,272);}
                using(var band=new GraphicsPath()){
                    band.AddPolygon(new[]{new PointF(291,295),new PointF(305,294),new PointF(311,303),new PointF(297,308)});Fill(g,band,"#202427",1.8f);
                }
                using(var yellow=new Pen(C("#DAA21C"),2.3f)){g.DrawLine(yellow,293,298,306,298);}
                using(var fist=new GraphicsPath()){
                    fist.AddBezier(299,302,293,302,286,307,287,313);
                    fist.AddBezier(287,313,287,319,298,324,306,321);
                    fist.AddBezier(306,321,313,319,315,310,311,305);
                    fist.AddBezier(311,305,307,301,303,301,299,302);fist.CloseFigure();Fill(g,fist,"#262B2D",2.2f);
                }
                using(var fingers=new GraphicsPath()){
                    fingers.AddBezier(291,309,291,307,298,309,304,310);
                    fingers.AddBezier(304,310,308,311,309,314,305,317);
                    fingers.AddBezier(305,317,300,320,294,318,291,315);fingers.CloseFigure();Fill(g,fingers,"#F6B173",1.3f);
                }
                using(var seams=new Pen(C("#704525"),1.0f)){g.DrawLine(seams,296,310,295,316);g.DrawLine(seams,300,311,300,317);g.DrawLine(seams,304,311,304,316);}
                using(var thumb=new GraphicsPath()){
                    thumb.AddBezier(308,305,312,306,314,309,311,312);
                    thumb.AddBezier(311,312,308,315,301,313,300,309);
                    thumb.AddBezier(300,309,301,306,304,307,308,305);thumb.CloseFigure();Fill(g,thumb,"#FFC08A",1.4f);
                }
            }
            int changed=0;
            // Keep the guide as one full canvas, respecting its temporary selection.
            for(int y=0;y<512;y++)for(int x=0;x<512;x++){
                if(m.GetPixel(x,y).R==0)b.SetPixel(x,y,a.GetPixel(x,y));
                if(b.GetPixel(x,y).ToArgb()!=a.GetPixel(x,y).ToArgb())changed++;
            }
            b.Save(target,ImageFormat.Png);return changed;
        }
    }
}
'@
$soraTarget=Join-Path $soraFolder 'whole_pose_backward_arm_guide.png'
$soraChanged=[SoraFlatArmGuide]::Paint($soraOriginal,$soraSelection,$soraTarget)
[ordered]@{role='One complete flat pose guide with genuinely redrawn sleeve, backward elbow, forearm and closed empty fist';originalWholePoseSha256='a3681849fa6b2a235fd36622866057191f0d073d39ea9cff8b7e30764f6d9022';guideSha256=(Get-FileHash -LiteralPath $soraTarget -Algorithm SHA256).Hash.ToLowerInvariant();selection=$soraSelection;changedPixels=$soraChanged;outsideSelectionRestoredFromOriginal=$true;componentProductionLayers=$false;status='Pose guide only; inspect before AI finish or artwork approval'} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $soraFolder 'guide_provenance.json') -Encoding UTF8
Write-Output "Complete flat guide saved; $soraChanged pixels redrawn within selection."
