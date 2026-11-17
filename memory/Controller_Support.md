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

**Browser (GitHub Pages) build (Kvon, November 17: "give the Pages version of the game controller compatibility"):** the controller code already used standard button names, which map to the browser's standard gamepad layout (a DualSense in Chrome reports it). Added: (1) a browser can't see a controller until one of its buttons is pressed (Godot web docs) - menu.gd shows "Controller: press any button on it to connect" in web builds (OS.has_feature("web")) until Input.joy_connection_changed reports one; (2) that waking press also arrives as a normal press and started Player vs. Player - the menu now ignores presses for 300 ms after a controller connects; (3) the touchpad press isn't in the standard web layout, so **L3 also resets Training** (all builds). Tested in headless Chrome with a simulated standard-layout DualSense (scratch script gp_test.mjs overrides navigator.getGamepads): hint, connect, menu navigation, Square attack, D-pad walk, L3 reset. Not tested with a real DualSense in a browser; Firefox may report a non-standard layout. A controller still can't leave Training back to the menu (Esc only) - not added.
