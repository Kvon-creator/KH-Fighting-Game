# Input buffer (5 frames, everywhere)

**Fact or rule (Kvon, November 11):** "Go for the 5-frame buffer and apply it to all of the available inputs": attack recovery, landing, blockstun, hitstun and wake-up (plus the hit-freeze, which already had a one-frame version).

**Why:** Kvon asked after I explained attack buffering (comparable games: SF6 4 frames, Strive ~5); no further reason given.

**Built (fighter.gd):** INPUT_BUFFER 5, BUFFERED_KEYS up / light / medium / heavy / dash (the grab = Medium + Heavy). `_press_at[k]` = the game frame of the last new press, recorded every frame in every state (`_record_presses`, also during hit-freeze via `buffer_input`). A press counts while `_tick - press <= 5`: up to 5 frames before the first frame he can act. A move that uses a press clears it (`_use`) so it can't come out twice (e.g. a buffered jump becoming a double jump). Cleared when he is hit / grabbed / knocked down (`_end_moves`) and on reset. Directions (forward / back) are NOT buffered - double taps start glides and back-dashes. Replaced the old `_buffered` dict; presses during hitstun no longer get thrown away.
**Grab buffer (Kvon, November 11: "a bit longer"):** GRAB_BUFFER 8 - Medium + Heavy both pressed up to 8 frames before he can act still gives the grab (attacks / jump / dash stay at 5). Tested: 8 early yes, 9 early no.
**Tested:** recovery (Medium 3 frames before the Light's end -> first actionable frame; 8 early -> dropped), landing (Medium during a jL cut by the landing -> first ground frame), hitstun (5 early yes, 6 early no), wake-up (5 yes, 6 no), blockstun, double jump, L -> M chain, grab, CPU match - no errors.
