// Offline artwork helper, not Godot engine code. One flat RGBA canvas only.
using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using System.Globalization;
using System.IO;
using System.Text.RegularExpressions;

public static class FlatLiftPainting {
    static Color C(string value) { return ColorTranslator.FromHtml(value); }
    static GraphicsPath PathData(string text) {
        var tokens = Regex.Matches(text, @"[MLCZ]|-?\d+(?:\.\d+)?");
        int i=0; PointF last=new PointF(); var result=new GraphicsPath();
        Func<float> number=()=>float.Parse(tokens[i++].Value,CultureInfo.InvariantCulture);
        while(i<tokens.Count) {
            string command=tokens[i++].Value;
            if(command=="M") { last=new PointF(number(),number());result.StartFigure(); }
            else if(command=="L") { var next=new PointF(number(),number());result.AddLine(last,next);last=next; }
            else if(command=="C") { var a=new PointF(number(),number());var b=new PointF(number(),number());var next=new PointF(number(),number());result.AddBezier(last,a,b,next);last=next; }
            else if(command=="Z") result.CloseFigure();
            else throw new InvalidDataException("Unexpected path token: "+command);
        }
        return result;
    }
    static void Shape(Graphics g,string data,string fill,string outline,float width) {
        using(var p=PathData(data)) {
            if(fill!=null) using(var b=new SolidBrush(C(fill))) g.FillPath(b,p);
            if(outline!=null) using(var pen=new Pen(C(outline),width)) {pen.LineJoin=LineJoin.Round;g.DrawPath(pen,p);}
        }
    }
    static void Line(Graphics g,string data,string color,float width) {Shape(g,data,null,color,width);}
    static PointF[] Points(float[] values) {
        var p=new PointF[values.Length/2];for(int i=0;i<p.Length;i++)p[i]=new PointF(values[i*2],values[i*2+1]);return p;
    }
    static void Polygon(Graphics g,float[] values,string fill,string outline,float width) {
        var p=Points(values);using(var b=new SolidBrush(C(fill)))g.FillPolygon(b,p);
        if(outline!=null)using(var pen=new Pen(C(outline),width)){pen.LineJoin=LineJoin.Round;g.DrawPolygon(pen,p);}
    }
    static void Oval(Graphics g,float x,float y,float w,float h,string fill,string outline,float width) {
        using(var b=new SolidBrush(C(fill)))g.FillEllipse(b,x,y,w,h);
        if(outline!=null)using(var p=new Pen(C(outline),width))g.DrawEllipse(p,x,y,w,h);
    }
    static void ClearWeapon(Graphics g,float centerX,float centerY,float angle) {
        var state=g.Save();g.TranslateTransform(centerX,centerY);g.RotateTransform(angle);
        g.CompositingMode=CompositingMode.SourceCopy;
        using(var b=new SolidBrush(Color.Transparent)) {
            g.FillRectangle(b,32,-20,202,40);
            g.FillRectangle(b,136,-20,98,69);
            g.FillPolygon(b,Points(new float[]{-36,-38,38,-38,38,38,-36,38}));
        }
        g.Restore(state);
        // Old diagonal chain lies outside the silhouette; erase it on this same bitmap.
        state=g.Save();g.CompositingMode=CompositingMode.SourceCopy;
        using(var p=PathData("M 175 283 L 187 297 L 166 327 L 165 343 L 153 354 L 137 340 L 142 319 L 158 294 Z"))
        using(var b=new SolidBrush(Color.Transparent))g.FillPath(b,p);
        g.Restore(state);
    }
    static void RestoreClothAndDrawArm(Graphics g) {
        // Repaint the previously hidden jacket/lining/waist directly into the full sprite.
        Shape(g,"M 234 248 C 251 245 262 257 267 275 L 258 307 L 234 327 L 211 315 L 198 294 L 214 268 Z","#171C20","#101315",2.2f);
        Shape(g,"M 239 257 C 249 257 250 270 253 278 L 242 302 L 221 315 L 208 304 L 216 282 Z","#292F33",null,0);
        Shape(g,"M 257 259 L 263 277 L 247 311 L 235 318 L 233 307 L 247 286 Z","#C52523","#231618",1.4f);
        Shape(g,"M 240 295 L 241 308 L 225 322 L 215 322 L 227 309 Z","#E83C2C",null,0);
        Line(g,"M 224 287 C 232 292 239 289 246 281","#657075",1.4f);
        Line(g,"M 216 295 C 222 300 226 301 232 300","#121618",1.5f);
        Shape(g,"M 220 277 L 229 271 L 241 278 L 238 289 L 226 297 L 214 292 Z","#333B3E",null,0);
        Shape(g,"M 222 279 L 228 276 L 233 280 L 229 288 L 219 292 Z","#465153",null,0);
        Line(g,"M 217 285 C 223 281 229 280 232 278","#707B7A",1.0f);
        Line(g,"M 215 303 C 221 298 227 296 230 292","#101618",1.3f);
        Shape(g,"M 210 315 C 225 312 242 316 254 321 L 263 324 L 258 332 L 238 326 L 222 323 L 209 323 Z","#B42420","#211719",1.5f);
        Shape(g,"M 220 317 L 247 322 L 257 326 L 256 329 L 238 325 L 222 322 Z","#EE3F2C",null,0);
        Shape(g,"M 243 314 L 265 327 L 261 332 L 239 319 Z","#E5B924","#322A13",1.2f);
        Line(g,"M 244 316 L 263 328","#FFE060",1.2f);
        // Far shoulder stays attached to the original body; elbow changes genuinely.
        Shape(g,"M 245 212 C 234 215 216 225 205 239 L 217 253 C 231 245 242 239 253 232 L 251 220 Z","#22282C","#101518",2.4f);
        Shape(g,"M 241 218 C 226 222 218 230 211 238 L 218 244 L 235 233 L 246 228 Z","#454D50",null,0);
        Shape(g,"M 237 217 C 243 216 249 221 249 226 C 245 232 239 233 233 232 L 226 228 Z","#606A6D","#171E21",1.4f);
        Shape(g,"M 235 219 C 240 218 244 220 245 223 L 234 226 L 230 225 Z","#8A979B",null,0);
        Line(g,"M 211 234 C 220 229 228 225 233 221","#A2AAAB",1.3f);
        // Biceps/forearm connect the fixed shoulder to an intermediate lower-chest grip.
        Shape(g,"M 208 242 C 201 247 190 258 181 266 C 176 271 178 279 184 282 C 190 284 197 280 203 276 L 213 268 L 210 254 L 217 250 Z","#E8AE83","#27201C",2.3f);
        Shape(g,"M 207 248 C 195 256 187 266 184 272 C 187 278 194 278 200 275 L 209 268 L 207 263 L 196 270 L 197 260 Z","#C77955",null,0);
        Shape(g,"M 207 246 L 202 252 L 197 258 L 198 262 L 209 253 L 213 253 Z","#F7CCA0",null,0);
        Line(g,"M 183 271 C 190 274 196 272 201 268","#9A5C40",1.1f);
        Shape(g,"M 203 238 L 211 233 L 222 246 L 214 253 L 207 250 Z","#899597","#252D2F",1.8f);
        Shape(g,"M 205 240 L 211 237 L 218 247 L 214 249 Z","#CFD4CC",null,0);
        Line(g,"M 210 236 L 219 247","#F0F0DA",1.0f);
    }
    static void DrawChain(Graphics g,PointF pommel) {
        float startX=pommel.X+3,startY=pommel.Y+4;
        for(int i=0;i<8;i++) {
            float x=startX+5*(float)Math.Sin(i*0.42),y=startY+i*5.8f;
            Oval(g,x-3,y-4,6,8,"#929B9B","#303638",1.4f);
            Oval(g,x-1.25f,y-2,2.5f,4,"#293133",null,0);
            Line(g,"M "+(x-2).ToString(CultureInfo.InvariantCulture)+" "+(y-2).ToString(CultureInfo.InvariantCulture)+" L "+(x-1).ToString(CultureInfo.InvariantCulture)+" "+(y-3).ToString(CultureInfo.InvariantCulture),"#D9DEDC",0.8f);
        }
        float endX=startX+5*(float)Math.Sin(7*0.42),endY=startY+46;
        Oval(g,endX-12,endY-5,10,10,"#A2ABAA","#30383A",1.8f);
        Oval(g,endX+2,endY-5,10,10,"#A2ABAA","#30383A",1.8f);
        Oval(g,endX-8,endY,16,16,"#9EA9A8","#293234",1.8f);
        Oval(g,endX-4,endY+2,5,4,"#D7DEDB",null,0);
        Oval(g,endX-10,endY-3,3,2,"#D7DEDB",null,0);
    }
    static void DrawConnectedWeaponAndGrip(Graphics g,float gripX,float gripY,float angle) {
        double radians=angle*Math.PI/180;
        var pommel=new PointF(gripX-35*(float)Math.Cos(radians),gripY-35*(float)Math.Sin(radians));
        DrawChain(g,pommel);
        var state=g.Save();g.TranslateTransform(gripX,gripY);g.RotateTransform(angle);
        // All rigid weapon measurements are in a single local axis, not independent layers.
        using(var shaft=new LinearGradientBrush(new PointF(70,-7),new PointF(70,7),C("#F4F4E7"),C("#7F898E"))) {
            shaft.WrapMode=WrapMode.TileFlipXY;g.FillRectangle(shaft,43,-7,163,14);
        }
        Polygon(g,new float[]{43,-7,206,-7,209,-3,209,7,43,7},"#B2BBBC","#252B2C",2.1f);
        Shape(g,"M 45 -5 L 204 -5 L 206 -2 L 206 0 L 45 0 Z","#E2E6DC",null,0);
        Line(g,"M 49 -4 L 202 -4","#FAFAE9",1.35f);
        Line(g,"M 46 5 L 203 5","#717C84",1.15f);
        Polygon(g,new float[]{202,7,194,27,188,30,186,17,180,14,182,31,173,35,171,23,167,21,165,37,156,39,142,13,138,7},"#A6B0B4","#2A2F30",2.0f);
        Shape(g,"M 198 9 L 191 24 L 189 25 L 187 13 L 179 10 L 178 28 L 174 30 L 174 20 L 167 17 L 162 34 L 158 34 L 145 11 Z","#D0D6D5",null,0);
        Line(g,"M 155 35 L 162 36 L 166 25","#747F89",1.2f);
        Line(g,"M 172 29 L 177 31 L 180 23","#859097",1.1f);
        Polygon(g,new float[]{29,-7,34,-9,43,-8,45,-5,45,6,42,9,33,8,29,6},"#263D57","#20272B",1.8f);
        Shape(g,"M 32 -6 L 42 -6 L 43 -2 L 32 -2 Z","#697E94",null,0);
        Line(g,"M 43 -6 L 43 5","#D4D8D1",1.2f);
        Polygon(g,new float[]{-29,-5,29,-5,29,5,-29,5},"#282D2F","#151A1C",1.5f);
        Line(g,"M -22 -2 L 22 -2","#62686A",1.3f);
        Oval(g,-40,-6,12,12,"#B5BCB3","#303B3A",1.8f);
        Oval(g,-37,-4,5,4,"#E2E8DA",null,0);
        var outer=Points(new float[]{-32,-22,-25,-29,26,-29,35,-22,35,22,27,29,-25,29,-32,22});
        var inner=Points(new float[]{-24,-17,-19,-21,22,-21,27,-16,27,16,21,21,-19,21,-24,16});
        using(var frame=new GraphicsPath(FillMode.Alternate)) {
            frame.AddPolygon(outer);frame.AddPolygon(inner);
            using(var gold=new LinearGradientBrush(new PointF(-21,-27),new PointF(24,27),C("#FFE45A"),C("#C28B10"))) {gold.WrapMode=WrapMode.TileFlipXY;g.FillPath(gold,frame);}
            using(var outline=new Pen(C("#403014"),2.0f)) {outline.LineJoin=LineJoin.Round;g.DrawPolygon(outline,outer);g.DrawPolygon(outline,inner);}
        }
        Line(g,"M -25 -26 L 25 -26 L 31 -20 L 31 18","#FFF49A",1.25f);
        Line(g,"M -29 -19 L -29 20 L -22 26 L 24 26","#AC740A",1.35f);
        foreach(var uv in new PointF[]{new PointF(-23,-25),new PointF(24,-25),new PointF(-23,25),new PointF(24,25)}) {
            Oval(g,uv.X-2,uv.Y-2,4,4,"#967010","#604713",0.65f);
            Oval(g,uv.X-1.3f,uv.Y-1.3f,1.5f,1.5f,"#FFE589",null,0);
        }
        // Wrist enters from local negative-v side; thumb folds over the index finger.
        Shape(g,"M -11 -23 L 13 -23 L 15 -16 L -13 -16 Z","#171E22","#121718",1.8f);
        Line(g,"M -8 -21 L 10 -21","#D4B83D",1.2f);
        Shape(g,"M -15 -17 C -20 -10 -19 2 -14 9 L 12 10 C 18 5 20 -5 16 -13 L 11 -18 Z","#20282B","#111719",2.0f);
        Shape(g,"M -13 -15 C -16 -8 -15 -2 -11 4 L -6 6 L -8 -7 L 11 -13 Z","#424A4A",null,0);
        for(int i=0;i<4;i++) {
            float u=-14+i*8.4f;
            Shape(g,"M "+u.ToString(CultureInfo.InvariantCulture)+" -1 C "+(u-1).ToString(CultureInfo.InvariantCulture)+" -4 "+(u+4).ToString(CultureInfo.InvariantCulture)+" -4 "+(u+5).ToString(CultureInfo.InvariantCulture)+" -1 L "+(u+4).ToString(CultureInfo.InvariantCulture)+" 8 C "+(u+2).ToString(CultureInfo.InvariantCulture)+" 10 "+(u-1).ToString(CultureInfo.InvariantCulture)+" 8 "+u.ToString(CultureInfo.InvariantCulture)+" 5 Z","#E9B18A","#4C3127",1.0f);
            Line(g,"M "+(u+1).ToString(CultureInfo.InvariantCulture)+" -1 L "+(u+3).ToString(CultureInfo.InvariantCulture)+" -1","#FFD7AA",1.0f);
        }
        Shape(g,"M 13 -12 C 17 -9 18 -4 16 1 L 12 4 L 8 -1 C 11 -5 8 -8 8 -11 Z","#F2BC94","#51342A",1.1f);
        Line(g,"M 14 -8 C 15 -5 14 -3 12 -2","#FFDCAE",1.0f);
        g.Restore(state);
    }
    public static void Paint(string source,string target) {
        if(File.Exists(target))throw new IOException("Preserve existing pilot; choose a new version");
        using(var original=new Bitmap(source)) {
            if(original.Width!=512||original.Height!=512)throw new InvalidDataException("Expected512px complete source");
            // Clone native pixels; drawing a whole PNG through GDI can round alpha colors.
            using(var bitmap=original.Clone(new Rectangle(0,0,512,512),PixelFormat.Format32bppArgb)) {
                for(int y=0;y<512;y++)for(int x=0;x<512;x++)if(bitmap.GetPixel(x,y).ToArgb()!=original.GetPixel(x,y).ToArgb())
                    throw new InvalidDataException("Whole-source clone changed a pixel");
                using(var g=Graphics.FromImage(bitmap)) {
                    g.CompositingMode=CompositingMode.SourceOver;g.SmoothingMode=SmoothingMode.AntiAlias;g.PixelOffsetMode=PixelOffsetMode.HighQuality;
                    ClearWeapon(g,217,281,-136);
                    RestoreClothAndDrawArm(g);
                    DrawConnectedWeaponAndGrip(g,218,257,-115);
                }
                // Protected artwork is untouched outside the directly painted lift region.
                int changed=0,outside=0;
                for(int y=0;y<512;y++)for(int x=0;x<512;x++)if(bitmap.GetPixel(x,y).ToArgb()!=original.GetPixel(x,y).ToArgb()) {
                    changed++;if(x>279||y>355)outside++;
                }
                if(outside!=0)throw new InvalidDataException("Painting touched protected face/free arm/lower body: "+outside);
                bitmap.Save(target,ImageFormat.Png);
                Console.WriteLine("Changed flat-canvas pixels: "+changed+"; outside permitted lift area: "+outside);
            }
        }
    }
}
