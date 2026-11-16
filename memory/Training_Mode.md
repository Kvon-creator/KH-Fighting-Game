# Training Mode Dummy Commands

**Fact or rule:** Training mode's dummy (player 2) takes simple commands (Kvon, November 13: "allowing me to give the cpu simple commands. Reference training modes from other fighting games"). Modeled on Street Fighter 6's dummy Action / Guard / Counter settings and Guilty Gear Strive's enemy status + counter-attack (my reference choice, from general knowledge of those games, not looked up).
- **T (DualSense Options) = Action:** stand / crouch / jump (over and over) / light / medium / heavy attack / grab (every 60 game frames) / CPU (the match CPU fights back, guarding by holding back).
- **G (Create) = Guard:** off / standing / crouching / auto, as before. A jumping dummy with any guard on now guards in the air (before, standing / crouching guard could not block while airborne).
- **Y (R3) = Counter:** off / light attack / grab / jump - what it does on its first free frame after guarding, being hit or getting up (it taps the buttons through the 5-frame input buffer). It never presses buttons while held, so the counter never escapes Sora's grab.
- HUD: ACTION / GUARD / COUNTER lines under the dummy's bar (only ACTION while the CPU action is on), key guide along the bottom. Launch flags `--dummy-action=0-7`, `--dummy-counter=0-3`.
- Code: match.gd `_dummy_input`, `_set_dummy_action`, DUMMY_ACTIONS / COUNTER_KEYS; fighter.gd guard_pose air rule.

**Why:** Kvon's request; no further reason given.

**Testing note:** headless Godot runs need `--fixed-fps 60` with `--quit-after`, or far fewer game frames run than asked (demo presses late in the run never happen).
