# DualSense controller support (Kvon, November 6)

**Fact or rule:** Kvon connected a DualSense over Bluetooth "for testing purposes". Answers:
- The **first connected controller controls player 1**, together with the keyboard (WASD + U/I/O still work). P2 stays on arrows + numpad 7/8/9.
- **Square / Triangle / Circle = light / medium / heavy.** **R1 = dash** (November 6; dedicated button - Light + Medium is not a dash).
- **D-pad and left stick** move (up = jump, down = crouch); stick dead zone 0.5.
- **Menu:** D-pad / stick choose (Godot's built-in ui_up / ui_down already include them); **Cross starts** (Kvon asked for Cross specifically; the default ui_accept has no controller button, so menu.gd handles it).
- **Training only:** Create = dummy guard mode (G), touchpad press = reset (R), L1 = boxes (F1).
- Options = back to menu was offered and **not** chosen.

**Why:** Kvon's answers; no further reasons given.

**Built:** `scripts/match.gd` `_pad_input()` + `_unhandled_input` (Training buttons), `scripts/menu.gd` `_unhandled_input` (Cross). No project.godot / input map change. Tested with simulated controller events (menu nav, Cross pick, Training buttons). Live play with the pad was NOT tested: Windows listed the DualSense as paired but not connected at the time.
