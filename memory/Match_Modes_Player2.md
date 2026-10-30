# Menu, Player vs. Player / CPU, Training (Kvon, October 29)

**Fact or rule:** Kvon: "Make the dummy Sora in his limit form. I also want to add a screen that allows you to go into a Player vs. Player match or Player vs. CPU. The controls for player two will be with the arrow keys to move and 7, 8, and 9 for the attacks." Answers:
- P2: arrow keys move (Up jump, Down crouch), **number pad 7 / 8 / 9** = light / medium / heavy. **P1 becomes WASD only** (+ U / I / O).
- CPU: **simple fighter AI** (walks in / backs off, attacks in range incl. lows and jump-ins, guards some attacks, sometimes launches and juggles; beatable).
- Match end: **best of 3 rounds** ("K.O." + winner; first to 2 round wins, then back to the menu).
- Facing: **fighters always face each other** (turn around when they cross; on the ground at once, in the air on landing); "back" = away from the opponent, also for guarding.
- Menu: **Player vs. Player / Player vs. CPU / Training** (Training = the current standing dummy with G guard modes, F1 boxes).
- Limit Form: Blender 5.2 has no Collada (.dae) importer any more, and the Limit Form rig has 284 numbered bones (bone000-283) vs. the KH2 Sora rig's 49 named ones - **I write a small .dae importer** (no install) and map bones by position; **menu + player 2 first** (P2 = normal Sora meanwhile), then re-render every animation as Limit Form for P2 / the dummy.
- Kvon OK'd removing design/models/sora/atk_guard_v1 (done).

**Why:** Kvon's answers; no further reasons given.

## Built (October 29) - step 1: menu, PvP, PvCPU, Training on a two-fighter match
- `scripts/fighter.gd` (class_name Fighter): one Sora - all movement/attacks (moved from sora_move_test.gd), facing (sprite scale.x; root motion, dashes and air speed x facing), states control / stun / guard / hurt_air / down, take_hit (guard_pose: players hold back - crouch blocks low+mid, stand blocks mid+overhead, air blocks all; not while attacking/dashing/reeling; dummy guard modes), knockdown, KO (stays down), hitstun decay per fighter (combo_hits).
- `scripts/match.gd` on `scenes/match.tscn` (and `scenes/sora_move_test.tscn` now uses it as the Training scene - its labels updated, old `scripts/sora_move_test.gd` is unused): mode from `get_tree().root` meta "mode" / `--mode=`; P1 WASD + U/I/O (no arrows any more), P2 arrows + KP 7/8/9; fighters face each other (turn on the ground at once, in the air on landing); hits both ways (trades), freeze, pushback, middle-box pushing, effects, KH bars with names + round markers, announcer (ROUND n / FIGHT! / K.O. / X WINS THE ROUND / X WINS!), best of 3 then back to the menu, Esc = menu; training: G guard modes, H/J tests, R reset, health refills. CPU = `_cpu_input` (plans of held buttons: approach / back off / pokes / lows / launcher / jump-in heavy, 50% guard reaction to a new attack within 330 px, juggle after a launch).
- `scripts/menu.gd` on `scenes/menu.tscn`: KINGDOM ARENA title, 3 buttons (mouse, W/S/arrows, Enter/Space/U), ignores input for 0.25 s.
- Test flags: P1 demo flags as before + same with `p2-` prefix; `--start-hp=N`; menu `--pick=n`, `--capture=`.
- Tested: training results identical to before (medium HIT 84, launcher combo 161/214, guard modes, push 873/1051, H/J/air guard); PvP best of 3 -> menu; P2 demo walk + heavy; crossover turn-around; CPU vs idle P1 (all attack types, hits) and vs attacking P1 (guards some); menu picks; screenshots.
- Kvon authorized ("Yes to both", October 29): project.godot `run/main_scene` changed to `res://scenes/menu.tscn` (F5 opens the menu) and the unused `scripts/sora_move_test.gd` (+ .uid) deleted; Training still runs from `scenes/sora_move_test.tscn` or the menu. These were one-time authorizations for those two changes, not standing permission for protected files.
- Next: step 2 = Limit Form importer + re-render for P2 / CPU / dummy.
