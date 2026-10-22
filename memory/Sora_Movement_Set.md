# Sora movement animation set

**Fact or rule (October22):** Sora's movement animations are made at 384 x 384, in the approved sprite2d_v3 style, starting from the approved battle_v12 stance, using the PS2-model pipeline. Kvon added to the earlier list (crouch down/hold/up, step forward/back shimmies, run start/loop/stop, KH1 first jump + KH2 Aerial Dodge second jump):

- **Back-dash:** a short hop backwards, the SAME animation on the ground and in the air.
- **Forward air-dash:** separate from the back-dash.
- **Landing.**
- **Air poses:** one for rising to the apex of the jump and one for falling from the apex.

**References:** `design/references/air_movement/air_movement_ref_01-04.png`. Kvon supplied these four stills of another fighting-game character's jump/air poses ("Think of the reference photo as an example"). They are pose references only, not Sora's design. Kvon's mapping:
  - ref_01 = rising toward the apex.
  - ref_02 = the apex tuck, and also the brief transition pose before any air option that needs another input.
  - ref_03 = falling toward the ground.
  - ref_04 = back-dash.

**Air transition rule:** Pose 1 (rising) -> Pose 2 (brief tuck) -> the air option. This applies to back-dash, forward-dash and any other air movement that needs an extra player input.

**Why:** User additions to the movement list.

**Keyblade during movement (October22):** Kvon said "One-handed, but he holds up high when he's falling."

- **Default (steps, crouch, run, rise, tuck, dashes, landing):** right hand only, held low and behind him, pointing away from the opponent; the left arm is free to move like the references.
- **Falling (ref_03 pose):** the Keyblade is raised up high in that hand.

**Why:** User decision.
