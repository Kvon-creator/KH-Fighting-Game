# Sora Sprite Frame Size

**Fact or rule:** Sora's base movement frames (idle, crouch, shimmies) use a 128 x 128 pixel canvas. A larger canvas (such as 160 x 160) will be adopted specifically for extended attack poses where weapon reach exceeds 128 pixels.

**Why:** K'von chose to maintain 128 x 128 for grounded movement and only adopt a larger canvas for extended attack swings after the idle canvas fit analysis.

**Display size increase, October22:** In the Godot test Kvon asked to "make the models bigger". The test scene now uses 192 x 192 frames (1.5x; soles on row 176, floor anchor (96,177)), downscaled with Lanczos from the 512px renders so they stay sharp. Sora is ~128 px tall on the 1280x720 screen. The 128 px set is kept. Whether 192 px becomes the standard frame size for all of Sora's animations is not yet confirmed; ask before producing the movement set.
