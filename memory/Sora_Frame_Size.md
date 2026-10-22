# Sora Sprite Frame Size

**Fact or rule:** Sora's base movement frames (idle, crouch, shimmies) use a 128 x 128 pixel canvas. A larger canvas (such as 160 x 160) will be adopted specifically for extended attack poses where weapon reach exceeds 128 pixels.

**Why:** K'von chose to maintain 128 x 128 for grounded movement and only adopt a larger canvas for extended attack swings after the idle canvas fit analysis.

**Display size increase, October22:** In the Godot test Kvon asked to "make the models bigger". The test scene now uses 192 x 192 frames (1.5x; soles on row 176, floor anchor (96,177)), downscaled with Lanczos from the 512px renders so they stay sharp. Sora is ~128 px tall on the 1280x720 screen. The 128 px set is kept. Whether 192 px becomes the standard frame size for all of Sora's animations is not yet confirmed; ask before producing the movement set.

**Bigger again, October22:** Kvon then said "Make them bigger again". The test scene now uses 256 x 256 frames (2x the 128px set; soles on row 235, floor anchor (128,236)); Sora is ~170 px tall on the 1280x720 screen. The 128/192 sets are kept. Whether 256 becomes the standard for the movement set is still to confirm.

**Bigger again (2), October22:** Kvon asked for bigger again. The test scene now uses 320 x 320 frames (2.5x; soles on row 294, floor anchor (160,295)); Sora is ~213 px tall (~30% of the 720 px screen height). Earlier sizes are kept. The standard for the movement set is still to confirm.
