using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Runtime.InteropServices;

public static class AnimationPackaging {
    public static Rectangle Bounds(Bitmap bitmap) {
        var data=bitmap.LockBits(new Rectangle(0,0,bitmap.Width,bitmap.Height),ImageLockMode.ReadOnly,PixelFormat.Format32bppArgb);
        int minX=bitmap.Width,minY=bitmap.Height,maxX=-1,maxY=-1;
        try {
            byte[] row=new byte[bitmap.Width*4];
            for(int y=0;y<bitmap.Height;y++) {
                Marshal.Copy(IntPtr.Add(data.Scan0,y*data.Stride),row,0,row.Length);
                for(int x=0;x<bitmap.Width;x++) if(row[x*4+3]>32) {
                    minX=Math.Min(minX,x);maxX=Math.Max(maxX,x);minY=Math.Min(minY,y);maxY=Math.Max(maxY,y);
                }
            }
        } finally {bitmap.UnlockBits(data);}
        if(maxX<0) throw new InvalidDataException("Empty sprite");
        return Rectangle.FromLTRB(minX,minY,maxX+1,maxY+1);
    }
    public static int RowBoundary(Bitmap bitmap) {
        // Find the broadest transparent gap near the expected row division.
        int first=bitmap.Height*38/100,last=bitmap.Height*63/100;
        int runStart=-1,bestStart=-1,bestLength=0;
        var data=bitmap.LockBits(new Rectangle(0,0,bitmap.Width,bitmap.Height),ImageLockMode.ReadOnly,PixelFormat.Format32bppArgb);
        try {
            byte[] row=new byte[bitmap.Width*4];
            for(int y=first;y<=last;y++) {
                Marshal.Copy(IntPtr.Add(data.Scan0,y*data.Stride),row,0,row.Length);
                int visible=0;
                for(int x=0;x<bitmap.Width;x++) if(row[x*4+3]>32) visible++;
                if(visible==0) {if(runStart<0)runStart=y;}
                else if(runStart>=0) {
                    if(y-runStart>bestLength){bestStart=runStart;bestLength=y-runStart;}
                    runStart=-1;
                }
            }
            if(runStart>=0 && last+1-runStart>bestLength){bestStart=runStart;bestLength=last+1-runStart;}
        } finally {bitmap.UnlockBits(data);}
        if(bestStart<0) throw new InvalidDataException("No clean row separator; inspect source before cropping.");
        return bestStart+bestLength/2;
    }
    public static void Gif(string path,Bitmap[] frames,int[] delays) {
        if(frames.Length!=delays.Length)throw new ArgumentException("Frame/delay mismatch");
        using(var output=new BinaryWriter(File.Create(path))) {
            output.Write(System.Text.Encoding.ASCII.GetBytes("GIF89a"));
            output.Write((ushort)frames[0].Width);output.Write((ushort)frames[0].Height);
            output.Write((byte)0x70);output.Write((byte)0);output.Write((byte)0);
            output.Write(new byte[]{0x21,0xFF,11});output.Write(System.Text.Encoding.ASCII.GetBytes("NETSCAPE2.0"));
            output.Write(new byte[]{3,1,0,0,0});
            for(int n=0;n<frames.Length;n++) {
                using(var flat=new Bitmap(frames[n].Width,frames[n].Height,PixelFormat.Format24bppRgb)) {
                    using(var graphics=Graphics.FromImage(flat)) {
                        graphics.Clear(Color.FromArgb(31,37,51));graphics.DrawImageUnscaled(frames[n],0,0);
                    }
                    using(var memory=new MemoryStream()) {
                        flat.Save(memory,ImageFormat.Gif);byte[] bytes=memory.ToArray();
                        int packed=bytes[10],sizeBits=packed&7,offset=13;
                        byte[] palette=null;
                        if((packed&128)!=0) {
                            int count=3*(1<<(sizeBits+1));palette=new byte[count];Array.Copy(bytes,offset,palette,0,count);offset+=count;
                        }
                        while(bytes[offset]==0x21) {
                            offset+=2;
                            while(bytes[offset]!=0){offset+=1+bytes[offset];}offset++;
                        }
                        if(bytes[offset]!=0x2C)throw new InvalidDataException("GIF image missing");
                        int imagePacked=bytes[offset+9],dataStart=offset+10;
                        if((imagePacked&128)!=0) {
                            sizeBits=imagePacked&7;int count=3*(1<<(sizeBits+1));
                            palette=new byte[count];Array.Copy(bytes,dataStart,palette,0,count);dataStart+=count;
                        }
                        if(palette==null)throw new InvalidDataException("GIF palette missing");
                        int dataEnd=dataStart+1;
                        while(bytes[dataEnd]!=0){dataEnd+=1+bytes[dataEnd];}dataEnd++;
                        output.Write(new byte[]{0x21,0xF9,4,0});output.Write((ushort)Math.Max(1,delays[n]/10));output.Write(new byte[]{0,0});
                        output.Write((byte)0x2C);output.Write((ushort)0);output.Write((ushort)0);
                        output.Write((ushort)frames[n].Width);output.Write((ushort)frames[n].Height);
                        output.Write((byte)(128|sizeBits));output.Write(palette);
                        output.Write(bytes,dataStart,dataEnd-dataStart);
                    }
                }
            }
            output.Write((byte)0x3B);
        }
    }
}
