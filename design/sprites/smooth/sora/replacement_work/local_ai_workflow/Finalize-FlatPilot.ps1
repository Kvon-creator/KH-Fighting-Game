param([ValidatePattern('^attempt_[0-9]{2,}$')][string]$Attempt='attempt_03')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraTrial=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready/run_loop/comfyui_trial'
$soraOut=Join-Path $soraTrial $Attempt
$soraReceipt=Get-Content -LiteralPath (Join-Path $soraOut 'receipt.json') -Raw | ConvertFrom-Json
$soraNative=Join-Path $soraOut 'candidate_00.png'
$soraOriginal=Join-Path $soraTrial 'reference_v1/whole_pose_00_white.png'
$soraMask=[System.IO.Path]::GetFullPath((Join-Path $soraRoot $soraReceipt.mask))
if(-not $soraMask.StartsWith($soraRoot+'\',[System.StringComparison]::OrdinalIgnoreCase)){throw 'Selection escaped workspace'}
foreach($soraCheck in @(@($soraNative,$soraReceipt.files[0].sha256),@($soraOriginal,'a3681849fa6b2a235fd36622866057191f0d073d39ea9cff8b7e30764f6d9022'),@($soraMask,$soraReceipt.maskSha256))){if((Get-FileHash -LiteralPath $soraCheck[0] -Algorithm SHA256).Hash.ToLowerInvariant() -ne $soraCheck[1]){throw 'Native/source/selection hash changed'}}
$soraTarget=Join-Path $soraOut 'final_pose_v1.png'
if(Test-Path -LiteralPath $soraTarget){throw 'Preserve previous flat refinement'}
Add-Type -AssemblyName System.Drawing
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
public static class SoraFlatFinish {
    static Color C(string h){return ColorTranslator.FromHtml(h);}
    static void Fill(Graphics g,GraphicsPath p,string color,float width){using(var b=new SolidBrush(C(color)))g.FillPath(b,p);if(width>0)using(var pen=new Pen(C("#251D17"),width)){pen.LineJoin=LineJoin.Round;g.DrawPath(pen,p);}}
    public static void Paint(string native,string original,string selection,string target){
        using(var n=new Bitmap(native))using(var a=new Bitmap(original))using(var m=new Bitmap(selection))using(var b=new Bitmap(512,512,PixelFormat.Format24bppRgb)){
            using(var g=Graphics.FromImage(b)){
                g.DrawImageUnscaled(n,0,0);g.SmoothingMode=SmoothingMode.AntiAlias;
                // Refine the closed empty fist directly on this single complete canvas.
                using(var cuff=new GraphicsPath()){
                    cuff.AddPolygon(new[]{new PointF(291,295),new PointF(305,295),new PointF(310,303),new PointF(296,308)});Fill(g,cuff,"#24282A",1.8f);
                }
                using(var gold=new Pen(C("#D8A11A"),2.1f)){g.DrawLine(gold,293,298,305,299);}
                using(var fist=new GraphicsPath()){
                    fist.AddBezier(296,303,290,304,286,308,287,315);
                    fist.AddBezier(287,315,287,321,299,327,306,323);
                    fist.AddBezier(306,323,313,320,315,311,311,306);
                    fist.AddBezier(311,306,307,302,301,302,296,303);fist.CloseFigure();Fill(g,fist,"#242A2B",2.0f);
                }
                using(var shade=new GraphicsPath()){
                    shade.AddPolygon(new[]{new PointF(289,311),new PointF(291,320),new PointF(301,323),new PointF(307,320),new PointF(299,315)});Fill(g,shade,"#141A1C",0);
                }
                using(var fingers=new GraphicsPath()){
                    fingers.AddBezier(291,310,294,309,300,310,305,312);
                    fingers.AddBezier(305,312,309,313,308,316,304,319);
                    fingers.AddBezier(304,319,299,321,293,319,291,316);fingers.CloseFigure();Fill(g,fingers,"#F6B376",1.25f);
                }
                using(var light=new Pen(C("#FFD3A5"),1.4f)){g.DrawBezier(light,292,312,296,311,301,312,305,314);}
                using(var seams=new Pen(C("#764627"),1.0f)){g.DrawLine(seams,296,312,295,318);g.DrawLine(seams,300,312,300,319);g.DrawLine(seams,304,313,304,318);}
                using(var thumb=new GraphicsPath()){
                    thumb.AddBezier(308,306,312,307,314,310,311,313);
                    thumb.AddBezier(311,313,308,316,302,314,300,311);
                    thumb.AddBezier(300,311,300,307,304,308,308,306);thumb.CloseFigure();Fill(g,thumb,"#FFBF87",1.35f);
                }
                using(var stitch=new Pen(C("#586167"),0.8f)){g.DrawBezier(stitch,289,307,289,302,294,302,296,304);}
                using(var rivet=new SolidBrush(C("#818A8E"))){g.FillEllipse(rivet,301,303,2.1f,2.1f);g.FillEllipse(rivet,320,247,2.0f,2.0f);}
            }
            var protectedRects=new[]{new Rectangle(125,100,188,140),new Rectangle(298,100,137,139),new Rectangle(404,177,81,80)};
            for(int y=0;y<512;y++)for(int x=0;x<512;x++){
                bool keep=m.GetPixel(x,y).R==0;
                foreach(var r in protectedRects)if(r.Contains(x,y)){keep=true;break;}
                if(keep)b.SetPixel(x,y,a.GetPixel(x,y));
            }
            b.Save(target,ImageFormat.Png);
        }
    }
}
'@
[SoraFlatFinish]::Paint($soraNative,$soraOriginal,$soraMask,$soraTarget)
[ordered]@{file='final_pose_v1.png';sha256=(Get-FileHash -LiteralPath $soraTarget -Algorithm SHA256).Hash.ToLowerInvariant();sourceNativeSha256=$soraReceipt.files[0].sha256;protectedReference='design/sprites/smooth/sora/replacement_work/ready/run_loop/comfyui_trial/reference_v1/whole_pose_00_white.png';protectedReferenceSha256='a3681849fa6b2a235fd36622866057191f0d073d39ea9cff8b7e30764f6d9022';method='Direct empty-fist painting and hard source-pixel protection on one complete flat canvas; native model output preserved';componentProductionLayers=$false;finalUserApproval='pending'} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $soraOut 'refinement_manifest.json') -Encoding UTF8
Write-Output 'Complete flat refinement saved; native image preserved. Run final QA and visual review.'
