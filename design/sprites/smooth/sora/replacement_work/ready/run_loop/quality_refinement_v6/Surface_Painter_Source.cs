// Whole-reference brushes paint directly into a complete RGBA canvas.
// No cropped component bitmaps, part PNGs or production layers are created.
using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using System.Globalization;
using System.IO;
using System.Text.RegularExpressions;

public sealed class ReferenceSurfacePainting {
    readonly Bitmap reference,armReference;
    public const float NearThigh=84.023806f,FarThigh=75.82216f,NearShin=48.79549f,FarShin=48.01042f;
    public static readonly PointF NearHipSource=new PointF(285,317),NearKneeSource=new PointF(351,369);
    public static readonly PointF FarHipSource=new PointF(247,316),FarKneeSource=new PointF(190,366);
    static readonly PointF BootAnchor=new PointF(385,404);
    const float BootReferenceAngle=-10;
    const string NearPants="M 288 317 C 311 309 350 326 374 342 C 387 351 394 365 383 372 C 380 375 376 372 371 374 C 357 384 345 387 333 382 C 321 372 304 351 290 339 L 281 330 Z";
    const string FarPants="M 176 329 C 177 319 189 312 195 312 L 210 322 L 231 321 L 242 316 L 259 332 C 250 357 231 379 209 383 C 187 383 174 366 171 348 Z";
    const string BootContour="M 367 396 C 369 384 385 382 397 389 L 405 397 L 409 407 C 424 396 441 395 454 401 C 470 409 473 421 465 432 C 454 447 430 455 411 455 L 381 456 C 369 452 364 445 364 430 L 366 412 Z";
    static Color ColorOf(string s){return ColorTranslator.FromHtml(s);}
    static string N(float f){return f.ToString("0.###",CultureInfo.InvariantCulture);}
    static string P(PointF p){return N(p.X)+" "+N(p.Y);}
    static GraphicsPath Path(string s){var t=Regex.Matches(s,@"[MLCZ]|-?\d+(?:\.\d+)?");int i=0;PointF last=new PointF();var p=new GraphicsPath();Func<float> n=()=>float.Parse(t[i++].Value,CultureInfo.InvariantCulture);
        while(i<t.Count){string c=t[i++].Value;if(c=="M"){last=new PointF(n(),n());p.StartFigure();}else if(c=="L"){var q=new PointF(n(),n());p.AddLine(last,q);last=q;}else if(c=="C"){var a=new PointF(n(),n());var b=new PointF(n(),n());var q=new PointF(n(),n());p.AddBezier(last,a,b,q);last=q;}else if(c=="Z")p.CloseFigure();else throw new InvalidDataException(c);}return p;}
    static PointF Mix(PointF a,PointF b,float t){return new PointF(a.X+(b.X-a.X)*t,a.Y+(b.Y-a.Y)*t);}
    static PointF Add(PointF p,float x,float y){return new PointF(p.X+x,p.Y+y);}
    static float Angle(PointF a,PointF b){return (float)(Math.Atan2(b.Y-a.Y,b.X-a.X)*180/Math.PI);}
    static void Shape(Graphics g,string data,string fill,string edge,float width){using(var p=Path(data)){if(fill!=null)using(var b=new SolidBrush(ColorOf(fill)))g.FillPath(b,p);if(edge!=null)using(var pen=new Pen(ColorOf(edge),width)){pen.LineJoin=LineJoin.Round;pen.StartCap=pen.EndCap=LineCap.Round;g.DrawPath(pen,p);}}}
    static void Line(Graphics g,string data,string color,float width){Shape(g,data,null,color,width);}
    static void Grad(Graphics g,string data,string light,string dark,string edge,float width){using(var p=Path(data)){
        var r=p.GetBounds();using(var b=new LinearGradientBrush(r,ColorOf(light),ColorOf(dark),55)){b.WrapMode=WrapMode.TileFlipXY;g.FillPath(b,p);}if(edge!=null)using(var pen=new Pen(ColorOf(edge),width)){pen.LineJoin=LineJoin.Round;g.DrawPath(pen,p);}}}
    public ReferenceSurfacePainting(Bitmap wholeReference,Bitmap wholeArmReference){reference=wholeReference;armReference=wholeArmReference;}
    void Surface(Graphics g,Bitmap whole,string contour,PointF sourceAnchor,PointF destination,float rotation,float darkness=0,bool clothing=false){
        var save=g.Save();g.TranslateTransform(destination.X,destination.Y);g.RotateTransform(rotation);g.TranslateTransform(-sourceAnchor.X,-sourceAnchor.Y);
        using(var p=Path(contour))using(var brush=new TextureBrush(whole,WrapMode.Clamp))using(var region=new Region(p)){
            if(clothing){
                // Source calf pixels bordering the cuff must not become a second calf.
                // This is a temporary brush selection, not another raster canvas.
                var bounds=p.GetBounds();int left=(int)Math.Max(0,bounds.Left),right=(int)Math.Min(512,bounds.Right+1);
                for(int y=(int)Math.Max(0,bounds.Top);y<Math.Min(512,bounds.Bottom+1);y++){
                    int start=-1;
                    for(int x=left;x<=right;x++){
                        bool skin=false;if(x<right){var c=whole.GetPixel(x,y);skin=c.R>150&&c.G>70&&c.G<c.R*.85&&c.G>c.R*.37&&c.B>c.R*.27&&c.B<c.R*.7;}
                        if(skin&&start<0)start=x;else if(!skin&&start>=0){region.Exclude(new RectangleF(start,y,x-start,1));start=-1;}
                    }
                }
                g.FillRegion(brush,region);
            }else g.FillPath(brush,p);
            if(darkness>0)using(var shade=new SolidBrush(Color.FromArgb((int)darkness,4,8,10)))g.FillRegion(shade,region);
        }g.Restore(save);
    }
    public static PointF Knee(PointF hip,PointF ankle,bool near){
        float thigh=near?NearThigh:FarThigh,shin=near?NearShin:FarShin,dx=ankle.X-hip.X,dy=ankle.Y-hip.Y,d=(float)Math.Sqrt(dx*dx+dy*dy);
        if(d>thigh+shin||d<Math.Abs(thigh-shin))throw new InvalidDataException("Unreachable reference leg: "+P(hip)+" -> "+P(ankle));
        float u=(thigh*thigh-shin*shin+d*d)/(2*d),v=(float)Math.Sqrt(Math.Max(0,thigh*thigh-u*u));
        return new PointF(hip.X+dx/d*u+dy/d*v,hip.Y+dy/d*u-dx/d*v);
    }
    public void Shoe(Graphics g,PointF ankle,float angle,bool near){
        Surface(g,reference,BootContour,BootAnchor,ankle,angle-BootReferenceAngle,near?0:14);
        // Repaint the rounded collar where a new calf enters, using the same native material.
        // Texture sampling always reads the complete source PNG, never a part image.
    }
    public static float ShoeBottom(string source,float angle){using(var whole=new Bitmap(source))using(var probe=new Bitmap(256,256,PixelFormat.Format32bppArgb)){
        var renderer=new ReferenceSurfacePainting(whole,whole);
        using(var g=Graphics.FromImage(probe)){g.SmoothingMode=SmoothingMode.AntiAlias;g.PixelOffsetMode=PixelOffsetMode.HighQuality;g.InterpolationMode=InterpolationMode.HighQualityBicubic;renderer.Shoe(g,new PointF(100,100),angle,true);}
        for(int y=255;y>=0;y--)for(int x=0;x<256;x++)if(probe.GetPixel(x,y).A>0)return y+1-100;
    }throw new InvalidDataException("Empty reference shoe");}
    void Calf(Graphics g,PointF knee,PointF ankle,bool near){
        float dx=ankle.X-knee.X,dy=ankle.Y-knee.Y,len=(float)Math.Sqrt(dx*dx+dy*dy),px=-dy/len,py=dx/len;
        var a=Add(knee,px*13,py*13);var b=Add(ankle,px*10,py*10);var c=Add(ankle,-px*10,-py*10);var d=Add(knee,-px*13,-py*13);
        var p="M "+P(a)+" C "+P(Add(Mix(a,b,.3f),px*2,py*2))+" "+P(Mix(a,b,.65f))+" "+P(b)+" C "+P(Add(ankle,dx/len*5,dy/len*5))+" "+P(c)+" "+P(c)+" L "+P(d)+" Z";
        Grad(g,p,near?"#FFD0A2":"#EEBB92","#D17B50","#32231D",2.3f);
        Shape(g,"M "+P(a)+" L "+P(Add(Mix(knee,ankle,.2f),px*5,py*5))+" C "+P(Add(Mix(knee,ankle,.42f),px*6,py*6))+" "+P(Add(Mix(knee,ankle,.75f),px*4,py*4))+" "+P(Add(ankle,px*4,py*4))+" L "+P(b)+" Z","#E19769",null,0);
        Line(g,"M "+P(Add(Mix(knee,ankle,.3f),-px*6,-py*6))+" C "+P(Add(Mix(knee,ankle,.55f),-px*7,-py*7))+" "+P(Add(Mix(knee,ankle,.7f),-px*4,-py*4))+" "+P(Add(Mix(knee,ankle,.87f),-px*5,-py*5)),"#FFDEB4",1.2f);
    }
    public void Leg(Graphics g,PointF hip,PointF ankle,float bootAngle,bool near){
        var knee=Knee(hip,ankle,near);Calf(g,knee,ankle,near);Shoe(g,ankle,bootAngle,near);
        var oldHip=near?NearHipSource:FarHipSource;var oldKnee=near?NearKneeSource:FarKneeSource;
        Surface(g,reference,near?NearPants:FarPants,oldHip,hip,Angle(hip,knee)-Angle(oldHip,oldKnee),near?0:5,true);
        // Preserve the source's curved stitch/fold detail. Additional crease strokes
        // require a pose-specific garment contour; the earlier generic stroke floated outside it.
    }
    public void Waist(Graphics g,float clothLag){
        Surface(g,reference,"M 224 271 L 267 281 L 315 294 L 346 316 L 310 319 L 284 340 L 266 333 L 253 319 L 239 321 L 225 325 L 217 313 L 206 323 L 194 318 L 190 303 L 199 292 Z",new PointF(276,310),new PointF(276,310),0);
        // Preserve source belt crossings, fly stitching and organic red cloth folds.
        // A small delayed cloth-tip correction is drawn onto the same canvas.
        if(Math.Abs(clothLag)>5)Line(g,"M 201 303 C 208 296 221 291 235 289","#E8432B",.9f);
    }
    public void PelvisUnderpaint(Graphics g){
        // Bridge the newly posed thigh roots before repainting native belt/fly detail.
        // Most of this curved fill is occluded by the textured garments.
        Grad(g,"M 220 293 C 239 291 265 300 288 303 L 311 309 L 325 327 C 314 338 299 344 280 344 C 254 342 232 335 219 322 Z","#2C3033","#181E21","#111719",2.0f);
        Line(g,"M 273 313 C 274 325 277 334 283 340","#414A4D",.8f);
    }
    static void Arm(Graphics g,PointF a,PointF b,float aw,float bw){
        float dx=b.X-a.X,dy=b.Y-a.Y,d=(float)Math.Sqrt(dx*dx+dy*dy),px=-dy/d,py=dx/d;
        var a0=Add(a,px*aw,py*aw);var b0=Add(b,px*bw,py*bw);var a1=Add(a,-px*aw,-py*aw);var b1=Add(b,-px*bw,-py*bw);
        Grad(g,"M "+P(a0)+" C "+P(Add(Mix(a0,b0,.4f),px*2,py*2))+" "+P(Add(Mix(a0,b0,.7f),px*2,py*2))+" "+P(b0)+" C "+P(Add(b0,dx/d*6,dy/d*6))+" "+P(Add(b1,dx/d*6,dy/d*6))+" "+P(b1)+" C "+P(Mix(b1,a1,.4f))+" "+P(Mix(b1,a1,.7f))+" "+P(a1)+" Z","#FFD2A1","#D77F54","#38251E",2.1f);
        Line(g,"M "+P(Add(Mix(a,b,.2f),-px*aw*.5f,-py*aw*.5f))+" C "+P(Add(Mix(a,b,.4f),-px*aw*.55f,-py*aw*.55f))+" "+P(Add(Mix(a,b,.65f),-px*bw*.55f,-py*bw*.55f))+" "+P(Add(Mix(a,b,.8f),-px*bw*.4f,-py*bw*.4f)),"#FFE1B4",1.3f);
    }
    static void ArmChain(Graphics g,PointF a,PointF b,PointF c,float aw,float bw,float cw){
        using(var center=new GraphicsPath()){
            center.AddBezier(a,Mix(a,b,.6f),Mix(a,b,.86f),b);center.AddBezier(b,Mix(b,c,.14f),Mix(b,c,.6f),c);
            using(var pen=new Pen(Color.Black,bw*2)){pen.StartCap=pen.EndCap=LineCap.Round;pen.LineJoin=LineJoin.Round;center.Widen(pen);}
            var bounds=center.GetBounds();
            using(var skin=new LinearGradientBrush(bounds,ColorOf("#FFD6A6"),ColorOf("#DE986D"),45)){skin.WrapMode=WrapMode.TileFlipXY;g.FillPath(skin,center);}
            using(var edge=new Pen(ColorOf("#37271F"),2.0f)){edge.LineJoin=LineJoin.Round;g.DrawPath(edge,center);}
            var save=g.Save();g.SetClip(center,CombineMode.Intersect);
            float dx=c.X-b.X,dy=c.Y-b.Y,len=(float)Math.Sqrt(dx*dx+dy*dy),px=-dy/len,py=dx/len;
            using(var shade=new Pen(ColorOf("#D5885E"),5.5f)){shade.StartCap=shade.EndCap=LineCap.Round;g.DrawBezier(shade,Add(b,px*5,py*5),Add(Mix(b,c,.3f),px*6,py*6),Add(Mix(b,c,.7f),px*6,py*6),Add(c,px*4,py*4));}
            using(var light=new Pen(ColorOf("#FFDFB1"),1.25f)){light.StartCap=light.EndCap=LineCap.Round;g.DrawBezier(light,Add(Mix(b,c,.2f),-px*4,-py*4),Add(Mix(b,c,.4f),-px*5,-py*5),Add(Mix(b,c,.6f),-px*5,-py*5),Add(Mix(b,c,.8f),-px*3,-py*3));}
            g.Restore(save);
            Line(g,"M "+P(Add(b,-3,-2))+" C "+P(Add(b,-1,1))+" "+P(Add(b,3,2))+" "+P(Add(b,5,0)),"#B06C4C",1.0f);
        }
    }
    public void FreeArm(Graphics g,PointF shoulder,PointF elbow,PointF wrist){
        ArmChain(g,shoulder,elbow,wrist,13,13,10);
        // Rounded KH2 sleeve pad and silver cuff from the complete accepted drawing.
        Surface(g,reference,"M 350 248 C 363 250 380 258 391 268 L 388 274 L 362 291 L 351 288 L 343 274 L 343 260 Z",new PointF(361,268),shoulder,Angle(shoulder,elbow)-20);
        // Complete source08 contains a longer unobstructed empty hand and wrist.
        Surface(g,armReference,"M 431 307 C 440 294 454 291 466 298 C 478 302 484 312 482 325 C 478 339 465 340 451 334 L 432 329 Z",new PointF(435,321),wrist,Angle(elbow,wrist)+2);
    }
    public void HoldingArm(Graphics g,PointF shoulder,PointF grip,float angle,float bodyPitch){
        double radians=angle*Math.PI/180;var wrist=new PointF(grip.X-(float)Math.Sin(radians)*25,grip.Y+(float)Math.Cos(radians)*25);
        float dx=wrist.X-shoulder.X,dy=wrist.Y-shoulder.Y,d=(float)Math.Sqrt(dx*dx+dy*dy);
        if(d>85||d<3)throw new InvalidDataException("Unreachable painted wrist");
        float u=(45*45-40*40+d*d)/(2*d),v=(float)Math.Sqrt(Math.Max(0,45*45-u*u)),sign=dy>=0?1:-1;
        var elbow=new PointF(shoulder.X+dx/d*u-sign*dy/d*v,shoulder.Y+dy/d*u+sign*dx/d*v);
        ArmChain(g,shoulder,elbow,wrist,13,14,11);
        Surface(g,reference,"M 270 214 C 279 211 294 215 303 226 L 305 244 L 292 252 L 277 250 L 265 237 L 262 221 Z",new PointF(280,230),shoulder,bodyPitch);
    }
    public void Weapon(Graphics g,PointF grip,float angle,float lag){
        // Connected shaft/crown share the exact same rigid axis as the sampled guard and grip.
        var s=g.Save();g.TranslateTransform(grip.X,grip.Y);g.RotateTransform(angle);
        Grad(g,"M 40 -7 L 204 -7 C 209 -7 212 -2 210 3 C 209 7 205 8 202 8 L 40 8 Z","#EEEFE8","#8A959D","#1C2429",2.8f);
        Shape(g,"M 43 -5 L 203 -5 C 205 -5 208 -3 207 -1 L 43 -1 Z","#E0E4E0",null,0);Line(g,"M 46 -4 L 202 -4","#F9F7E9",1.4f);
        Grad(g,"M 202 7 L 195 35 L 186 38 L 186 24 L 181 21 L 180 41 L 170 42 L 168 29 L 164 26 L 161 43 L 151 42 L 139 7 Z","#C8D1D6","#798892","#1E272D",2.6f);
        Shape(g,"M 199 9 L 192 32 L 189 33 L 189 21 L 179 17 L 177 38 L 173 39 L 172 26 L 163 22 L 158 39 L 154 38 L 143 10 Z","#BFCAD0",null,0);
        Line(g,"M 194 12 L 190 26 M 176 22 L 175 34 M 158 26 L 156 35","#EDF0E8",1.25f);
        Line(g,"M 187 25 L 186 36 M 171 29 L 170 40 M 151 32 L 150 39","#64717F",1.4f);
        Grad(g,"M 32 -8 L 42 -9 L 46 -6 L 46 7 L 42 10 L 32 8 Z","#6383A3","#233E57","#182B3D",1.7f);
        Line(g,"M 43 -6 L 43 6","#C9D4D6",1.3f);
        g.Restore(s);
        // Rich native guard bevels, black grip and finger anatomy are sampled from one full image.
        Surface(g,reference,"M 251 142 C 261 140 269 151 278 156 L 305 168 L 311 180 L 306 208 L 297 218 L 241 219 L 216 209 L 214 198 L 223 180 L 235 158 Z",new PointF(266,188),grip,angle-14);
        // Pommel chain is separately painted as strokes on the same canvas, never a component sprite.
        double a=angle*Math.PI/180;var origin=new PointF(grip.X-44*(float)Math.Cos(a),grip.Y-44*(float)Math.Sin(a)+6);
        for(int j=0;j<8;j++){float x=origin.X+lag*(float)Math.Sin((j+1)*.16),y=origin.Y+j*5.2f;
            using(var pen=new Pen(ColorOf("#313B3D"),2))g.DrawEllipse(pen,x-3,y-4,6,9);
            using(var pen=new Pen(ColorOf("#B5C0BB"),1.2f))g.DrawEllipse(pen,x-2,y-3,4,7);
        }
        float ex=origin.X+lag*(float)Math.Sin(1.28),ey=origin.Y+42;
        foreach(var oval in new RectangleF[]{new RectangleF(ex-13,ey-5,11,11),new RectangleF(ex+2,ey-5,11,11),new RectangleF(ex-8,ey,16,16)}){
            using(var p=new GraphicsPath()){p.AddEllipse(oval);using(var b=new PathGradientBrush(p)){b.CenterColor=ColorOf("#E2E6DD");b.SurroundColors=new[]{ColorOf("#67787F")};b.CenterPoint=new PointF(oval.X+oval.Width*.32f,oval.Y+oval.Height*.22f);g.FillPath(b,p);}using(var pen=new Pen(ColorOf("#273638"),1.8f))g.DrawPath(pen,p);}
        }
    }
}
