// Paint only complete canvases. Reference brushes always read whole source PNGs;
// selections are temporary paths, never cropped raster parts or production layers.
using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using System.Globalization;
using System.Text.RegularExpressions;

public static class GeneratedFlatRefinement {
    static GraphicsPath Path(string data) {
        var tokens=Regex.Matches(data,@"[MLCZ]|-?\d+(?:\.\d+)?");int i=0;
        var p=new GraphicsPath();PointF last=new PointF();
        Func<float> number=()=>float.Parse(tokens[i++].Value,CultureInfo.InvariantCulture);
        while(i<tokens.Count){string c=tokens[i++].Value;
            if(c=="M"){last=new PointF(number(),number());p.StartFigure();}
            else if(c=="L"){var q=new PointF(number(),number());p.AddLine(last,q);last=q;}
            else if(c=="C"){var a=new PointF(number(),number());var b=new PointF(number(),number());var q=new PointF(number(),number());p.AddBezier(last,a,b,q);last=q;}
            else if(c=="Z")p.CloseFigure();
        }return p;
    }
    static PointF Along(PointF p,float length,float degrees){double a=degrees*Math.PI/180;return new PointF(p.X+length*(float)Math.Cos(a),p.Y+length*(float)Math.Sin(a));}
    static void Brush(Graphics g,Bitmap whole,string contour,PointF origin,PointF destination,float rotation) {
        var state=g.Save();g.TranslateTransform(destination.X,destination.Y);g.RotateTransform(rotation);g.TranslateTransform(-origin.X,-origin.Y);
        using(var path=Path(contour))using(var brush=new TextureBrush(whole,WrapMode.Clamp))g.FillPath(brush,path);
        g.Restore(state);
    }
    static void Clear(Graphics g,string contour,float yOffset) {
        var state=g.Save();g.TranslateTransform(0,yOffset);g.CompositingMode=CompositingMode.SourceCopy;
        using(var p=Path(contour))using(var b=new SolidBrush(Color.Transparent))g.FillPath(b,p);
        g.Restore(state);
    }
    static float EyeY(Bitmap image){
        double sum=0;int count=0;
        for(int y=130;y<225;y++)for(int x=370;x<403;x++){
            var c=image.GetPixel(x,y);
            if(c.A>100&&c.R<160&&c.G>65&&c.B>100&&c.B>c.G*1.05&&c.B>c.R*1.15){sum+=y;count++;}
        }
        if(count<2)throw new InvalidOperationException("Inspect blue-eye registration before painting");
        return (float)(sum/count);
    }
    static void Skin(Graphics g,PointF shoulder,PointF elbow,PointF wrist){
        using(var path=new GraphicsPath()){
            path.AddLine(shoulder,elbow);path.AddLine(elbow,wrist);
            using(var edge=new Pen(Color.FromArgb(49,33,25),25)){edge.LineJoin=LineJoin.Round;edge.StartCap=edge.EndCap=LineCap.Round;g.DrawPath(edge,path);}
            using(var skin=new Pen(Color.FromArgb(247,181,127),21)){skin.LineJoin=LineJoin.Round;skin.StartCap=skin.EndCap=LineCap.Round;g.DrawPath(skin,path);}
        }
    }
    const string Sleeve="M 345 240 C 350 232 360 228 370 234 C 380 240 387 250 394 260 L 388 269 C 382 273 374 278 367 276 L 354 268 C 346 259 341 249 345 240 Z";
    const string Upper="M 370 269 C 376 264 381 267 387 274 L 397 281 L 394 295 C 385 292 376 287 370 281 L 364 275 Z";
    const string Forearm="M 384 272 C 396 273 405 274 415 270 C 422 266 429 267 433 270 C 448 263 462 267 471 279 C 480 294 475 306 463 312 C 449 313 431 307 420 301 C 407 300 393 297 383 289 Z";
    const string OldArm="M 343 237 C 347 229 364 226 379 238 L 404 261 L 422 260 C 447 254 473 261 483 277 C 493 295 484 317 466 322 C 447 323 428 312 414 308 C 394 307 376 295 364 282 L 350 271 C 343 260 339 246 343 237 Z";
    const string Carry="M 128 183 C 129 171 139 162 154 153 L 186 130 L 199 132 L 207 119 L 218 108 L 233 106 L 247 118 L 276 132 L 287 147 L 284 160 L 318 171 L 351 174 L 403 188 L 476 201 L 482 211 L 465 257 L 452 259 L 442 241 L 431 246 L 420 233 L 403 231 L 405 212 L 320 191 L 278 188 L 264 211 L 248 236 L 222 237 L 197 227 L 195 210 L 198 190 L 183 180 L 168 187 L 152 199 L 135 196 Z";
    const string Torso="M 235 175 L 324 175 L 335 216 L 344 232 L 350 250 L 346 264 L 325 282 L 312 294 L 284 301 L 259 304 L 239 297 L 209 308 L 176 306 L 190 287 L 212 266 L 231 244 L 228 224 Z";
    const string Head="M 291 166 L 313 160 L 304 148 L 325 143 L 314 126 L 337 131 L 326 116 L 350 123 L 354 106 L 373 126 L 381 111 L 396 132 L 432 139 L 416 151 L 438 161 L 424 172 L 437 181 L 418 190 L 407 203 L 394 223 L 374 239 L 357 232 L 345 231 L 337 242 L 329 229 L 321 226 L 326 208 L 315 206 L 320 196 L 304 188 L 312 180 L 291 166 Z";
    static void JacketJoin(Graphics g,float shift){
        var state=g.Save();g.TranslateTransform(0,shift);
        using(var p=Path("M 337 230 C 347 227 359 233 370 240 L 365 256 C 353 261 343 267 330 267 L 326 253 Z")){
            using(var b=new LinearGradientBrush(new Rectangle(326,227,45,41),Color.FromArgb(56,61,64),Color.FromArgb(26,31,34),65))g.FillPath(b,p);
            using(var edge=new Pen(Color.FromArgb(28,31,34),2))g.DrawPath(edge,p);
        }
        g.Restore(state);
    }
    static void NativeCollar(Graphics g,Bitmap whole,float shift){
        using(var p=Path("M 325 202 L 350 215 L 366 220 L 375 227 L 359 240 L 349 248 L 336 242 L 329 229 Z"))
        using(var matrix=new Matrix())using(var brush=new TextureBrush(whole,WrapMode.Clamp)){
            matrix.Translate(0,shift);p.Transform(matrix);g.FillPath(brush,p);
        }
    }
    static void RestoreHead(Bitmap output,Bitmap original,float eyeY) {
        // Copy native hair/face pixels exactly. The brown/skin seed and small dilation
        // exclude the old silver blade; no temporary head bitmap is made.
        int top=(int)eyeY-86,bottom=(int)eyeY+53;
        var mask=new bool[512,512];
        for(int y=Math.Max(0,top);y<Math.Min(512,bottom);y++)for(int x=298;x<439;x++){
            var c=original.GetPixel(x,y);
            if(c.A>0&&c.R>c.G*1.16&&c.G>c.B*1.12&&c.R>35)
                for(int dy=-2;dy<=2;dy++)for(int dx=-2;dx<=2;dx++)if(x+dx>=0&&x+dx<512&&y+dy>=0&&y+dy<512)mask[x+dx,y+dy]=true;
        }
        for(int y=Math.Max(0,top-2);y<Math.Min(512,bottom+2);y++)for(int x=296;x<441;x++)if(mask[x,y])output.SetPixel(x,y,original.GetPixel(x,y));
    }
    public static float[] Paint(string sourceFile,string referenceFile,string destination,float upperAngle,float forearmAngle,bool standardCarry,bool stopTorso) {
        using(var source=new Bitmap(sourceFile))using(var wholeReference=new Bitmap(referenceFile))using(var output=source.Clone(new Rectangle(0,0,512,512),PixelFormat.Format32bppArgb)){
            float eye=EyeY(source),baseEye=EyeY(wholeReference),shift=eye-baseEye;
            var shoulder=new PointF(365,247+shift);var elbow=Along(shoulder,40.4969f,upperAngle);var wrist=Along(elbow,36,forearmAngle);
            using(var g=Graphics.FromImage(output)){
                g.SmoothingMode=SmoothingMode.AntiAlias;g.PixelOffsetMode=PixelOffsetMode.HighQuality;g.InterpolationMode=InterpolationMode.HighQualityBicubic;
                if(stopTorso){
                    // Complete upper-figure selection includes its own head, jacket,
                    // carrying arm and weapon. Keep the independent braking legs below it.
                    Clear(g,"M 0 0 L 512 0 L 512 315 L 0 315 Z",shift);
                    Brush(g,wholeReference,"M 0 0 L 512 0 L 512 315 L 0 315 Z",new PointF(365,247),shoulder,0);
                }
                if(standardCarry&&!stopTorso){
                    Clear(g,"M 110 70 L 319 70 L 319 239 L 267 259 L 185 246 L 111 220 Z",shift);
                    Clear(g,"M 394 176 L 492 186 L 492 273 L 394 273 Z",shift);
                }
                Clear(g,OldArm,shift);
                // Repaint exposed jacket/strap material directly from a complete PNG.
                if(stopTorso)Brush(g,wholeReference,Torso,new PointF(365,247),shoulder,0);
                else Brush(g,source,Torso,new PointF(346,240),new PointF(346,240),0);
                if(standardCarry&&!stopTorso)Brush(g,wholeReference,Carry,new PointF(365,247),shoulder,0);
                JacketJoin(g,shift);
                Skin(g,shoulder,elbow,wrist);
                Brush(g,wholeReference,Upper,new PointF(365,247),shoulder,upperAngle-57.09f);
                Brush(g,wholeReference,Forearm,new PointF(387,281),elbow,forearmAngle-10);
                Brush(g,wholeReference,Sleeve,new PointF(365,247),shoulder,upperAngle-57.09f);
                if(stopTorso)Brush(g,wholeReference,Head,new PointF(365,247),shoulder,0);
                else NativeCollar(g,source,shift);
            }
            if(!stopTorso)RestoreHead(output,source,eye);
            if(!stopTorso){
                // Outside the front-arm editing envelope, retain exact native RGBA,
                // including antialias values. This also protects feet and carrying grip.
                int top=(int)Math.Floor(eye+30);
                for(int y=0;y<512;y++)for(int x=0;x<512;x++)
                    if(x<280||x>505||y<top||y>=335)output.SetPixel(x,y,source.GetPixel(x,y));
            }
            output.Save(destination,ImageFormat.Png);
            return new float[]{eye,shoulder.X,shoulder.Y,elbow.X,elbow.Y,wrist.X,wrist.Y};
        }
    }
}
