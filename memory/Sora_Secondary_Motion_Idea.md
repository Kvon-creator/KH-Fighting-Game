# Pinned idea: hair and cloth follow-through

**Fact or rule:** On October22 Kvon asked how hard it would be to make Sora's hair strands move as he moves, like `design/references/Sora_battle_stance.gif`, then said to pin the idea for later revisions and focus on the basic animations now. Do not implement it until he brings it back.

**Plan when revived:** The PS2 model already has the bones: C_kami_a/b/c, L_kami_a/b and R_kami_a/b (hair spikes), plus hood, neckla1 (necklace) and L/R_suso (jacket tails). Add per-frame follow-through (lag, swing, settle relative to the head/body) in `build_sprite_pilot.py`, so every recipe gets it, then re-render the approved animations. The hair moves in clumps, one bone per spike group.

**Why:** User deferred it to keep focus on the basic movement set.
