// Offline artwork only. Every output is painted directly on one complete RGBA canvas.
using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using System.Globalization;
using System.IO;
using System.Text.RegularExpressions;

public static class FlatRunPainting {
    static Color C(string s){return ColorTranslator.FromHtml(s);}
    static string N(float f){return f.ToString("0.###",CultureInfo.InvariantCulture);}
    static string P(PointF p){return N(p.X)+" "+N(p.Y);}
    static PointF Add(PointF p,float x,float y){return new PointF(p.X+x,p.Y+y);}
    static PointF Mix(PointF a,PointF b,float t){return new PointF(a.X+(b.X-a.X)*t,a.Y+(b.Y-a.Y)*t);}
    static GraphicsPath Path(string s){
        var t=Regex.Matches(s,@"[MLCZ]|-?\d+(?:\.\d+)?");int i=0;PointF last=new PointF();var p=new GraphicsPath();
        Func<float> n=()=>float.Parse(t[i++].Value,CultureInfo.InvariantCulture);
        while(i<t.Count){string cmd=t[i++].Value;if(cmd=="M"){last=new PointF(n(),n());p.StartFigure();}
        else if(cmd=="L"){var q=new PointF(n(),n());p.AddLine(last,q);last=q;}
        else if(cmd=="C"){var a=new PointF(n(),n());var b=new PointF(n(),n());var q=new PointF(n(),n());p.AddBezier(last,a,b,q);last=q;}
        else if(cmd=="Z")p.CloseFigure();else throw new InvalidDataException(cmd);}
        return p;
    }
    static void Shape(Graphics g,string data,string fill,string edge,float width){using(var p=Path(data)){
        if(fill!=null)using(var b=new SolidBrush(C(fill)))g.FillPath(b,p);
        if(edge!=null)using(var pen=new Pen(C(edge),width)){pen.LineJoin=LineJoin.Round;g.DrawPath(pen,p);}}}
    static void Grad(Graphics g,string data,string light,string dark,string edge,float width){using(var p=Path(data)){
        var r=p.GetBounds();using(var b=new LinearGradientBrush(r,C(light),C(dark),50)){b.WrapMode=WrapMode.TileFlipXY;g.FillPath(b,p);}
        if(edge!=null)using(var pen=new Pen(C(edge),width)){pen.LineJoin=LineJoin.Round;g.DrawPath(pen,p);}}}
    static void Line(Graphics g,string s,string color,float width){Shape(g,s,null,color,width);}
    static void Ellipse(Graphics g,float x,float y,float w,float h,string fill,string edge,float width){
        using(var b=new SolidBrush(C(fill)))g.FillEllipse(b,x,y,w,h);
        if(edge!=null)using(var pen=new Pen(C(edge),width))g.DrawEllipse(pen,x,y,w,h);}
    static void Erase(Graphics g,string data){var save=g.Save();g.CompositingMode=CompositingMode.SourceCopy;
        using(var p=Path(data))using(var b=new SolidBrush(Color.Transparent))g.FillPath(b,p);g.Restore(save);}
    static PointF Transform(PointF p,float pitch,float bob){double a=pitch*Math.PI/180;float x=p.X-276,y=p.Y-310;
        return new PointF(276+x*(float)Math.Cos(a)-y*(float)Math.Sin(a),310+x*(float)Math.Sin(a)+y*(float)Math.Cos(a)+bob);}
    static void BodyTransform(Graphics g,float pitch,float bob){g.TranslateTransform(276,310+bob);g.RotateTransform(pitch);g.TranslateTransform(-276,-310);}
    static bool[,] HeadSelection(Bitmap b){
        // A temporary selection of protected source pixels, never an exported body layer.
        var mask=new bool[512,512];
        for(int y=140;y<251;y++)for(int x=305;x<439;x++){
            var c=b.GetPixel(x,y);if(c.A<80||c.R<52||c.R<c.G*1.13||c.R<c.B*1.35)continue;
            for(int dy=-3;dy<=3;dy++)for(int dx=-3;dx<=3;dx++)if(dx*dx+dy*dy<=9)mask[x+dx,y+dy]=true;
        }
        for(int y=136;y<255;y++)for(int x=301;x<443;x++)if(mask[x,y]){
            var c=b.GetPixel(x,y);
            bool brown=c.R>52&&c.R>c.G*1.13&&c.R>c.B*1.35;
            bool dark=c.R<70&&c.G<70&&c.B<70;
            bool eye=x>=375&&x<=398&&y>=208&&y<=232;
            mask[x,y]=c.A>0&&(brown||dark||eye);
        }return mask;
    }
    static void ClearSource(Graphics g){
        Erase(g,"M 0 300 L 512 300 L 512 512 L 0 512 Z");
        Erase(g,"M 0 281 L 207 281 L 214 291 L 250 297 L 250 332 L 0 332 Z");
        Erase(g,"M 130 134 L 310 134 L 310 224 L 130 224 Z");
        Erase(g,"M 203 215 L 270 215 L 270 283 L 203 283 Z");
        Erase(g,"M 390 203 L 505 203 L 505 280 L 390 280 Z");
        Erase(g,"M 357 250 L 512 250 L 512 330 L 330 330 L 331 294 L 347 272 Z");
    }
    static PointF Knee(PointF hip,PointF ankle){
        const float thigh=86,shin=54;float dx=ankle.X-hip.X,dy=ankle.Y-hip.Y;
        float d=(float)Math.Sqrt(dx*dx+dy*dy);
        if(d>thigh+shin+0.01||d<Math.Abs(thigh-shin)-0.01)throw new InvalidDataException("Unreachable leg "+P(hip)+" -> "+P(ankle));
        float along=(thigh*thigh-shin*shin+d*d)/(2*d);
        float side=(float)Math.Sqrt(Math.Max(0,thigh*thigh-along*along));
        return new PointF(hip.X+dx/d*along+dy/d*side,hip.Y+dy/d*along-dx/d*side);
    }
    const string ShoeOuter="M -20 -16 C -18 -25 -2 -28 10 -22 L 16 -12 L 13 -2 C 29 -4 48 -1 57 11 C 66 21 65 31 54 37 C 34 44 -9 45 -24 32 L -26 7 Z";
    public static float ShoeBottom(float angle){using(var p=Path(ShoeOuter))using(var m=new Matrix()){
        m.Rotate(angle);p.Transform(m);return p.GetBounds().Bottom+1.4f;}}
    public static void Shoe(Graphics g,PointF ankle,float angle,bool near){
        var s=g.Save();g.TranslateTransform(ankle.X,ankle.Y);g.RotateTransform(angle);
        Grad(g,ShoeOuter,near?"#343B3D":"#2D3538","#171C20","#101517",2.5f);
        Shape(g,"M -24 22 C -7 31 32 35 59 24 C 65 29 58 36 49 39 C 27 45 -13 43 -24 33 Z","#171C20","#101416",1.7f);
        Line(g,"M -20 33 C 0 40 33 40 52 33","#4D5150",1.0f);
        Grad(g,"M 14 3 C 29 -2 49 2 56 13 C 61 19 60 26 53 30 C 41 35 25 34 10 29 L 5 21 Z",near?"#FFE459":"#DABF49","#D9950F","#28271B",1.7f);
        Shape(g,"M 18 5 C 29 1 47 5 51 12 C 38 9 26 11 17 17 L 12 21 L 12 12 Z",near?"#FFEC7B":"#E4CF71",null,0);
        Shape(g,"M 55 19 C 61 21 63 27 58 32 C 50 37 42 39 34 39 L 37 32 C 47 32 52 27 55 19 Z","#202627","#151B1C",1.2f);
        Line(g,"M 44 34 C 50 32 54 29 56 26","#525A54",1.2f);
        Line(g,"M 20 5 C 32 2 45 5 51 10","#FFF1A0",1.1f);
        Line(g,"M 16 29 C 32 34 45 32 54 27","#F8CD3C",1.1f);
        Shape(g,"M -21 7 L -9 5 L 4 27 L -18 26 Z","#C62A25","#261A1D",1.5f);
        Shape(g,"M -18 9 L -11 8 L -4 22 L -14 19 Z","#F0402E",null,0);
        Grad(g,"M -15 -19 C -8 -23 4 -23 11 -17 L 10 -4 C 3 1 -12 0 -17 -7 Z","#DCC560","#C88D16","#26251C",1.8f);
        Shape(g,"M -10 -16 C -4 -18 3 -17 6 -14 L 5 -8 L -11 -9 Z","#434C51","#171E21",1.3f);
        Line(g,"M -9 -15 C -3 -18 3 -16 5 -14","#BFC4B6",1.2f);
        Shape(g,"M -11 -3 L -3 -5 L 14 18 L 8 22 Z","#E8B429","#37301A",1.4f);
        Shape(g,"M 14 -7 L 20 -3 L 0 23 L -7 21 Z","#E9B52E","#30291B",1.5f);
        Line(g,"M 14 -4 L -3 20","#FFE465",1.2f);
        Shape(g,"M -2 4 L 6 6 L 5 13 L -2 15 L -7 10 Z","#626A65","#1B2222",1.5f);
        Shape(g,"M -2 6 L 3 7 L 2 11 L -2 12 Z","#D5D3AC",null,0);
        Line(g,"M -22 2 C -16 -4 -10 -5 -6 -2 M -24 6 L -17 5","#68736A",1.0f);
        Shape(g,"M 5 -21 L 13 -17 L 15 -7 L 12 -3 L 9 -8 Z","#B2B9A9","#333D37",1.1f);
        Line(g,"M 10 -17 L 12 -8","#EEECD2",.9f);
        Line(g,"M 31 36 L 26 41 M 44 34 L 40 39 M -15 30 L -12 35","#0C1214",1.3f);
        g.Restore(s);
    }
    public static void Leg(Graphics g,PointF hip,PointF ankle,float shoeAngle,bool near){
        var k=Knee(hip,ankle);float dx=k.X-hip.X,dy=k.Y-hip.Y,len=(float)Math.Sqrt(dx*dx+dy*dy);
        var s=g.Save();g.TranslateTransform(hip.X,hip.Y);g.RotateTransform((float)(Math.Atan2(dy,dx)*180/Math.PI)-90);
        // Baggy shorts, material planes, curved inseam and fixed-width cuff.
        Grad(g,"M -27 -7 C -34 7 -38 27 -35 49 C -34 65 -28 80 -20 86 C -8 96 17 94 26 85 C 33 72 33 56 32 41 L 26 1 Z",near?"#363B40":"#2D3338","#20262B","#101619",2.6f);
        Shape(g,"M -28 5 C -32 24 -29 54 -23 64 C -12 75 0 78 10 71 C -3 62 -5 38 1 16 L 8 5 Z",near?"#3C4247":"#333A3F",null,0);
        Shape(g,"M 19 13 C 16 35 22 54 20 68 C 16 78 0 87 -13 85 L -20 85 C -7 97 16 93 25 84 C 33 64 29 44 27 27 Z","#1B2126",null,0);
        Line(g,"M -29 19 C -32 36 -24 54 -16 63 C -4 73 8 74 23 64",near?"#C7C9BE":"#8F9A97",1.4f);
        Line(g,"M -27 23 C -30 40 -20 58 -8 65","#606A6D",0.9f);
        Line(g,"M -21 86 C -7 92 14 92 24 83","#677072",1.3f);
        Shape(g,"M 19 -2 L 29 0 L 21 31 L 12 29 Z","#E6AE25","#413419",1.5f);
        Line(g,"M 21 1 L 14 27","#FFE263",1.2f);
        Ellipse(g,20,3,4,4,"#D8D3AE","#403F33",0.7f);
        Line(g,"M 7 1 L 2 18 M -16 10 L -11 26","#161D21",1.4f);
        Line(g,"M -24 8 C -21 19 -23 28 -21 34 M 8 6 C 14 14 10 22 9 27","#555F62",.9f);
        Line(g,"M -12 72 C -1 77 10 76 17 71 M -17 76 C -5 82 9 83 19 76","#171F23",1.1f);
        Line(g,"M -18 73 C -9 79 0 81 7 80","#6C7777",.8f);
        Line(g,"M 23 43 C 23 51 21 57 17 61","#424D52",1.0f);
        g.Restore(s);
        // Exposed calf joins the cuff and boot socket, without stretch or pasted cutouts.
        dx=ankle.X-k.X;dy=ankle.Y-k.Y;len=(float)Math.Sqrt(dx*dx+dy*dy);
        float px=-dy/len,py=dx/len;
        var q0=Add(k,px*11,py*11);var q1=Add(ankle,px*8,py*8);
        var q2=Add(ankle,-px*8,-py*8);var q3=Add(k,-px*11,-py*11);
        Grad(g,"M "+P(q0)+" C "+P(Mix(q0,q1,.35f))+" "+P(Mix(q0,q1,.7f))+" "+P(q1)+" L "+P(q2)+" C "+P(Mix(q2,q3,.35f))+" "+P(Mix(q2,q3,.7f))+" "+P(q3)+" Z",near?"#FFD0A2":"#E9B189","#BF7551","#34251F",1.8f);
        Line(g,"M "+P(Add(Mix(k,ankle,.2f),px*5,py*5))+" L "+P(Add(Mix(k,ankle,.8f),px*4,py*4)),near?"#FFDBAF":"#ECC6A0",1.5f);
        Shoe(g,ankle,shoeAngle,near);
        // Cuff rim occludes the upper calf. Repaint its curved edge on the same canvas.
        s=g.Save();g.TranslateTransform(hip.X,hip.Y);g.RotateTransform((float)(Math.Atan2(k.Y-hip.Y,k.X-hip.X)*180/Math.PI)-90);
        Shape(g,"M -22 79 C -9 86 12 87 26 78 L 25 86 C 14 96 -8 95 -21 87 Z",near?"#292F34":"#232B30","#11191C",1.8f);
        Line(g,"M -20 81 C -7 88 12 88 23 81",near?"#8A9495":"#647276",1.2f);g.Restore(s);
    }
    static void Waist(Graphics g,float clothLag){
        Grad(g,"M 223 294 C 240 299 267 304 289 302 L 312 304 L 319 320 C 313 333 294 337 274 335 C 249 334 230 327 215 315 Z","#282F34","#141C20","#11191C",2.1f);
        Shape(g,"M 263 309 L 269 310 L 274 334 L 268 332 Z","#3E484C","#1D2528",1.0f);
        Line(g,"M 278 315 L 282 326 C 288 332 297 331 305 326","#687773",1.0f);
        Line(g,"M 241 308 C 244 317 251 320 258 322","#465154",.9f);
        Grad(g,"M 215 288 C 201 291 188 298 175 314 L 204 308 C 204 315 202 321 201 328 C 217 332 232 319 239 306 L 256 302 L 244 294 Z","#D43529","#8F2422","#31171A",2.0f);
        Shape(g,"M 213 295 L 200 308 L 207 320 L 227 307 L 223 299 Z","#EB3E2D",null,0);
        Line(g,"M 181 311 L 205 303 L 230 301","#F66540",1.0f);
        Line(g,"M 204 309 L 202 326 M 224 301 L 228 307","#541A1D",1.5f);
        float tx=178+clothLag;
        Grad(g,"M 219 294 C 204 299 "+N(tx+5)+" 302 "+N(tx)+" 310 C "+N(tx+8)+" 313 "+N(tx+14)+" 322 "+N(tx+20)+" 329 C 204 330 217 320 225 309 L 233 304 Z","#D9392B","#882020","#30191B",1.9f);
        Shape(g,"M 216 298 C 204 304 "+N(tx+11)+" 304 "+N(tx+3)+" 310 L 210 309 L 220 302 Z","#EB422D",null,0);
        Line(g,"M "+N(tx+1)+" 311 C 192 312 206 315 214 315 L 219 295","#571E21",1.5f);
        Line(g,"M "+N(tx+4)+" 311 L 209 298","#EE4C32",1.0f);
        Shape(g,"M 237 292 C 256 304 281 311 312 311 L 322 315 L 318 320 C 290 320 258 313 233 302 Z","#E6B02B","#322B19",1.5f);
        Line(g,"M 240 295 C 260 307 289 314 316 315","#FFE164",1.4f);
        Shape(g,"M 290 307 L 300 309 L 297 317 L 287 315 Z","#AEAC83","#31392F",1.3f);
        Shape(g,"M 292 309 L 297 310 L 296 314 L 291 313 Z","#E5D99F",null,0);
    }
    static void ArmSegment(Graphics g,PointF a,PointF b,float w0,float w1){
        float dx=b.X-a.X,dy=b.Y-a.Y,d=(float)Math.Sqrt(dx*dx+dy*dy),px=-dy/d,py=dx/d;
        var a0=Add(a,px*w0,py*w0);var b0=Add(b,px*w1,py*w1);var b1=Add(b,-px*w1,-py*w1);var a1=Add(a,-px*w0,-py*w0);
        Grad(g,"M "+P(a0)+" C "+P(Add(Mix(a0,b0,.32f),px*2,py*2))+" "+P(Add(Mix(a0,b0,.7f),px*2,py*2))+" "+P(b0)+" C "+P(Add(b0,dx/d*7,dy/d*7))+" "+P(Add(b1,dx/d*7,dy/d*7))+" "+P(b1)+" C "+P(Mix(b1,a1,.35f))+" "+P(Add(Mix(b1,a1,.8f),-px*2,-py*2))+" "+P(a1)+" C "+P(Add(a1,-dx/d*5,-dy/d*5))+" "+P(Add(a0,-dx/d*5,-dy/d*5))+" "+P(a0)+" Z","#FFD0A0","#C5845D","#35241F",1.7f);
        Line(g,"M "+P(Add(Mix(a,b,.2f),-px*w0*.45f,-py*w0*.45f))+" L "+P(Add(Mix(a,b,.8f),-px*w1*.4f,-py*w1*.4f)),"#FFE0B1",1.5f);
    }
    static void FreeArm(Graphics g,PointF shoulder,PointF elbow,PointF wrist,bool reaching){
        // Repair the original sleeve's opening and redraw an articulated empty arm.
        ArmSegment(g,shoulder,elbow,12,11);ArmSegment(g,elbow,wrist,11,9);
        float angle=(float)(Math.Atan2(elbow.Y-shoulder.Y,elbow.X-shoulder.X)*180/Math.PI);
        var s=g.Save();g.TranslateTransform(shoulder.X,shoulder.Y);g.RotateTransform(angle-90);
        Grad(g,"M -21 -11 C -23 -23 13 -25 21 -10 C 22 -1 21 8 17 16 C 7 20 -10 19 -19 14 Z","#5A656A","#202A30","#141B1F",2.1f);
        Shape(g,"M -19 9 C -9 13 7 14 18 10 L 17 16 C 6 20 -10 18 -18 15 Z","#A7B1AE","#303A3D",1.4f);
        Line(g,"M -15 13 C -5 16 7 16 14 13","#E5E6D5",1.2f);
        Shape(g,"M -15 -15 C -7 -20 5 -20 11 -15 L 12 -10 C 4 -9 -4 -10 -11 -7 Z","#718087","#283237",1.3f);
        Line(g,"M -11 -15 C -2 -19 5 -17 9 -14","#ACB8B4",1.0f);
        Line(g,"M -17 -4 C -11 -1 -8 3 -9 8 M 14 -5 L 13 5","#151F25",1.0f);g.Restore(s);
        angle=(float)(Math.Atan2(wrist.Y-elbow.Y,wrist.X-elbow.X)*180/Math.PI);
        s=g.Save();g.TranslateTransform(wrist.X,wrist.Y);g.RotateTransform(angle);
        Shape(g,"M -9 -11 L 5 -11 L 8 10 L -10 12 Z","#242D31","#11191C",1.8f);
        Line(g,"M -7 -9 L -5 9","#EAC340",2.0f);
        Grad(g,"M 5 -11 C 16 -15 25 -9 28 0 C 27 10 19 16 6 12 L 2 3 Z","#3D484A","#1B2428","#131A1C",2.0f);
        for(int j=0;j<4;j++){float y=-8+j*5;
            Grad(g,"M 20 "+N(y)+" C 24 "+N(y-2)+" 29 "+N(y)+" 29 "+N(y+3)+" L 25 "+N(y+5)+" L 20 "+N(y+3)+" Z","#F4C399","#CC875F","#52362B",0.9f);}
        Shape(g,"M 7 -10 C 12 -15 18 -14 20 -10 L 18 -4 L 12 -3 Z","#F0B990","#4D342B",1.0f);
        Line(g,"M 8 8 L 13 11 L 18 9","#737C76",1.0f);g.Restore(s);
    }
    static void HoldingArm(Graphics g,PointF shoulder,PointF grip,float angle){
        double a=angle*Math.PI/180;var wrist=new PointF(grip.X-(float)Math.Sin(a)*22,grip.Y+(float)Math.Cos(a)*22);
        var elbow=new PointF(Math.Min(shoulder.X-26,wrist.X-24),Math.Max(shoulder.Y+8,wrist.Y+31));
        ArmSegment(g,shoulder,elbow,12,13);ArmSegment(g,elbow,wrist,12,10);
        Ellipse(g,elbow.X-5,elbow.Y-5,10,8,"#F5BE8E",null,0);
        var s=g.Save();g.TranslateTransform(shoulder.X,shoulder.Y);g.RotateTransform(-22);
        Grad(g,"M -17 -18 C -12 -24 15 -17 19 -7 C 18 1 15 9 13 15 C 3 18 -12 15 -19 11 Z","#566268","#263137","#171E22",1.9f);
        Shape(g,"M -19 6 C -8 11 5 12 15 9 L 13 16 C 0 17 -11 14 -18 13 Z","#B4BDB7","#313D3F",1.3f);
        Shape(g,"M -11 -17 C -3 -20 6 -15 11 -9 L 8 -4 L -5 -7 Z","#7D8A8B","#293438",1.0f);
        Line(g,"M -7 -16 C 0 -16 5 -12 7 -8","#BCC4BE",1.0f);
        Line(g,"M -15 10 L 10 12","#E5E8D9",1.0f);g.Restore(s);
    }
    static void Chain(Graphics g,PointF origin,float lag){
        for(int j=0;j<8;j++){float x=origin.X+lag*(float)Math.Sin((j+1)*.19),y=origin.Y+j*5.0f;
            Ellipse(g,x-2.8f,y-3,5.6f,7,"#939FA2","#303A3E",1.15f);
            Ellipse(g,x-1,y-1.5f,2,3.8f,"#303A3E",null,0);Line(g,"M "+N(x-1.8f)+" "+N(y-1)+" L "+N(x-.8f)+" "+N(y-2),"#DAE0DC",.8f);}
        float ex=origin.X+lag*(float)Math.Sin(1.52),ey=origin.Y+39;
        Ellipse(g,ex-12,ey-5,10,10,"#B6C0BC","#2C393B",1.5f);Ellipse(g,ex+2,ey-5,10,10,"#B6C0BC","#2C393B",1.5f);
        Ellipse(g,ex-8,ey,16,16,"#AEBAB7","#2B383C",1.8f);Ellipse(g,ex-4,ey+2,5,4,"#F0F0DE",null,0);
    }
    public static void Weapon(Graphics g,PointF grip,float angle,float lag,bool secondHand){
        double a=angle*Math.PI/180;Chain(g,new PointF(grip.X-35*(float)Math.Cos(a),grip.Y-35*(float)Math.Sin(a)+3),lag);
        var s=g.Save();g.TranslateTransform(grip.X,grip.Y);g.RotateTransform(angle);
        // Constant slightly foreground-facing projected model: axial geometry never varies.
        using(var p=Path("M 43 -7 L 204 -7 C 210 -7 212 -3 210 2 C 209 5 207 7 204 7 L 43 7 Z"))
        using(var b=new LinearGradientBrush(new PointF(70,-7),new PointF(70,7),C("#F4F4E7"),C("#7F898E"))){b.WrapMode=WrapMode.TileFlipXY;g.FillPath(b,p);using(var pen=new Pen(C("#252B2C"),2.1f))g.DrawPath(pen,p);}
        Shape(g,"M 45 -5 L 201 -5 C 205 -5 207 -2 206 0 L 45 0 Z","#E2E6DC",null,0);Line(g,"M 49 -4 L 202 -4","#FAFAE9",1.35f);
        Grad(g,"M 202 7 L 194 25 C 193 27 190 30 188 30 L 186 17 L 180 14 L 182 29 C 182 32 177 35 173 35 L 171 23 L 167 21 L 165 35 C 164 38 158 40 156 39 L 143 15 C 141 12 139 9 138 7 Z","#D1D9D8","#828E96","#252B2D",2.1f);
        Line(g,"M 145 11 L 157 34 L 162 33 M 172 26 L 174 31 L 179 29 M 187 20 L 189 25 L 192 23","#E5E7DA",1.1f);
        Shape(g,"M 29 -7 L 34 -9 L 43 -8 L 45 -5 L 45 6 L 42 9 L 33 8 L 29 6 Z","#263D57","#20272B",1.8f);
        Line(g,"M 33 -5 L 42 -5","#8A9DAC",1.7f);Line(g,"M 43 -6 L 43 5","#D4D8D1",1.2f);
        Shape(g,"M -29 -5 L 29 -5 L 29 5 L -29 5 Z","#282D2F","#151A1C",1.5f);
        Line(g,"M -22 -2 L 22 -2","#62686A",1.3f);Ellipse(g,-40,-6,12,12,"#B5BCB3","#303B3A",1.8f);
        using(var outer=Path("M -32 -22 L -25 -29 L 26 -29 L 35 -22 L 35 22 L 27 29 L -25 29 L -32 22 Z"))
        using(var inner=Path("M -24 -17 L -19 -21 L 22 -21 L 27 -16 L 27 16 L 21 21 L -19 21 L -24 16 Z"))
        using(var ring=new GraphicsPath(FillMode.Alternate)){
            ring.AddPath(outer,false);ring.AddPath(inner,false);
            using(var gold=new LinearGradientBrush(new PointF(-21,-27),new PointF(24,27),C("#FFE45A"),C("#C28B10"))){gold.WrapMode=WrapMode.TileFlipXY;g.FillPath(gold,ring);}
            using(var edge=new Pen(C("#403014"),2)){edge.LineJoin=LineJoin.Round;g.DrawPath(edge,outer);g.DrawPath(edge,inner);}}
        Line(g,"M -25 -26 L 25 -26 L 31 -20 L 31 18","#FFF49A",1.25f);Line(g,"M -29 -19 L -29 20 L -22 26 L 24 26","#AC740A",1.35f);
        foreach(var p in new PointF[]{new PointF(-23,-25),new PointF(24,-25),new PointF(-23,25),new PointF(24,25)}){Ellipse(g,p.X-2,p.Y-2,4,4,"#967010","#604713",.65f);Ellipse(g,p.X-1.3f,p.Y-1.3f,1.5f,1.5f,"#FFE589",null,0);}
        // Positive-v socket: far wrist approaches the shoulder carry from below.
        Shape(g,"M -11 23 L 13 23 L 15 16 L -13 16 Z","#171E22","#121718",1.8f);Line(g,"M -8 21 L 10 21","#D4B83D",1.2f);
        Grad(g,"M -15 17 C -20 10 -19 -2 -14 -9 L 12 -10 C 18 -5 20 5 16 13 L 11 18 Z","#424A4A","#20282B","#111719",2.0f);
        for(int j=0;j<4;j++){float u=-14+j*8.4f;
            Grad(g,"M "+N(u)+" 1 C "+N(u-1)+" 4 "+N(u+4)+" 4 "+N(u+5)+" 1 L "+N(u+4)+" -8 C "+N(u+2)+" -10 "+N(u-1)+" -8 "+N(u)+" -5 Z","#F8C79E","#DA9C74","#4C3127",1.0f);}
        Shape(g,"M 13 12 C 17 9 18 4 16 -1 L 12 -4 L 8 1 C 11 5 8 8 8 11 Z","#F2BC94","#51342A",1.1f);
        if(secondHand){Shape(g,"M -7 17 C -16 16 -20 10 -18 3 L -13 -1 L -8 1 L -7 11 L 4 11 L 7 16 Z","#29343A","#111B20",1.5f);Line(g,"M -13 10 L -9 13 L 1 14","#687776",1.1f);}
        g.Restore(s);
    }
    public static PointF[] Paint(string source,string target,float pitch,float bob,PointF farAnkle,float farAngle,PointF nearAnkle,float nearAngle,PointF elbow,PointF wrist,PointF grip,float weaponAngle,float lag,bool secondHand){
        if(File.Exists(target))throw new IOException("Preserve existing artwork: "+target);
        using(var original=new Bitmap(source))using(var canvas=new Bitmap(512,512,PixelFormat.Format32bppArgb)){
            var head=HeadSelection(original);
            using(var g=Graphics.FromImage(canvas)){
                g.SmoothingMode=SmoothingMode.AntiAlias;g.PixelOffsetMode=PixelOffsetMode.HighQuality;g.InterpolationMode=InterpolationMode.HighQualityBicubic;
                var s=g.Save();BodyTransform(g,pitch,bob);g.DrawImageUnscaled(original,0,0);ClearSource(g);g.Restore(s);
                PointF farHip=Transform(new PointF(250,321),pitch,bob),nearHip=Transform(new PointF(292,326),pitch,bob);
                Leg(g,farHip,farAnkle,farAngle,false);Leg(g,nearHip,nearAnkle,nearAngle,true);
                s=g.Save();BodyTransform(g,pitch,bob);Waist(g,lag);g.Restore(s);
                HoldingArm(g,Transform(new PointF(269,242),pitch,bob),grip,weaponAngle);
                FreeArm(g,Transform(new PointF(369,268),pitch,bob),elbow,wrist,secondHand);
                Weapon(g,grip,weaponAngle,lag,secondHand);
            }
            // Restore only protected source face/hair pixels into the same painted canvas.
            // Integer translation is exact for the run; stop's rotation is sampled from a full-source canvas.
            using(var reference=new Bitmap(512,512,PixelFormat.Format32bppArgb))using(var g=Graphics.FromImage(reference)){
                g.InterpolationMode=InterpolationMode.HighQualityBicubic;g.PixelOffsetMode=PixelOffsetMode.HighQuality;BodyTransform(g,pitch,bob);g.DrawImageUnscaled(original,0,0);
                for(int y=136;y<255;y++)for(int x=301;x<443;x++)if(head[x,y]){
                    PointF q=Transform(new PointF(x,y),pitch,bob);int xx=(int)Math.Round(q.X),yy=(int)Math.Round(q.Y);
                    if(xx>=1&&xx<511&&yy>=1&&yy<511){var c=reference.GetPixel(xx,yy);if(c.A>0)canvas.SetPixel(xx,yy,c);}
                }
            }
            canvas.Save(target,ImageFormat.Png);
            var fh=Transform(new PointF(250,321),pitch,bob);var nh=Transform(new PointF(292,326),pitch,bob);
            return new PointF[]{fh,Knee(fh,farAnkle),farAnkle,nh,Knee(nh,nearAnkle),nearAnkle};
        }
    }
}
