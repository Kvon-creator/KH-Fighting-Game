param([ValidatePattern('^motion_refinement_v[0-9]+$')][string]$Version='motion_refinement_v1')
$ErrorActionPreference='Stop'
$soraRoot=(Resolve-Path (Join-Path $PSScriptRoot '../../../../../..')).Path
if($soraRoot -ne 'D:\KH Fighting Game'){throw "Unexpected workspace: $soraRoot"}
$soraReady=Join-Path $soraRoot 'design/sprites/smooth/sora/replacement_work/ready'
$soraTrial='direct_generation_retry_v1'
foreach($soraAnimation in @('run_loop','run_stop')){
    if(Test-Path -LiteralPath (Join-Path $soraReady "$soraAnimation/$soraTrial/$Version")){throw 'Preserve previous refinement'}
}
Add-Type -AssemblyName System.Drawing
Add-Type -Path (Join-Path $PSScriptRoot 'GeneratedFlatRefinement.cs') -ReferencedAssemblies System.Drawing
Add-Type -Path (Join-Path $PSScriptRoot '../AnimationPackaging.cs') -ReferencedAssemblies System.Drawing
$soraReference=Join-Path $soraReady "run_loop/$soraTrial/whole_frame_review_v1/sora_run_loop_00.png"
$soraUpper=@(115,108,95,76,55,45,50,65,88,108,120,121)
$soraFore=@(-145,-133,-107,0,10,15,10,5,-86,-123,-148,-151)
$soraLoopRecords=[System.Collections.Generic.List[object]]::new()
$soraStopRecords=[System.Collections.Generic.List[object]]::new()
foreach($soraAnimation in @('run_loop','run_stop')){
    $soraOut=Join-Path $soraReady "$soraAnimation/$soraTrial/$Version"
    New-Item -ItemType Directory -Path $soraOut,(Join-Path $soraOut 'frames_128') | Out-Null
    for($soraIndex=0;$soraIndex -lt 12;$soraIndex++){
        $soraFile=('sora_{0}_{1:00}.png' -f $soraAnimation,$soraIndex);$soraTarget=Join-Path $soraOut $soraFile
        if($soraAnimation -eq 'run_loop'){
            $soraSource=Join-Path $soraReady "$soraAnimation/$soraTrial/whole_frame_review_v1/$soraFile"
            $soraJoints=[GeneratedFlatRefinement]::Paint($soraSource,$soraReference,$soraTarget,$soraUpper[$soraIndex],$soraFore[$soraIndex],$false,$false)
            $soraLoopRecords.Add([pscustomobject][ordered]@{index=$soraIndex;file=$soraFile;source=$soraSource;sourceSha256=(Get-FileHash -LiteralPath $soraSource -Algorithm SHA256).Hash.ToLowerInvariant();durationMs=80;eyeY=$soraJoints[0];upperAngle=$soraUpper[$soraIndex];forearmAngle=$soraFore[$soraIndex];shoulder=@($soraJoints[1],$soraJoints[2]);elbow=@($soraJoints[3],$soraJoints[4]);wrist=@($soraJoints[5],$soraJoints[6]);upperLength=40.4969;forearmLength=36;sha256=(Get-FileHash -LiteralPath $soraTarget -Algorithm SHA256).Hash.ToLowerInvariant()})
        }else{
            # A whole-pose carry-order study, not a claim of newly drawn braking legs.
            $soraLoopIndices=@(0,1,2,5,8)
            if($soraIndex -lt 5){$soraSource=Join-Path $soraReady ('run_loop/{0}/{1}/sora_run_loop_{2:00}.png' -f $soraTrial,$Version,$soraLoopIndices[$soraIndex])}
            else{$soraSource=Join-Path $soraReady ('run_stop/{0}/whole_frame_review_v1/sora_run_stop_{1:00}.png' -f $soraTrial,$soraIndex)}
            Copy-Item -LiteralPath $soraSource -Destination $soraTarget
            $soraDurations=@(80,80,100,80,100,100,100,100,120,120,120,200)
            $soraStopRecords.Add([pscustomobject][ordered]@{index=$soraIndex;file=$soraFile;source=$soraSource;sourceSha256=(Get-FileHash -LiteralPath $soraSource -Algorithm SHA256).Hash.ToLowerInvariant();durationMs=$soraDurations[$soraIndex];method='Unchanged complete-pose selection';sha256=(Get-FileHash -LiteralPath $soraTarget -Algorithm SHA256).Hash.ToLowerInvariant()})
        }
    }
}
foreach($soraAnimation in @('run_loop','run_stop')){
    $soraOut=Join-Path $soraReady "$soraAnimation/$soraTrial/$Version"
    $soraRecords=if($soraAnimation -eq 'run_loop'){$soraLoopRecords.ToArray()}else{$soraStopRecords.ToArray()}
    $soraBoard=[System.Drawing.Bitmap]::new(1024,840);$soraBoardG=[System.Drawing.Graphics]::FromImage($soraBoard);$soraBoardG.Clear([System.Drawing.Color]::White)
    $soraSheet=[System.Drawing.Bitmap]::new(2048,1536,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb);$soraSheetG=[System.Drawing.Graphics]::FromImage($soraSheet)
    $soraFont=[System.Drawing.Font]::new('Arial',10)
    $soraLarge=[System.Collections.Generic.List[System.Drawing.Bitmap]]::new();$soraSmall=[System.Collections.Generic.List[System.Drawing.Bitmap]]::new()
    foreach($soraRecord in $soraRecords){
        $soraImage=[System.Drawing.Bitmap]::new((Join-Path $soraOut $soraRecord.file));$soraIndex=$soraRecord.index
        $soraCol=$soraIndex%4;$soraRow=[Math]::Floor($soraIndex/4)
        $soraSheetG.DrawImageUnscaled($soraImage,$soraCol*512,$soraRow*512)
        $soraBoardG.DrawImage($soraImage,[int]($soraCol*256),[int]($soraRow*280),256,256)
        $soraBoardG.DrawString(('Study{0:00}' -f $soraIndex),$soraFont,[System.Drawing.Brushes]::Black,$soraCol*256+8,$soraRow*280+257)
        foreach($soraSize in @(512,128)){
            $soraFlat=[System.Drawing.Bitmap]::new($soraSize,$soraSize);$soraG=[System.Drawing.Graphics]::FromImage($soraFlat);$soraG.Clear([System.Drawing.Color]::White)
            $soraG.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic;$soraG.DrawImage($soraImage,0,0,$soraSize,$soraSize);$soraG.Dispose()
            if($soraSize -eq 512){$soraLarge.Add($soraFlat)}else{$soraSmall.Add($soraFlat)}
        }
        $soraGame=[System.Drawing.Bitmap]::new(128,128,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb);$soraG=[System.Drawing.Graphics]::FromImage($soraGame)
        $soraG.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic;$soraG.DrawImage($soraImage,0,0,128,128);$soraG.Dispose()
        $soraGame.Save((Join-Path $soraOut "frames_128/$($soraRecord.file)"),[System.Drawing.Imaging.ImageFormat]::Png);$soraGame.Dispose();$soraImage.Dispose()
    }
    $soraBoard.Save((Join-Path $soraOut 'Contact_Sheet.png'),[System.Drawing.Imaging.ImageFormat]::Png);$soraSheet.Save((Join-Path $soraOut 'Sprite_Sheet_512.png'),[System.Drawing.Imaging.ImageFormat]::Png)
    foreach($soraSize in @(512,128)){
        $soraFrames=if($soraSize -eq 512){$soraLarge.ToArray()}else{$soraSmall.ToArray()};$soraSuffix=if($soraAnimation -eq 'run_loop'){'Loop'}else{'Once'}
        $soraGif=Join-Path $soraOut "Preview_${soraSize}_${soraSuffix}.gif"
        [AnimationPackaging]::Gif($soraGif,$soraFrames,[int[]]@($soraRecords | ForEach-Object durationMs))
        if($soraAnimation -eq 'run_stop'){
            $soraBytes=[System.IO.File]::ReadAllBytes($soraGif)
            if([System.Text.Encoding]::ASCII.GetString($soraBytes,16,11) -ne 'NETSCAPE2.0'){throw 'Unexpected GIF header'}
            [System.IO.File]::WriteAllBytes($soraGif,[byte[]]($soraBytes[0..12]+$soraBytes[32..($soraBytes.Length-1)]))
        }
    }
    $soraManifest=[ordered]@{status='Motion refinement study; unfinished art and joins, not game integration';animation=$soraAnimation;frameCount=12;loop=($soraAnimation -eq 'run_loop');durationMs=($soraRecords | Measure-Object durationMs -Sum).Sum;canvas=@(512,512);gameExport=@(128,128);method=if($soraAnimation -eq 'run_loop'){'Complete generated canvases with articulated free arm painted using one whole-image reference brush and direct jacket/skin strokes; no component raster layers.'}else{'Complete-pose carry-order selection: loop00,01,02,05,08, then original stop05-11. No new braking-leg drawings.'};frames=$soraRecords;limitations=@('Arm-to-jacket contour and shadow joins still need art refinement.','Generated leg roles, contacts, body jitter and loop wrap are not corrected by this arm study.','Stop opening pose selection fixes carry chronology but foot paths and joins remain provisional.','Weapon proportions across original sheets, foreground projection and final idle alignment remain unverified.','Stop painting pilots contain waist seams and are not inserted.','No Godot or actual-browser playback test.')}
    $soraManifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $soraOut 'manifest.json') -Encoding UTF8
    $soraBoardG.Dispose();$soraBoard.Dispose();$soraSheetG.Dispose();$soraSheet.Dispose();$soraFont.Dispose();foreach($soraBitmap in @($soraLarge.ToArray())+@($soraSmall.ToArray())){$soraBitmap.Dispose()}
}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'GeneratedFlatRefinement.cs') -Destination (Join-Path $soraReady "run_loop/$soraTrial/$Version/Flat_Painter_Source.cs")
Write-Output 'Complete arm-motion and stop carry-order studies created; inspect before promotion.'
