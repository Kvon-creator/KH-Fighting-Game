# Sora Quick Run special

**Fact or rule:** Kvon (November 18): Sora gets Wisdom Form's Quick Run (KH2) as a special: he uses it to move past the opponent and appear behind them. Light = the run only (no follow-up). Medium = hits the opponent from behind and knocks them back. Heavy = a 3-hit follow-up whose last hit bounces the opponent off the ground into the air to lead into a combo. Input "down forward L/M/H".
Decisions (Kvon picked the recommended options, November 18):
- **Input:** quarter circle forward (down, down-forward, forward) + L / M / H, with a short motion buffer; holding down-forward + a button still does crouching attacks.
- **Pass-through:** strikes pass through Sora during the run, grabs still catch him; he passes through the opponent and stops just behind them; out of range he runs a fixed distance.
- **Numbers:** Medium follow-up 900, big knockback, no knockdown. Heavy follow-up 300 / 300 / 600 (1200), the 3rd hit = ground bounce high enough to juggle. Both follow-ups are blockable (hold away from Sora's new side). Light recovers fast.
- **Order:** mechanics first with existing drawings as stand-ins (to feel and tune), then the new Quick Run drawings, then the follow-up drawings.

**Why:** Kvon's request; the options were chosen by Kvon from my suggestions (the held diagonal would clash with crouching attacks).

**Step 1 built (November 18) - mechanics with STAND-IN drawings** (`fighter.gd`: QCF_* / QR_* / QR_HITS / BOUNCE_*, `_qcf_done`, `_start_quick_run`, `_qr_step`, `_end_run`, `hit_info`; `match.gd` `_hits` uses `hit_info()`):
- Stand-ins: run = the glide's push-off (8 frames startup), hover loop, skid (Light, 12 frames); Medium = Standing Medium drawings; Heavy = Standing Light, Medium, Heavy drawings (faster holds). `STAND_IN` maps them to the source animation for shifts / smears; hitboxes come with the drawings. Replace with the real drawings in steps 2-3.
- Run 34 px/frame, stops 140 px behind an opponent within 860 px in front (homes if they move), else 520 px; the match skips push-apart and turning while he runs; `_find_hit` ignores a running fighter.
- Heavy hits 1-2 have a 30-frame stun and almost no push so the string always combos and the bounce stays in reach; hit 3: 5 frames on the floor (hurt_down drawing), then up at 14 px/frame (LAUNCH_GRAVITY). Normal damage scaling applies (300 / 240 / 360 from a fresh start).
- Only from neutral (GROUND_CANCEL moves), ground only; no cancels into or out of it (not requested); the CPU doesn't use it.
- Tested headless: all three versions; Heavy = combo 1-2-3 then Crouching Heavy juggles (combo 4); Medium guarded by the auto-guard dummy; the dummy's Medium hits him in the startup but passes through mid-run at the same spacing; held down-forward + L = Crouching Light; normal moves unchanged (same trace as before). Demo flag `--qcf-demo-at=N` (+ `--light-demo-at=N` etc.).
