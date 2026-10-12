// New leg joints on one complete RGBA canvas. All texture brushes read complete
// source images. Paths and pixel selections are temporary; no part bitmaps/layers.
using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using System.Globalization;
using System.Text.RegularExpressions;

public static class GeneratedGaitPainting {
    public const float NearThigh=83,NearShin=47,FarThigh=65,FarShin=45;
    static readonly PointF NearSourceHip=new PointF(272,316),NearSourceKnee=new PointF(223,382);
    static readonly PointF FarSourceHip=new PointF(291,325),FarSourceKnee=new PointF(324,374);
    static readonly PointF ShoeSourceAnkle=new PointF(327,391);
    const string NearPants="M 216 309 C 229 306 248 302 260 307 L 275 319 C 282 342 277 368 258 382 C 242 395 217 397 199 386 C 183 377 172 358 176 338 C 178 325 196 314 216 309 Z";
    const string FarPants="M 276 318 C 286 310 301 307 314 314 C 333 320 347 330 356 342 C 366 352 365 369 351 377 C 333 388 309 389 288 378 C 276 371 268 356 268 341 Z";
    const string Shoe="M 314 377 C 325 373 338 374 347 381 C 354 387 355 395 353 403 C 370 395 391 400 403 410 C 416 422 419 440 410 451 C 396 464 370 467 339 463 C 316 463 291 458 286 445 C 283 431 290 411 306 402 L 308 389 Z";
    const string Waist="M 202 267 L 237 271 L 267 274 L 289 282 L 325 305 L 310 324 L 295 335 L 272 332 L 260 320 L 244 322 L 225 328 L 199 325 L 175 315 L 191 298 Z";
    static string N(float f){return f.ToString("0.###",CultureInfo.InvariantCulture);}
    static string P(PointF p){return N(p.X)+" "+N(p.Y);}
    static PointF Add(PointF p,float x,float y){return new PointF(p.X+x,p.Y+y);}
    static PointF Mix(PointF a,PointF b,float t){return new PointF(a.X+(b.X-a.X)*t,a.Y+(b.Y-a.Y)*t);}
    static float Angle(PointF a,PointF b){return (float)(Math.Atan2(b.Y-a.Y,b.X-a.X)*180/Math.PI);}
    static GraphicsPath Path(string data){
        var t=Regex.Matches(data,@"[MLCZ]|-?\d+(?:\.\d+)?");int i=0;var p=new GraphicsPath();PointF last=new PointF();
        Func<float> n=()=>float.Parse(t[i++].Value,CultureInfo.InvariantCulture);
        while(i<t.Count){string c=t[i++].Value;
            if(c=="M"){last=new PointF(n(),n());p.StartFigure();}
            else if(c=="L"){var q=new PointF(n(),n());p.AddLine(last,q);last=q;}
            else if(c=="C"){var a=new PointF(n(),n());var b=new PointF(n(),n());var q=new PointF(n(),n());p.AddBezier(last,a,b,q);last=q;}
            else if(c=="Z")p.CloseFigure();
        }return p;
    }
    static bool SkinPixel(Color c){return c.R>160&&c.G>c.R*.45&&c.G<c.R*.85&&c.B>c.R*.32&&c.B<c.R*.7;}
    static bool OtherMaterial(Color c){return SkinPixel(c)||(c.R>45&&c.R>c.G*1.35&&c.R>c.B*1.35)||(c.R>130&&c.G>80&&c.G>c.R*.45&&c.B<c.R*.4);}
    static void Surface(Graphics g,Bitmap whole,string contour,PointF anchor,PointF target,float rotation,bool excludeSkin){
        var state=g.Save();g.TranslateTransform(target.X,target.Y);g.RotateTransform(rotation);g.TranslateTransform(-anchor.X,-anchor.Y);
        using(var p=Path(contour))using(var region=new Region(p))using(var brush=new TextureBrush(whole,WrapMode.Clamp)){
            if(excludeSkin){var bounds=p.GetBounds();int left=(int)Math.Max(0,bounds.Left),right=(int)Math.Min(511,bounds.Right+1);
                for(int y=(int)Math.Max(0,bounds.Top);y<Math.Min(512,bounds.Bottom+1);y++){
                    int start=-1;for(int x=left;x<=right;x++){
                        bool skin=x<right&&SkinPixel(whole.GetPixel(x,y));
                        if(skin&&start<0)start=x;else if(!skin&&start>=0){region.Exclude(new Rectangle(start,y,x-start,1));start=-1;}
                    }
                }
            }g.FillRegion(brush,region);
        }g.Restore(state);
    }
    public static PointF Knee(PointF hip,PointF ankle,bool near){
        float thigh=near?NearThigh:FarThigh,shin=near?NearShin:FarShin;
        float dx=ankle.X-hip.X,dy=ankle.Y-hip.Y,d=(float)Math.Sqrt(dx*dx+dy*dy);
        if(d>=thigh+shin||d<=Math.Abs(thigh-shin))throw new InvalidOperationException("Unreachable new leg");
        float along=(thigh*thigh-shin*shin+d*d)/(2*d),side=(float)Math.Sqrt(thigh*thigh-along*along);
        return new PointF(hip.X+dx/d*along+dy/d*side,hip.Y+dy/d*along-dx/d*side);
    }
    public static float SoleOffset(string wholeShoeFile,float angle){
        using(var whole=new Bitmap(wholeShoeFile))using(var p=Path(Shoe)){
            double r=angle*Math.PI/180;float bottom=float.MinValue;
            for(int y=370;y<475;y++)for(int x=280;x<430;x++){
                // Register the visible solid sole, excluding faint native edge/shadow alpha.
                var c=whole.GetPixel(x,y);if(c.A<=100||SkinPixel(c)||!p.IsVisible(x+.5f,y+.5f))continue;
                float projected=(float)((x-ShoeSourceAnkle.X)*Math.Sin(r)+(y-ShoeSourceAnkle.Y)*Math.Cos(r));bottom=Math.Max(bottom,projected+1);
            }return bottom;
        }
    }
    static void Calf(Graphics g,PointF knee,PointF ankle,bool near){
        float dx=ankle.X-knee.X,dy=ankle.Y-knee.Y,length=(float)Math.Sqrt(dx*dx+dy*dy),px=-dy/length,py=dx/length;
        float kw=near?14:12,aw=near?10:9;
        var a=Add(knee,px*kw,py*kw);var b=Add(ankle,px*aw,py*aw);var c=Add(ankle,-px*aw,-py*aw);var d=Add(knee,-px*kw,-py*kw);
        using(var p=Path("M "+P(a)+" C "+P(Mix(a,b,.3f))+" "+P(Mix(a,b,.7f))+" "+P(b)+" C "+P(Add(b,dx/length*6,dy/length*6))+" "+P(Add(c,dx/length*6,dy/length*6))+" "+P(c)+" C "+P(Mix(c,d,.4f))+" "+P(Mix(c,d,.8f))+" "+P(d)+" Z")){
            using(var brush=new LinearGradientBrush(p.GetBounds(),Color.FromArgb(255,209,160),Color.FromArgb(208,124,80),50))g.FillPath(brush,p);
            using(var pen=new Pen(Color.FromArgb(53,34,27),2.3f)){pen.LineJoin=LineJoin.Round;g.DrawPath(pen,p);}
        }
        using(var light=new Pen(Color.FromArgb(255,223,182),1.6f)){light.StartCap=light.EndCap=LineCap.Round;
            g.DrawLine(light,Add(Mix(knee,ankle,.22f),-px*5,-py*5),Add(Mix(knee,ankle,.82f),-px*5,-py*5));}
    }
    static void Leg(Graphics g,Bitmap clothes,Bitmap boots,PointF hip,PointF ankle,float shoeAngle,bool near){
        var knee=Knee(hip,ankle,near);Calf(g,knee,ankle,near);
        Surface(g,boots,Shoe,ShoeSourceAnkle,ankle,shoeAngle,true);
        var oldHip=near?NearSourceHip:FarSourceHip;var oldKnee=near?NearSourceKnee:FarSourceKnee;
        Pants(g,clothes,near?NearPants:FarPants,oldHip,hip,knee,Angle(hip,knee)-Angle(oldHip,oldKnee),near);
    }
    static void Pants(Graphics g,Bitmap whole,string sourceContour,PointF oldHip,PointF hip,PointF knee,float rotation,bool near){
        float dx=knee.X-hip.X,dy=knee.Y-hip.Y,d=(float)Math.Sqrt(dx*dx+dy*dy),ux=dx/d,uy=dy/d,px=-uy,py=ux;
        float rw=near?33:27,kw=near?28:24;
        var a=Add(hip,px*rw-ux*6,py*rw-uy*6);var b=Add(knee,px*kw,py*kw);
        var c=Add(knee,-px*kw,-py*kw);var e=Add(hip,-px*rw-ux*8,-py*rw-uy*8);
        string garment;
        if(near){
            var root=Add(hip,-8,-18);var round=Add(hip,7,38);
            garment="M "+P(root)+" C "+P(Add(hip,-26,-14))+" "+P(Add(hip,-41,2))+" "+P(Add(hip,-38,22))+" C "+P(Add(hip,-32,35))+" "+P(Add(hip,-13,41))+" "+P(round)+" C "+P(Add(hip,24,44))+" "+P(Add(Mix(round,b,.75f),px*5,py*5))+" "+P(b)+" C "+P(Add(b,ux*13,uy*13))+" "+P(Add(c,ux*13,uy*13))+" "+P(c)+" C "+P(Add(Mix(c,root,.3f),-px*6,-py*6))+" "+P(Add(Mix(c,root,.7f),-px*5,-py*5))+" "+P(root)+" Z";
        }else garment="M "+P(a)+" C "+P(Add(Mix(a,b,.3f),px*7,py*7))+" "+P(Add(Mix(a,b,.72f),px*8,py*8))+" "+P(b)+" C "+P(Add(b,ux*13,uy*13))+" "+P(Add(c,ux*13,uy*13))+" "+P(c)+" C "+P(Add(Mix(c,e,.35f),-px*6,-py*6))+" "+P(Add(Mix(c,e,.75f),-px*3,-py*3))+" "+P(e)+" C "+P(Add(hip,-ux*15,-uy*15))+" "+P(a)+" "+P(a)+" Z";
        using(var destination=Path(garment)){
            using(var fill=new LinearGradientBrush(destination.GetBounds(),Color.FromArgb(46,49,51),Color.FromArgb(23,28,31),65))g.FillPath(fill,destination);
            var state=g.Save();g.TranslateTransform(hip.X,hip.Y);g.RotateTransform(rotation);g.TranslateTransform(-oldHip.X,-oldHip.Y);
            using(var inverse=g.Transform){inverse.Invert();using(var sourceClip=(GraphicsPath)destination.Clone())using(var p=Path(sourceContour))using(var region=new Region(p))using(var brush=new TextureBrush(whole,WrapMode.Clamp)){
                sourceClip.Transform(inverse);region.Intersect(sourceClip);
                var bounds=p.GetBounds();int left=(int)Math.Max(0,bounds.Left),right=(int)Math.Min(511,bounds.Right+1);
                for(int y=(int)Math.Max(0,bounds.Top);y<Math.Min(512,bounds.Bottom+1);y++){
                    int start=-1;for(int x=left;x<=right;x++){
                        bool other=x<right&&OtherMaterial(whole.GetPixel(x,y));
                        if(other&&start<0)start=x;else if(!other&&start>=0){region.Exclude(new Rectangle(start,y,x-start,1));start=-1;}
                    }
                }g.FillRegion(brush,region);
            }}g.Restore(state);
            using(var outline=new Pen(Color.FromArgb(25,29,31),2.4f)){outline.LineJoin=LineJoin.Round;g.DrawPath(outline,destination);}
            var sb=Add(knee,px*(kw-5)-ux*5,py*(kw-5)-uy*5);var sc=Add(knee,-px*(kw-5)-ux*5,-py*(kw-5)-uy*5);
            using(var stitch=new Pen(Color.FromArgb(144,150,151),1.1f))g.DrawBezier(stitch,sb,Add(sb,ux*8,uy*8),Add(sc,ux*8,uy*8),sc);
        }
    }
    public static PointF[] Paint(string bodyFile,string clothesFile,string bootsFile,string outputFile,int bodyShift,PointF nearAnkle,float nearShoeAngle,PointF farAnkle,float farShoeAngle){
        using(var body=new Bitmap(bodyFile))using(var clothes=new Bitmap(clothesFile))using(var boots=new Bitmap(bootsFile))using(var output=body.Clone(new Rectangle(0,0,512,512),PixelFormat.Format32bppArgb)){
            int split=312+bodyShift;var nearHip=new PointF(272,316+bodyShift);var farHip=new PointF(291,325+bodyShift);
            var nearKnee=Knee(nearHip,nearAnkle,true);var farKnee=Knee(farHip,farAnkle,false);
            for(int y=0;y<512;y++)for(int x=0;x<512;x++)output.SetPixel(x,y,y<split&&y-bodyShift>=0?body.GetPixel(x,y-bodyShift):Color.Transparent);
            using(var g=Graphics.FromImage(output)){
                g.SmoothingMode=SmoothingMode.AntiAlias;g.PixelOffsetMode=PixelOffsetMode.HighQuality;g.InterpolationMode=InterpolationMode.HighQualityBicubic;
                Leg(g,clothes,boots,farHip,farAnkle,farShoeAngle,false);
                Leg(g,clothes,boots,nearHip,nearAnkle,nearShoeAngle,true);
                Surface(g,body,Waist,NearSourceHip,nearHip,0,false);
                Surface(g,body,"M 323 224 L 378 224 L 388 310 L 336 310 Z",NearSourceHip,nearHip,0,false);
            }
            // Preserve every upper-body pixel after its whole-figure integer bob.
            for(int y=0;y<270+bodyShift;y++)for(int x=0;x<512;x++)output.SetPixel(x,y,y-bodyShift>=0?body.GetPixel(x,y-bodyShift):Color.Transparent);
            output.Save(outputFile,ImageFormat.Png);
            return new PointF[]{nearHip,nearKnee,nearAnkle,farHip,farKnee,farAnkle};
        }
    }
}
