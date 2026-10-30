extends Node2D
## Movement test for Sora: battle idle by default. Hold D or Right to shuffle forward, A or Left
## to shuffle back. The shuffle's first drawing is the idle stance, so it starts straight from the
## idle; when the key is released he finishes the current step (back to the idle stance) and
## stands. Hold S or Down to crouch (Keyblade in one hand); release to stand back up. Crouching
## wins over walking; during a step he crouches once the step finishes. Double-tap D or Right and
## hold to glide low across the floor; on release he skids to a stop into the idle. Press W or Up to
## jump straight up (takeoff, then the air drawing follows his vertical speed, then the landing; keep it
## held to jump again as soon as he is upright on the ground);
## press it again in the air for the second jump (an upright spin, like KH2's Aerial Dodge), or
## double-tap D or Right in the air to air-dash forward (once each per jump). Double-tap A or Left to
## back-dash: a low backward hop on the ground, or a backward air dash (sharing the one air dash).
## Hold D/Right or A/Left in the air to drift that way.
## Hurt tests (no opponent yet): H = a hit (on the ground he snaps back and recovers; in the air he is
## knocked down), J = a knockdown from the ground (launched back, head-first fall, lands on his back, lies
## there a moment, then gets up).
## U = Standing Light (a guard bash), I = Standing Medium (a batter-style slash with Keyblade smears),
## O = Standing Heavy (an advancing downward slash); while standing or walking.
## U while holding S or Down = Crouching Light (a low jab from the kneel); I while holding S or Down =
## Crouching Medium (a lunging low sweep); O while holding S or Down = Crouching Heavy (an overhead Keyblade
## thrust that launches). U / I / O in the air = Jumping Light (a quick level
## slash) / Jumping Medium (a spinning diagonal strike) / Jumping Heavy (a two-handed overhead chop).
## R resets his position.
## Automated checks: `-- --walk-demo-ticks=N` holds forward for N game frames, `-- --back-demo-ticks=N`
## holds back, `-- --crouch-demo-ticks=N` holds crouch (from game frame `--crouch-demo-from=M`,
## default 1), `-- --glide-demo-ticks=N` double-taps forward (held on frames 1-3 and 7-N),
## `-- --jump-demo-at=N` presses jump on game frame N (`--jump2-demo-at=M` presses it again,
## `--dash-demo-at=M` double-taps forward from frame M); `--bdash-demo-at=N` double-taps back;
## `--hit-demo-at=N` / `--knock-demo-at=N` / `--light-demo-at=N` / `--medium-demo-at=N` / `--heavy-demo-at=N` press H / J /
## U / I / O on
## game frame N;
## `--capture=<png path>` saves a screenshot after 1.5 s and quits.
## `--show-boxes` starts with the F1 hitbox / hurtbox view on.
##
## Animation is stepped once per physics tick (60 per second, the project default), like a
## fighting game: each drawing is held an exact number of game frames.

## Floor surface of arena.tscn.
const FLOOR_Y := 600.0
## Pixel in each 384 x 384 frame that sits on the floor (shared by every Sora animation).
const FEET := Vector2(192, 354)
## Animations drawn on taller 384 x 576 frames (the Crouching Heavy's overhead thrust): the extra 192 px are
## added above him, so his feet sit 192 px lower in the frame.
const TALL_FEET := {&"attack_cheavy": Vector2(192, 354 + 192)}
## How far he may walk toward either screen edge.
const LEFT_LIMIT := 120.0
const RIGHT_LIMIT := 1280.0 - 120.0
## The second forward press must come within this many game frames of the first to start a glide.
const DOUBLE_TAP_FRAMES := 15
## The glide push-off ends on the loop's first pose, so it hands over to this glide_loop drawing.
const GLIDE_ENTRY_DRAWING := 1
## Jump: peak height in px and game frames from leaving the floor to the peak; gravity and launch
## speed follow from these. Kvon: the Jumping Heavy (24 game frames) must be able to finish when pressed at
## the very top, so the same 200 px jump rises and falls more slowly - 26 frames each way (was 18, a 0.6 s hop).
const JUMP_HEIGHT := 200.0
const JUMP_RISE_FRAMES := 26.0
const JUMP_GRAVITY := 2.0 * JUMP_HEIGHT / (JUMP_RISE_FRAMES * JUMP_RISE_FRAMES)
const JUMP_SPEED := JUMP_GRAVITY * JUMP_RISE_FRAMES
## Second jump: launch speed as a share of the first jump's (about two-thirds of its height; Kvon asked
## for a little higher than 0.7). Used at the very top of the first jump, his hair can pass the top of
## this fixed test screen by ~25 px.
const JUMP2_SPEED := JUMP_SPEED * 0.8
## Second jump sideways push (Kvon: travel a little further): px per game frame in the held direction.
const JUMP2_VX := 7.0
## Game frames into the second jump at which the post-spin swing-up drawing ends (22 spin + 3).
const SPIN_SWING_END := 25
## Forward air-dash: game frames for the tuck, burst, dash 1, dash 2 and brake, and px moved forward per
## game frame in each (about 190 px in all).
## (Kvon: the air dashes linger slightly longer and carry momentum.) About 255 px in all.
const AIR_DASH_HOLDS := [3, 3, 6, 6, 4]
const AIR_DASH_SPEED := [4.0, 10.0, 16.0, 16.0, 6.0]
## Back-dash (double-tap back): push, hop, hop 2, touch down, settle - game frames and px per game frame
## (negative = backward). On the ground he hops low along BACK_DASH_HEIGHT; in the air only the push and
## hops play, then he falls. Kvon: the hop lingers slightly longer and carries further (~245 px).
const BACK_DASH_HOLDS := [2, 7, 7, 3, 4]
const BACK_DASH_SPEED := [-6.0, -17.0, -14.0, -5.0, 0.0]
const BACK_DASH_HEIGHT := 32.0
## Sideways speed (px per game frame) an air dash leaves him with; it fades by AIR_DRAG each frame.
const AIR_DASH_CARRY := 7.0
const AIR_DRAG := 0.9
## Air steering (Kvon: move left and right in the air without dashing): holding D/Right or A/Left eases
## his sideways speed toward this many px per game frame (240 px/s).
const AIR_STEER_SPEED := 6.0
const AIR_STEER_ACCEL := 0.6
## Jump carry (Kvon: a decent distance and angle out of a walk, magnified out of a ground dash): the
## sideways speed a jump keeps, px per game frame. Holding the same way keeps it; letting go slows it a
## little (AIR_COAST); holding the other way turns him around.
const WALK_JUMP_VX := 5.0
const GLIDE_JUMP_VX := 12.0
const BACK_DASH_JUMP_VX := 9.0
const AIR_COAST := 0.98
## Simple camera: the arena view's centre, the highest pixel row of Sora's hair in his 384 px frames,
## how far below the top of the screen his head is kept, how quickly the camera eases (per game frame),
## and the sky colour painted above the background.
const SCREEN_CENTER := Vector2(640, 360)
const HEAD_TOP_ROW := 60.0
const CAMERA_MARGIN := 40.0
const CAMERA_EASE := 0.25
const SKY_COLOR := Color8(19, 28, 57)
## Knockdown: launch speed (px per game frame, about 145 px high and half a second in the air), backward
## push, game frames for air hit 1, air hit 2 and the first three falling drawings (the last falling
## drawing is held until he lands), and how long he lies on the floor before standing. (Kvon: faster from
## the first air pose to the last - 12 game frames instead of 23.)
## The knockdown keeps the original (18-frame jump) gravity, so it is unchanged by the slower jump.
const HURT_GRAVITY := 2.0 * JUMP_HEIGHT / (18.0 * 18.0)
const KNOCK_SPEED := HURT_GRAVITY * 18.0 * 0.85
const KNOCK_VX := 5.0
const HURT_AIR_HOLDS := [2, 4, 2, 2, 2]
const LIE_FRAMES := 30  # Kvon: less time on the floor (was 60)
## Ground moves any of which a jump, back-dash or glide may cancel at once.
const GROUND_CANCEL := [&"idle", &"shuffle_forward", &"shuffle_back", &"crouch_down", &"crouch_hold",
	&"crouch_up", &"glide_start", &"glide_loop", &"glide_stop", &"jump_land"]
const GLIDE_ANIMS := [&"glide_start", &"glide_loop", &"glide_stop"]
## name -> [folder, file prefix, game frames per drawing, root motion in px per drawing,
## optional file numbers in play order (crouch_up is crouch_down backwards)]
## Root motion is how far his body moves as each drawing starts, taken from the render (metres x
## 180.5 px per metre), so planted feet stay exactly in place: 64.5 px per 20-frame cycle, ~193 px/s.
const ANIMATIONS := {
	&"idle": ["res://assets/sora/idle_battle_384/", "sora_idle_",
		[6, 5, 5, 6, 7, 6, 5, 5, 6, 7], []],
	&"shuffle_forward": ["res://assets/sora/shuffle_fwd_384/", "sora_shuffle_fwd_",
		[3, 3, 2, 4, 2, 3, 3], [1.61, 8.07, 14.51, 9.67, 9.67, 14.51, 6.44]],
	&"shuffle_back": ["res://assets/sora/shuffle_back_384/", "sora_shuffle_back_",
		[3, 3, 2, 4, 2, 3, 3], [-1.61, -8.07, -14.51, -9.67, -9.67, -14.51, -6.44]],
	&"crouch_down": ["res://assets/sora/crouch_down_384/", "sora_crouch_down_",
		[2, 1, 1, 1, 2, 2, 3], []],
	&"crouch_hold": ["res://assets/sora/crouch_hold_384/", "sora_crouch_hold_",
		[6, 5, 5, 7, 6, 5, 5, 7], []],
	&"crouch_up": ["res://assets/sora/crouch_down_384/", "sora_crouch_down_",
		[3, 2, 2, 1, 1, 1, 2], [], [6, 5, 4, 3, 2, 1, 0]],
	# Low ground glide (replaces the run; from Gemini's concept art): push-off, a hovering loop at
	# 900 px/s (Kvon: faster; no planted feet, so it can stop after any drawing), skid landing into the idle.
	&"glide_start": ["res://assets/sora/glide_start_384/", "sora_glide_start_",
		[2, 2, 3, 3], [5.42, 21.66, 27.07, 43.32]],
	&"glide_loop": ["res://assets/sora/glide_loop_384/", "sora_glide_loop_",
		[3, 3, 3, 3, 3, 3], [45.0, 45.0, 45.0, 45.0, 45.0, 45.0]],
	&"glide_stop": ["res://assets/sora/glide_stop_384/", "sora_glide_stop_",
		[2, 3, 3, 3, 3], [45.0, 27.07, 13.54, 5.42, 0.0]],
	# Jump: takeoff on the ground, then one "air" animation whose drawing is picked from his vertical
	# speed each game frame (rising 1, rising 2, apex, swing up, falling 1, falling 2), then the landing.
	# Takeoff (Kvon: instant cancels): 3 game frames from standing, 2 when already moving.
	&"jump_start": ["res://assets/sora/jump_start_384/", "sora_jump_start_", [1, 1, 1], []],
	&"jump_air": ["res://assets/sora/jump_rise_384/", "sora_jump_rise_", [1, 1, 1, 1, 1, 1], [],
		[0, 1, 0, 0, 1, 2], ["sora_jump_rise_", "sora_jump_rise_", "sora_jump_apex_", "sora_jump_fall_",
		"sora_jump_fall_", "sora_jump_fall_"], ["res://assets/sora/jump_rise_384/",
		"res://assets/sora/jump_rise_384/", "res://assets/sora/jump_apex_384/", "res://assets/sora/jump_fall_384/",
		"res://assets/sora/jump_fall_384/", "res://assets/sora/jump_fall_384/"]],
	&"jump_land": ["res://assets/sora/jump_land_384/", "sora_jump_land_", [3, 3, 4], []],
	# Second jump: the apex pose spinning on his vertical axis in 30-degree steps (2 game frames each).
	&"jump_spin": ["res://assets/sora/jump_spin_384/", "sora_jump_spin_", [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], []],
	# Forward air-dash: burst, dash 1, dash 2, brake (timed by AIR_DASH_HOLDS in _air_step).
	&"jump_dash": ["res://assets/sora/jump_dash_384/", "sora_jump_dash_", [3, 4, 4, 3], []],
	# Back-dash: push, hop, hop 2, touch down, settle (timed by BACK_DASH_HOLDS).
	&"back_dash": ["res://assets/sora/back_dash_384/", "sora_back_dash_", [2, 7, 7, 3, 4], []],
	# Hurt (Kvon's approved set): ground hit with a short knockback; air hit, head-first fall and the
	# knockdown on his back are timed by HURT_AIR_HOLDS and _down_step.
	&"hurt_ground": ["res://assets/sora/hurt_ground_384/", "sora_hurt_ground_", [2, 6, 5, 4],
		[-10.0, -14.0, -4.0, 0.0]],
	&"hurt_air": ["res://assets/sora/hurt_air_384/", "sora_hurt_air_", [4, 8], []],
	&"hurt_fall": ["res://assets/sora/hurt_fall_384/", "sora_hurt_fall_", [3, 4, 4, 4], []],
	&"hurt_down": ["res://assets/sora/hurt_down_384/", "sora_hurt_down_", [3, 4, 6], []],
	# Get-up after lying down (Kvon approved): sit up, tuck, crouch, rise, settle. The lying drawing is centred
	# in its frame but the get-up stands on the usual feet spot, so the first drawing shifts him to keep his
	# hips in place.
	&"hurt_getup": ["res://assets/sora/hurt_getup_384/", "sora_hurt_getup_", [4, 4, 4, 3, 3],
		[8.0, 0.0, 0.0, 0.0, 0.0]],
	# Standing Light (U; Kvon approved): a bunt-style guard bash - set, bash, recoil, return to the idle.
	&"attack_light": ["res://assets/sora/attack_light_384/", "sora_attack_light_", [6, 3, 6, 7], []],  # Kvon: startup 6, active 3, recovery 13
	# Standing Medium (I; Kvon: fine for now): batter-style horizontal slash. Startup 9 (rise x2, raised, wind-up,
	# slash start), active 3 (impact), recovery 17 (wrap, follow-through, recover, return) - between the Light and
	# Ekko's heavy (13/3/21), since Ekko's reference move is a heavy.
	&"attack_medium": ["res://assets/sora/attack_medium_384/", "sora_attack_medium_", [1, 1, 2, 3, 2, 3, 3, 5, 5, 4],
		[]],
	# Standing Heavy (O): an advancing downward slash (Kvon; Sol's 6H as reference) - lift, overhead, back foot steps
	# up, front foot strides as the Key comes down, impact lunge, follow-through, recover, back foot steps up, idle.
	# Startup 13, active 3, recovery 21 (Ekko's heavy). Root motion from the render (~101 px forward in all).
	&"attack_heavy": ["res://assets/sora/attack_heavy_384/", "sora_attack_heavy_", [2, 4, 3, 4, 3, 5, 6, 5, 5],
		[0.0, -3.61, 21.65, 21.65, 94.61, 3.61, -18.04, -2.2, -16.64]],
	# Crouching Light (U while crouching; Kvon approved v30): a low jab from the kneel - chamber, drive, hit, hold,
	# return, back in the crouch guard. Startup 5, active 3, recovery 12.
	&"attack_clight": ["res://assets/sora/attack_clight_384/", "sora_attack_clight_", [2, 3, 3, 4, 4, 4], []],
	# Crouching Medium (I while crouching; Kvon approved v23, after Ky's 2S): from the kneel the forearm tucks under
	# the chin, he lunges out, the Key circles level over his head, comes round flat at waist height and sweeps low
	# behind him, then he draws back into the crouch guard. Kvon: too fast to see the details - startup 13,
	# active 4, recovery 18 (was 9 / 3 / 17).
	&"attack_cmedium": ["res://assets/sora/attack_cmedium_384/", "sora_attack_cmedium_", [3, 4, 3, 3, 4, 6, 12], []],
	# Crouching Heavy (O while crouching; Kvon liked v8, after Sora's SSBU up smash): a grounded upward launcher -
	# gather low with the Key upright, rise while turning away, thrust it straight up overhead one-handed with his
	# chest to the background (the hit), hold with the knee up, tip it back and settle into the crouch guard.
	# Startup 11, active 4, recovery 22. Drawn on taller 384 x 576 frames (see TALL_FEET).
	&"attack_cheavy": ["res://assets/sora/attack_cheavy_384/", "sora_attack_cheavy_", [6, 5, 4, 8, 5, 4, 5], []],
	# Jumping Light (U in the air; Kvon approved v7, after Ky's GGST j.S): from the jump tuck the Key draws back over
	# his shoulder, a quick level slash at chest height with the front knee up, follow-through, back to the tuck.
	# Startup 5, active 3, recovery 9; the jump keeps moving him meanwhile (timed in _air_step).
	&"attack_jlight": ["res://assets/sora/attack_jlight_384/", "sora_attack_jlight_", [2, 3, 3, 4, 5], []],
	# Jumping Medium (I in the air; Kvon: v7 "looks good for now", after Simon's SSBU back air): a clockwise 3/4 spin
	# with the Key overhead into a diagonal strike with his back to the camera, reach, arm level, back to the tuck.
	# Startup 8, active 3, recovery 12.
	&"attack_jmedium": ["res://assets/sora/attack_jmedium_384/", "sora_attack_jmedium_", [2, 3, 3, 3, 3, 4, 5], []],
	# Jumping Heavy (O in the air; Kvon: v2 "That's good", after Trunks' DBFZ j.H): a two-handed overhead slash -
	# lift, wind-up behind the head, over the top, chop down in front, low, rise, back to the tuck. Kvon: must
	# finish when pressed at the very top of a jump but stay slower than the Medium - startup 10, active 3,
	# recovery 11 (24 frames vs the Medium's 23; was 11 / 4 / 18).
	&"attack_jheavy": ["res://assets/sora/attack_jheavy_384/", "sora_attack_jheavy_", [2, 4, 4, 3, 5, 3, 3], []],
}

## Drawings drawn shifted LEFT inside their frame so a long reach fits (the Standing Medium's full extension);
## the sprite is shifted back right by this many px so he stays in place.
const DRAW_SHIFT := {&"attack_medium": [0, 0, 0, 0, 0, 90, 30, 0, 0, 0],
	&"attack_heavy": [0, 0, 0, 0, 72, 30, 0, 0, 0],
	&"attack_clight": [0, 45, 82.5, 75, 0, 0],
	&"attack_cmedium": [0, -22.5, -30, 82.5, -60, 0, 0],
	&"attack_jlight": [0, 0, 45, 0, 0],
	&"attack_jmedium": [0, 0, 0, 90, 52.5, 82.5, 0],
	&"attack_jheavy": [0, 0, 0, 52.5, 0, 0, 0]}
## Drawings drawn shifted UP inside their frame (the Jumping Heavy's low chop): shifted back down by this many px.
const DRAW_SHIFT_Y := {&"attack_jheavy": [0, 0, 0, 15, 15, 0, 0]}
## Keyblade smear layers (separate from the body art, drawn on top of it), one texture per drawing.
const SMEARS := {&"attack_medium": ["res://assets/sora/attack_medium_smear_384/", "sora_attack_medium_smear_"],
	&"attack_light": ["res://assets/sora/attack_light_smear_384/", "sora_attack_light_smear_"],
	&"attack_heavy": ["res://assets/sora/attack_heavy_smear_384/", "sora_attack_heavy_smear_"],  # Kvon: a small streak on the bash
	&"attack_clight": ["res://assets/sora/attack_clight_smear_384/", "sora_attack_clight_smear_"],
	&"attack_cmedium": ["res://assets/sora/attack_cmedium_smear_384/", "sora_attack_cmedium_smear_"],
	&"attack_cheavy": ["res://assets/sora/attack_cheavy_smear_384/", "sora_attack_cheavy_smear_"],
	&"attack_jlight": ["res://assets/sora/attack_jlight_smear_384/", "sora_attack_jlight_smear_"],
	&"attack_jmedium": ["res://assets/sora/attack_jmedium_smear_384/", "sora_attack_jmedium_smear_"],
	&"attack_jheavy": ["res://assets/sora/attack_jheavy_smear_384/", "sora_attack_jheavy_smear_"]}

## Combat (Kvon, October 29): hurtboxes / hitboxes for every drawing (generated by make_boxes.py), a training
## dummy Sora on the right until player 2 exists, 10000 health each, Light / Medium / Heavy damage 300 / 500 / 800,
## F1 shows the boxes (red = hitbox, blue = hurtbox), Kingdom Hearts style health bars at the top.
const BOXES := preload("res://scripts/sora_boxes.gd")
const MAX_HP := 10000
const DUMMY_X := 860.0
## Game frames the red "just lost" part of a health bar waits before draining, and how fast it drains (HP/frame).
const LOST_HP_DELAY := 30
const LOST_HP_DRAIN := 120.0
## Per attack strength (Kvon): damage, hit-freeze (both fighters stop, game frames) and hitstun (game frames the one
## hit is stuck reeling; its hurt animation is stretched to it).
const DAMAGE := {&"light": 300, &"medium": 500, &"heavy": 800}
const HIT_FREEZE := {&"light": 11, &"medium": 13, &"heavy": 16}
const HITSTUN := {&"light": 15, &"medium": 19, &"heavy": 23}
## Launcher (the Crouching Heavy; Kvon: launch + air juggle): the one launched flies up about 250 px under a light
## gravity (Sora's jump gravity, so he can jump after it); every hit while it is airborne pops it up a little; it
## drifts away from the attacker, then lands into the knockdown (lie down, get up), untouchable until it stands.
const LAUNCH_SPEED := 17.2
const JUGGLE_SPEED := 7.0
const LAUNCH_VX := 1.5

var _sprite: AnimatedSprite2D
var _smear: Sprite2D
var _smear_frames := {}
var _camera: Camera2D
var _start_x := 420.0
## Game frames to hold forward / back / crouch in the timed demos (-1 = not used).
var _demo_forward_ticks := -1
var _demo_back_ticks := -1
var _demo_crouch_ticks := -1
var _demo_crouch_from := 1
var _demo_glide_ticks := -1
var _demo_jump_at := -1
## `--jump-hold-to=N` keeps the demo jump held from `--jump-demo-at` through game frame N.
var _demo_jump_hold := -1
var _demo_jump2_at := -1
var _demo_dash_at := -1
## Second jump: whether it has been used in this jump, and game frames into its spin (-1 = not spinning).
var _jump2_used := false
var _spin_tick := -1
## Game frames into the air attack being played (-1 = none); the jump keeps moving him meanwhile.
var _air_atk_tick := -1
## Which air attack is playing (attack_jlight / attack_jmedium / attack_jheavy).
var _air_atk_anim := &"attack_jlight"
## Forward air-dash: whether it has been used in this jump, game frames into it (-1 = not dashing),
## and whether he is falling after one (the falling drawing then skips the swing-up).
var _dash_used := false
var _dash_tick := -1
var _after_dash := false
## Which air dash is running (true = back-dash), sideways momentum in px per game frame, the ground
## back-dash's game frame (-1 = not back-dashing), and back double-tap tracking.
var _dash_back := false
var _vx := 0.0
## Held left/right in the air this frame (-1, 0 or 1).
var _air_input := 0.0
## Sideways speed the next jump leaves the floor with.
var _takeoff_vx := 0.0
var _bd_tick := -1
var _back_was := false
var _last_back_press := -1000
var _demo_bdash_at := -1
## Hurt: game frames into the knocked-back air time and into the knockdown on the floor (-1 = not
## running), the H / J keys last frame, and the timed demo presses.
var _hurt_tick := -1
var _down_tick := -1
var _hit_was := false
var _knock_was := false
var _demo_hit_at := -1
var _demo_knock_at := -1
## Standing Light: the U key last frame and the timed demo press (`--light-demo-at=N`).
var _light_was := false
var _demo_light_at := -1
## Standing Medium: the I key last frame and the timed demo press (`--medium-demo-at=N`).
var _medium_was := false
var _demo_medium_at := -1
## Standing Heavy: the O key last frame and the timed demo press (`--heavy-demo-at=N`).
var _heavy_was := false
var _demo_heavy_at := -1
## Jump state: vertical speed in px per game frame (negative = up) while airborne, and whether the
## jump key was held last frame (a jump starts on a new press).
var _air := false
var _vy := 0.0
var _jump_was := false
var _tick := 0
## Game frames the current drawing has been shown.
var _hold := 0
## Double-tap tracking: forward held last frame, the frame it was last pressed, and whether the
## current hold is a glide.
var _forward_was := false
var _last_forward_press := -1000
var _glide := false
## `--trace` prints every drawing change (game frame, animation, drawing, x) for automated checks.
var _trace := false
## Combat: the training dummy, both health values (0 = Sora, 1 = dummy / player 2), the red trailing health,
## whether the current attack has already hit, and the box view.
var _dummy: AnimatedSprite2D
var _dummy_hold := 0
## Dummy state: &"idle", &"stun" (reeling for _dummy_stun frames), &"air" (launched / juggled), &"down" (knocked
## down: lying, then getting up).
var _dummy_state := &"idle"
var _dummy_stun := 0
var _dummy_stun_len := 1
var _dummy_tick := 0
var _dummy_vx := 0.0
var _dummy_vy := 0.0
## Game frames the launched dummy has been coming down (its head-first fall is timed from the top of the arc).
var _dummy_fall := 0
## Hit-freeze frames left (both fighters stop while it counts down).
var _freeze := 0
## Real game frames run (counts through hit-freeze too; _tick is Sora's own clock and pauses).
var _frames := 0
var _hp := [MAX_HP, MAX_HP]
var _lost_hp := [float(MAX_HP), float(MAX_HP)]
var _lost_wait := [0, 0]
var _attack_hit := false
var _show_boxes := false
var _box_view: Node2D
var _bars: Control


func _ready() -> void:
	var frames := SpriteFrames.new()
	for anim: StringName in ANIMATIONS:
		frames.add_animation(anim)
		var folder: String = ANIMATIONS[anim][0]
		var prefix: String = ANIMATIONS[anim][1]
		var order: Array = ANIMATIONS[anim][4] if ANIMATIONS[anim].size() > 4 \
			else range(ANIMATIONS[anim][2].size())
		for k in order.size():
			# Optional per-drawing prefix/folder lists (the jump's air drawings come from several folders).
			var pre: String = ANIMATIONS[anim][5][k] if ANIMATIONS[anim].size() > 5 else prefix
			var dir: String = ANIMATIONS[anim][6][k] if ANIMATIONS[anim].size() > 6 else folder
			frames.add_frame(anim, load(dir + pre + "%02d.png" % order[k]) as Texture2D)

	_sprite = AnimatedSprite2D.new()
	_sprite.sprite_frames = frames
	_sprite.centered = false
	_sprite.offset = -FEET
	_sprite.position = Vector2(_start_x, FLOOR_Y)
	add_child(_sprite)
	# Smear layer: a child of the sprite (so it moves with him and draws on top), shown only on smeared drawings.
	_smear = Sprite2D.new()
	_smear.centered = false
	_smear.visible = false
	_sprite.add_child(_smear)
	for anim: StringName in SMEARS:
		var list: Array[Texture2D] = []
		for k in ANIMATIONS[anim][2].size():
			list.append(load(SMEARS[anim][0] + SMEARS[anim][1] + "%02d.png" % k) as Texture2D)
		_smear_frames[anim] = list

	# Simple camera (Kvon): fixed on the arena, it only rises when Sora's head nears the top of the screen
	# (a high second jump) and never goes below the floor or sideways. The area above the background
	# painting is filled with its sky colour so nothing shows empty.
	var sky := ColorRect.new()
	sky.color = SKY_COLOR
	sky.position = Vector2(0, -600)
	sky.size = Vector2(1280, 600)
	sky.z_index = -10
	add_child(sky)
	move_child(sky, 0)
	_camera = Camera2D.new()
	_camera.position = SCREEN_CENTER
	_camera.limit_left = 0
	_camera.limit_right = 1280
	_camera.limit_bottom = 720
	add_child(_camera)
	_camera.make_current()
	_show(&"idle")

	# Training dummy: a second Sora on the right facing left (mirrored with a negative x scale, so the feet stay
	# on its position like Sora's). It stands in the idle and plays the ground hit when struck.
	_dummy = AnimatedSprite2D.new()
	_dummy.sprite_frames = frames
	_dummy.centered = false
	_dummy.scale = Vector2(-1, 1)
	_dummy.position = Vector2(DUMMY_X, FLOOR_Y)
	add_child(_dummy)
	_dummy_show(&"idle", 0)
	# Box view: draws every box in world coordinates on top of the fighters while F1 is on.
	_box_view = Node2D.new()
	_box_view.z_index = 50
	_box_view.draw.connect(_draw_boxes)
	add_child(_box_view)
	# Health bars: drawn on the HUD layer (fixed on screen, not moved by the camera).
	_bars = Control.new()
	_bars.size = Vector2(1280, 720)
	_bars.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_bars.draw.connect(_draw_bars)
	$HUD.add_child(_bars)

	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--walk-demo-ticks="):
			_demo_forward_ticks = int(arg.trim_prefix("--walk-demo-ticks="))
		elif arg.begins_with("--back-demo-ticks="):
			_demo_back_ticks = int(arg.trim_prefix("--back-demo-ticks="))
		elif arg.begins_with("--crouch-demo-ticks="):
			_demo_crouch_ticks = int(arg.trim_prefix("--crouch-demo-ticks="))
		elif arg.begins_with("--crouch-demo-from="):
			_demo_crouch_from = int(arg.trim_prefix("--crouch-demo-from="))
		elif arg.begins_with("--glide-demo-ticks="):
			_demo_glide_ticks = int(arg.trim_prefix("--glide-demo-ticks="))
		elif arg.begins_with("--hit-demo-at="):
			_demo_hit_at = int(arg.trim_prefix("--hit-demo-at="))
		elif arg.begins_with("--heavy-demo-at="):
			_demo_heavy_at = int(arg.trim_prefix("--heavy-demo-at="))
		elif arg.begins_with("--medium-demo-at="):
			_demo_medium_at = int(arg.trim_prefix("--medium-demo-at="))
		elif arg.begins_with("--light-demo-at="):
			_demo_light_at = int(arg.trim_prefix("--light-demo-at="))
		elif arg.begins_with("--knock-demo-at="):
			_demo_knock_at = int(arg.trim_prefix("--knock-demo-at="))
		elif arg.begins_with("--bdash-demo-at="):
			_demo_bdash_at = int(arg.trim_prefix("--bdash-demo-at="))
		elif arg.begins_with("--dash-demo-at="):
			_demo_dash_at = int(arg.trim_prefix("--dash-demo-at="))
		elif arg.begins_with("--jump2-demo-at="):
			_demo_jump2_at = int(arg.trim_prefix("--jump2-demo-at="))
		elif arg.begins_with("--jump-hold-to="):
			_demo_jump_hold = int(arg.trim_prefix("--jump-hold-to="))
		elif arg.begins_with("--jump-demo-at="):
			_demo_jump_at = int(arg.trim_prefix("--jump-demo-at="))
		elif arg == "--trace":
			_trace = true
		elif arg.begins_with("--dummy-x="):
			_dummy.position.x = float(arg.trim_prefix("--dummy-x="))  # tests: start the dummy elsewhere
		elif arg == "--show-boxes":
			_show_boxes = true  # the F1 box view on from the start (recordings)
		elif arg.begins_with("--capture="):
			_capture(arg.trim_prefix("--capture="))


func _physics_process(_delta: float) -> void:
	if _freeze > 0:
		_freeze -= 1  # hit-freeze: everyone holds still (the bars still drain)
	else:
		_sora_step()
		_dummy_step()
		_push_apart()
		_check_hits()
	_drain_lost_hp()
	_box_view.queue_redraw()
	_bars.queue_redraw()
	_frames += 1
	if _trace and _frames % 4 == 0:
		print("POS ", _frames, " sora=", snappedf(_sprite.position.x, 0.1), " dummy=",
			snappedf(_dummy.position.x, 0.1), ",", snappedf(_dummy.position.y, 0.1), " ", _dummy_state,
			" freeze=", _freeze)


## One game frame of Sora: read the input and move him / pick his drawing.
func _sora_step() -> void:
	_tick += 1
	_follow_camera()
	var forward := _tick <= _demo_forward_ticks or Input.is_physical_key_pressed(KEY_D) \
		or Input.is_physical_key_pressed(KEY_RIGHT) \
		or (_demo_glide_ticks > 0 and (_tick <= 3 or (_tick >= 7 and _tick <= _demo_glide_ticks))) \
		or (_demo_dash_at > 0 and (_tick - _demo_dash_at) in [0, 1, 5, 6])
	var back := _tick <= _demo_back_ticks or Input.is_physical_key_pressed(KEY_A) \
		or Input.is_physical_key_pressed(KEY_LEFT) \
		or (_demo_bdash_at > 0 and (_tick - _demo_bdash_at) in [0, 1, 5, 6])
	# A new back press soon after the previous one is a back-dash (on the ground or in the air).
	var back_tap := false
	if back and not _back_was:
		back_tap = _tick - _last_back_press <= DOUBLE_TAP_FRAMES
		_last_back_press = _tick
	_back_was = back
	var crouch := (_demo_crouch_from <= _tick and _tick <= _demo_crouch_ticks) \
		or Input.is_physical_key_pressed(KEY_S) or Input.is_physical_key_pressed(KEY_DOWN)
	# A new forward press soon after the previous one is a double tap: glide while it stays held (on the
	# ground) or air-dash (in the air).
	var double_tap := false
	if forward and not _forward_was:
		_glide = _tick - _last_forward_press <= DOUBLE_TAP_FRAMES
		double_tap = _glide
		_last_forward_press = _tick
	if not forward:
		_glide = false
	_forward_was = forward
	var wanted: StringName = &"crouch_down" if crouch else (
		&"shuffle_forward" if forward and not back else (
		&"shuffle_back" if back and not forward else &"idle"))
	var glide_wanted := _glide and wanted == &"shuffle_forward"
	var anim := _sprite.animation
	var jump := _tick == _demo_jump_at or _tick == _demo_jump2_at \
		or (_demo_jump_at > 0 and _demo_jump_at <= _tick and _tick <= _demo_jump_hold) \
		or Input.is_physical_key_pressed(KEY_W) or Input.is_physical_key_pressed(KEY_UP)
	var jump_pressed := jump and not _jump_was
	_jump_was = jump
	# Hurt tests: being hit overrides whatever he is doing (except lying on the floor).
	var hit := _tick == _demo_hit_at or Input.is_physical_key_pressed(KEY_H)
	var hit_pressed := hit and not _hit_was
	_hit_was = hit
	var knock := _tick == _demo_knock_at or Input.is_physical_key_pressed(KEY_J)
	var knock_pressed := knock and not _knock_was
	_knock_was = knock
	var light := _tick == _demo_light_at or Input.is_physical_key_pressed(KEY_U)
	var light_pressed := light and not _light_was
	_light_was = light
	var medium := _tick == _demo_medium_at or Input.is_physical_key_pressed(KEY_I)
	var medium_pressed := medium and not _medium_was
	_medium_was = medium
	var heavy := _tick == _demo_heavy_at or Input.is_physical_key_pressed(KEY_O)
	var heavy_pressed := heavy and not _heavy_was
	_heavy_was = heavy
	if _down_tick < 0 and (knock_pressed or (hit_pressed and (_air or _hurt_tick >= 0))):
		_start_knockdown(_air or _hurt_tick >= 0)
	elif _down_tick < 0 and hit_pressed:
		_bd_tick = -1
		_sprite.position.y = FLOOR_Y
		_show(&"hurt_ground")
		return
	if _hurt_tick >= 0:
		_hurt_air_step()
		return
	if _down_tick >= 0:
		_down_step()
		return
	if _air:
		_air_input = (1.0 if forward and not back else 0.0) - (1.0 if back and not forward else 0.0)
		if (double_tap or back_tap) and not _dash_used and _dash_tick < 0 and _spin_tick < 0 and _air_atk_tick < 0:
			_dash_used = true  # air dash (forward or back): a straight horizontal burst, once per jump
			_dash_back = back_tap and not double_tap
			_dash_tick = 0
			_after_dash = false
		elif (light_pressed or medium_pressed or heavy_pressed) and _dash_tick < 0 and _air_atk_tick < 0:
			# Jumping Light / Medium / Heavy (U / I / O): plays over the jump (no air-dash during it)
			_air_atk_anim = &"attack_jheavy" if heavy_pressed else (&"attack_jmedium" if medium_pressed
				else &"attack_jlight")
			_air_atk_tick = 0
			_spin_tick = -1
		elif jump_pressed and not _jump2_used and _dash_tick < 0:
			_jump2_used = true  # second jump: a new upward burst and the spin
			_air_atk_tick = -1
			_vy = -JUMP2_SPEED
			if _air_input != 0.0 and absf(_vx) < JUMP2_VX:
				_vx = _air_input * JUMP2_VX
			_spin_tick = 0
			_after_dash = false
		_air_step()
		return
	# Instant cancels (Kvon): any ground move - standing, walking, crouching, gliding, back-dashing or
	# landing - can be cancelled straight into a jump, a back-dash or a glide. A jump keeps the ground
	# speed he had: a decent arc from a walk, a much longer one out of a glide or back-dash.
	var back_dashing := _bd_tick >= 0
	# Held jump (Kvon): keep jumping as soon as he is upright on the ground again - the landing's last
	# (nearly standing) drawing, standing or walking; not during the crouched landing drawings.
	var upright := anim in [&"idle", &"shuffle_forward", &"shuffle_back"] or (anim == &"jump_land"
		and _sprite.frame == ANIMATIONS[&"jump_land"][2].size() - 1)
	if (jump_pressed and (back_dashing or anim in GROUND_CANCEL)) or (jump and upright and not back_dashing):
		_takeoff_vx = _ground_speed(anim, forward, back)
		var moving := absf(_takeoff_vx) > 0.0
		_bd_tick = -1
		_sprite.position.y = FLOOR_Y
		_show(&"jump_start", 1 if moving else 0)  # already moving: skip the crouch drawing
		return
	# Crouching Light (U while S/Down is held): from any ground move (not mid back-dash); like the standing
	# attacks it plays to the end (only a hit interrupts it), then he stays crouched or stands up.
	if light_pressed and not back_dashing and crouch and anim in GROUND_CANCEL:
		_sprite.position.y = FLOOR_Y
		_show(&"attack_clight")
		return
	# Standing Light (U): from any standing ground move (not crouching, not mid back-dash); it plays to the
	# end (only a hit interrupts it), then he returns to whatever is held.
	if light_pressed and not back_dashing and not crouch and anim in GROUND_CANCEL:
		_sprite.position.y = FLOOR_Y
		_show(&"attack_light")
		return
	# Crouching Medium (I while crouching): same rules as the Crouching Light.
	if medium_pressed and not back_dashing and crouch and anim in GROUND_CANCEL:
		_sprite.position.y = FLOOR_Y
		_show(&"attack_cmedium")
		return
	# Standing Medium (I): same rules as the Light.
	if medium_pressed and not back_dashing and not crouch and anim in GROUND_CANCEL:
		_sprite.position.y = FLOOR_Y
		_show(&"attack_medium")
		return
	# Crouching Heavy (O while crouching): same rules as the Crouching Light.
	if heavy_pressed and not back_dashing and crouch and anim in GROUND_CANCEL:
		_sprite.position.y = FLOOR_Y
		_show(&"attack_cheavy")
		return
	# Standing Heavy (O): same rules.
	if heavy_pressed and not back_dashing and not crouch and anim in GROUND_CANCEL:
		_sprite.position.y = FLOOR_Y
		_show(&"attack_heavy")
		return
	if back_tap and not back_dashing and anim in GROUND_CANCEL:
		_bd_tick = 0
		_back_dash_step()
		return
	if glide_wanted and (back_dashing or (anim in GROUND_CANCEL and not (anim in GLIDE_ANIMS))):
		_bd_tick = -1
		_sprite.position.y = FLOOR_Y
		_show(&"glide_start")
		return
	if back_dashing:
		_back_dash_step()
		return
	if crouch and anim in [&"shuffle_forward", &"shuffle_back", &"jump_land", &"glide_stop"]:
		_show(&"crouch_down")  # crouch at once instead of finishing the step or landing
		return
	if anim == &"jump_land" and wanted != &"idle":
		_show(wanted)  # walk out of a landing at once
		return
	if anim == &"idle" and wanted != &"idle":
		_show(wanted)  # drawing 1 of the shuffle is the idle stance; the crouch starts from it too
		return
	# Changing your mind halfway: crouch_up drawing k is crouch_down drawing 6 - k, so turn around
	# from the matching drawing instead of starting over.
	var last: int = ANIMATIONS[&"crouch_down"][2].size() - 1
	if anim == &"crouch_down" and not crouch:
		_show(&"crouch_up", last - _sprite.frame)
		return
	if anim == &"crouch_up" and crouch:
		_show(&"crouch_down", last - _sprite.frame)
		return
	if anim == &"crouch_hold" and not crouch:
		_show(&"crouch_up")
		return
	# Advance one game frame; move to the next drawing when this one's hold is used up.
	_hold += 1
	var holds: Array = ANIMATIONS[anim][2]
	if _hold >= holds[_sprite.frame]:
		var at_end := _sprite.frame + 1 == holds.size()
		if anim == &"jump_start" and at_end:
			_air = true  # leave the floor
			_vy = -JUMP_SPEED
			_jump2_used = false
			_spin_tick = -1
			_dash_used = false
			_dash_tick = -1
			_after_dash = false
			_dash_back = false
			_vx = _takeoff_vx
			_air_step()
		elif anim == &"glide_start" and at_end:
			_show(&"glide_loop", GLIDE_ENTRY_DRAWING)
		elif anim == &"glide_loop" and not glide_wanted:
			_show(&"glide_stop")  # hovering, nothing planted: land after any drawing
		elif anim == &"glide_loop" and at_end:
			_show(&"glide_loop")
		elif not at_end:
			_show(anim, _sprite.frame + 1)
		elif anim == &"idle":
			_show(&"idle")
		elif anim == &"crouch_down" or anim == &"crouch_hold":
			_show(&"crouch_hold")
		elif anim in [&"attack_clight", &"attack_cmedium", &"attack_cheavy"]:
			# It ends in the crouch guard: stay down, or stand up from the full crouch.
			_show(&"crouch_hold" if crouch else &"crouch_up")
		else:
			# End of a step cycle, standing up or the glide landing: the feet are in the idle stance, so
			# he can stand, crouch, switch direction or keep going without any pop.
			_show(wanted)


## One airborne game frame: move by the vertical speed, apply gravity, pick the air drawing from the
## speed, and land when the feet reach the floor.
func _air_step() -> void:
	if _dash_tick >= 0:
		# Air dash: no gravity, a straight horizontal move with its own drawings, holds and speeds. Forward:
		# brief tuck (the apex drawing), burst, dash 1, dash 2, brake. Back: push, hop, hop 2. Then he falls,
		# carrying some sideways momentum.
		var holds_d: Array = BACK_DASH_HOLDS.slice(0, 3) if _dash_back else AIR_DASH_HOLDS
		var speeds_d: Array = BACK_DASH_SPEED.slice(0, 3) if _dash_back else AIR_DASH_SPEED
		var step := _step_of(_dash_tick, holds_d)
		_dash_tick += 1
		if step < holds_d.size():
			_sprite.position.x = clampf(_sprite.position.x + speeds_d[step], LEFT_LIMIT, RIGHT_LIMIT)
			if _dash_back:
				if _sprite.animation != &"back_dash" or _sprite.frame != step:
					_show(&"back_dash", step)
			elif step == 0:
				if _sprite.animation != &"jump_air" or _sprite.frame != 2:
					_show(&"jump_air", 2)
			elif _sprite.animation != &"jump_dash" or _sprite.frame != step - 1:
				_show(&"jump_dash", step - 1)
			return
		_dash_tick = -1
		_vy = 0.0
		_vx = -AIR_DASH_CARRY if _dash_back else AIR_DASH_CARRY
		_after_dash = not _dash_back  # the forward brake already raised the Keyblade
	if _air_input != 0.0:
		# Steering: ease toward the held direction's speed; holding the same way as a faster carry keeps it.
		var target := _air_input * AIR_STEER_SPEED
		if absf(_vx) > AIR_STEER_SPEED and signf(_vx) == signf(target):
			pass
		else:
			_vx = move_toward(_vx, target, AIR_STEER_ACCEL)
	elif _after_dash or _dash_back:
		_vx *= AIR_DRAG  # dash momentum fades quickly when not steering
	else:
		_vx *= AIR_COAST
	_sprite.position.x = clampf(_sprite.position.x + _vx, LEFT_LIMIT, RIGHT_LIMIT)
	_sprite.position.y += _vy
	_vy += JUMP_GRAVITY
	if _sprite.position.y >= FLOOR_Y:
		_sprite.position.y = FLOOR_Y
		_air = false
		_spin_tick = -1
		_dash_tick = -1
		_air_atk_tick = -1  # landing cuts an air attack short
		_after_dash = false
		_vx = 0.0
		_show(&"jump_land")
		return
	if _air_atk_tick >= 0:
		# Air attack: its drawings by its own holds while the jump carries on; then the speed-picked air drawing.
		var holds_a: Array = ANIMATIONS[_air_atk_anim][2]
		var step_a := _step_of(_air_atk_tick, holds_a)
		_air_atk_tick += 1
		if step_a < holds_a.size():
			if _sprite.animation != _air_atk_anim or _sprite.frame != step_a:
				_show(_air_atk_anim, step_a)
			return
		_air_atk_tick = -1
	if _spin_tick >= 0:
		# Second-jump spin: one drawing every 2 game frames, then back to the speed-picked air drawing.
		var spin_drawing := _spin_tick / 2
		_spin_tick += 1
		if spin_drawing < ANIMATIONS[&"jump_spin"][2].size():
			if _sprite.animation != &"jump_spin" or _sprite.frame != spin_drawing:
				_show(&"jump_spin", spin_drawing)
			return
		if _spin_tick <= SPIN_SWING_END:
			# Then the swing-up drawing (air drawing 3) for a moment, so the Keyblade rises smoothly into the
			# falling pose instead of jumping straight to it.
			if _sprite.animation != &"jump_air" or _sprite.frame != 3:
				_show(&"jump_air", 3)
			return
		_spin_tick = -1
	var t := _vy / JUMP_SPEED  # -1 at launch, 0 at the peak, about +1 on landing
	var drawing := 0 if t < -0.55 else (1 if t < -0.15 else (2 if t <= 0.15 else (
		3 if t < 0.4 else (4 if t < 0.75 else 5))))
	if _after_dash:
		drawing = maxi(drawing, 4)  # the brake already raised the Keyblade: straight into falling 1
	if _sprite.animation != &"jump_air" or _sprite.frame != drawing:
		_show(&"jump_air", drawing)


## Raise the camera just enough to keep Sora's head CAMERA_MARGIN px below the top of the screen, easing
## there (and back down to the arena view once he comes down).
func _follow_camera() -> void:
	var head_y := _sprite.position.y - FEET.y + HEAD_TOP_ROW
	var target := minf(SCREEN_CENTER.y, head_y - CAMERA_MARGIN + SCREEN_CENTER.y)
	_camera.position.y = lerpf(_camera.position.y, target, CAMERA_EASE)


## Sideways speed (px per game frame) a jump starts with, from what he was doing on the ground.
func _ground_speed(anim: StringName, forward: bool, back: bool) -> float:
	if _bd_tick >= 0:
		return -BACK_DASH_JUMP_VX
	if anim in GLIDE_ANIMS:
		return GLIDE_JUMP_VX
	if anim == &"shuffle_forward" or (forward and not back):
		return WALK_JUMP_VX
	if anim == &"shuffle_back" or (back and not forward):
		return -WALK_JUMP_VX
	return 0.0


## Which step of a timed move a game frame falls in (the step count once it is over).
func _step_of(frame: int, holds: Array) -> int:
	var step := 0
	for h: int in holds:
		if frame < h:
			return step
		frame -= h
		step += 1
	return step


## One game frame of the ground back-dash: move back, hop low over the hop drawings, then the touch
## down and settle, then the idle.
func _back_dash_step() -> void:
	var step := _step_of(_bd_tick, BACK_DASH_HOLDS)
	if step >= BACK_DASH_HOLDS.size():
		_bd_tick = -1
		_sprite.position.y = FLOOR_Y
		_show(&"idle")
		return
	var hop_start: int = BACK_DASH_HOLDS[0]
	var hop_len: int = BACK_DASH_HOLDS[1] + BACK_DASH_HOLDS[2]
	var u := float(_bd_tick - hop_start) / hop_len
	_sprite.position.y = FLOOR_Y - (BACK_DASH_HEIGHT * sin(PI * u) if u > 0.0 and u < 1.0 else 0.0)
	_sprite.position.x = clampf(_sprite.position.x + BACK_DASH_SPEED[step], LEFT_LIMIT, RIGHT_LIMIT)
	_bd_tick += 1
	if _sprite.animation != &"back_dash" or _sprite.frame != step:
		_show(&"back_dash", step)


## Knocked back into the air (from the ground, or a hit while already airborne - a smaller pop up then).
func _start_knockdown(airborne: bool) -> void:
	_air = false  # the jump logic stays off; _hurt_air_step moves him instead
	_dash_tick = -1
	_spin_tick = -1
	_air_atk_tick = -1
	_bd_tick = -1
	_after_dash = false
	_vy = -KNOCK_SPEED * (0.5 if airborne else 1.0)
	_vx = -KNOCK_VX
	_hurt_tick = 0
	_down_tick = -1


## One game frame knocked back in the air: air hit, drift, then the head-first fall (its last drawing
## held), under the jump's gravity; on reaching the floor he lands on his back.
func _hurt_air_step() -> void:
	var step := _step_of(_hurt_tick, HURT_AIR_HOLDS)
	_hurt_tick += 1
	_vx *= AIR_COAST
	_sprite.position.x = clampf(_sprite.position.x + _vx, LEFT_LIMIT, RIGHT_LIMIT)
	_sprite.position.y += _vy
	_vy += HURT_GRAVITY
	if _sprite.position.y >= FLOOR_Y:
		_sprite.position.y = FLOOR_Y
		_hurt_tick = -1
		_vx = 0.0
		_down_tick = 0
		_show(&"hurt_down")
		return
	var anim: StringName = &"hurt_air" if step < 2 else &"hurt_fall"
	var drawing := step if step < 2 else mini(step - 2, 3)
	if _sprite.animation != anim or _sprite.frame != drawing:
		_show(anim, drawing)


## One game frame of the knockdown: shoulders hit, settle, lie flat for LIE_FRAMES, then get up (the get-up
## then plays like any ground animation and ends in the idle).
func _down_step() -> void:
	_down_tick += 1
	var holds: Array = ANIMATIONS[&"hurt_down"][2]
	var step := mini(_step_of(_down_tick, holds), holds.size() - 1)
	if _down_tick >= 13 + LIE_FRAMES:
		_down_tick = -1
		_show(&"hurt_getup")
		return
	if _sprite.frame != step:
		_show(&"hurt_down", step)


## Shows a drawing and applies its root motion as it starts.
func _show(anim: StringName, drawing: int = 0) -> void:
	_sprite.animation = anim
	_sprite.frame = drawing
	_hold = 0
	if drawing == 0 and String(anim).begins_with("attack_"):
		_attack_hit = false  # a new attack: it may hit once
	var shift: float = DRAW_SHIFT[anim][drawing] if DRAW_SHIFT.has(anim) else 0.0
	var shift_y: float = DRAW_SHIFT_Y[anim][drawing] if DRAW_SHIFT_Y.has(anim) else 0.0
	_sprite.offset = -(TALL_FEET[anim] if TALL_FEET.has(anim) else FEET) + Vector2(shift, shift_y)
	_smear.visible = _smear_frames.has(anim)
	if _smear.visible:
		_smear.texture = _smear_frames[anim][drawing]
		_smear.offset = _sprite.offset
	var motion: Array = ANIMATIONS[anim][3]
	if drawing < motion.size():
		_sprite.position.x = clampf(_sprite.position.x + motion[drawing], LEFT_LIMIT, RIGHT_LIMIT)
	if _trace:
		print("TRACE ", _tick, " ", anim, " ", drawing, " ", snappedf(_sprite.position.x, 0.01), " ",
			snappedf(_sprite.position.y, 0.01))


func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_R:
		_sprite.position.x = _start_x
		_hp = [MAX_HP, MAX_HP]  # reset also refills both health bars and stands the dummy back up
		_lost_hp = [float(MAX_HP), float(MAX_HP)]
		_dummy.position = Vector2(DUMMY_X, FLOOR_Y)
		_dummy_state = &"idle"
		_dummy_show(&"idle", 0)
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_F1:
		_show_boxes = not _show_boxes


## Shows a dummy drawing, placed like Sora's (feet on its position). Its root motion is mirrored (it faces left).
func _dummy_show(anim: StringName, drawing: int) -> void:
	_dummy.animation = anim
	_dummy.frame = drawing
	_dummy_hold = 0
	var shift: float = DRAW_SHIFT[anim][drawing] if DRAW_SHIFT.has(anim) else 0.0
	_dummy.offset = -FEET + Vector2(shift, 0)
	var motion: Array = ANIMATIONS[anim][3]
	if drawing < motion.size():
		_dummy.position.x = clampf(_dummy.position.x - motion[drawing], LEFT_LIMIT, RIGHT_LIMIT)


## One game frame of the dummy.
func _dummy_step() -> void:
	if _dummy_state == &"stun":
		# Reeling: the ground hit animation stretched over the hitstun, then back to the idle.
		_dummy_stun -= 1
		if _dummy_stun <= 0:
			_dummy_state = &"idle"
			_dummy_show(&"idle", 0)
			return
		var holds_h: Array = ANIMATIONS[&"hurt_ground"][2]
		var total := 0
		for h: int in holds_h:
			total += h
		var elapsed := int(float(_dummy_stun_len - _dummy_stun) * total / _dummy_stun_len)
		var step := mini(_step_of(elapsed, holds_h), holds_h.size() - 1)
		if _dummy.animation != &"hurt_ground" or _dummy.frame != step:
			_dummy_show(&"hurt_ground", step)
		return
	if _dummy_state == &"air":
		# Launched: Sora's knockdown drawings under the jump's gravity - the air hit and drift while it rises, the
		# head-first fall (timed from the top) once it comes down.
		var step_a := 0 if _dummy_tick < HURT_AIR_HOLDS[0] else 1
		if _dummy_vy >= 0.0:
			_dummy_fall += 1
			step_a = 2 + _step_of(_dummy_fall, HURT_AIR_HOLDS.slice(2))
		_dummy_tick += 1
		_dummy_vx *= AIR_COAST
		_dummy.position.x = clampf(_dummy.position.x + _dummy_vx, LEFT_LIMIT, RIGHT_LIMIT)
		_dummy.position.y += _dummy_vy
		_dummy_vy += JUMP_GRAVITY
		if _dummy.position.y >= FLOOR_Y:
			_dummy.position.y = FLOOR_Y
			_dummy_state = &"down"
			_dummy_tick = 0
			_dummy_show(&"hurt_down", 0)
			return
		var anim_a: StringName = &"hurt_air" if step_a < 2 else &"hurt_fall"
		var drawing_a := step_a if step_a < 2 else mini(step_a - 2, 3)
		if _dummy.animation != anim_a or _dummy.frame != drawing_a:
			_dummy_show(anim_a, drawing_a)
		return
	if _dummy_state == &"down":
		# Knocked down: like Sora's (shoulders hit, lie for LIE_FRAMES), then the get-up plays and ends in the idle.
		_dummy_tick += 1
		if _dummy.animation == &"hurt_down":
			var holds_d: Array = ANIMATIONS[&"hurt_down"][2]
			if _dummy_tick >= 13 + LIE_FRAMES:
				_dummy_show(&"hurt_getup", 0)
			else:
				var step_d := mini(_step_of(_dummy_tick, holds_d), holds_d.size() - 1)
				if _dummy.frame != step_d:
					_dummy_show(&"hurt_down", step_d)
			return
	# Idle loop, or the get-up playing through (then standing again).
	_dummy_hold += 1
	var holds: Array = ANIMATIONS[_dummy.animation][2]
	if _dummy_hold >= holds[_dummy.frame]:
		if _dummy.frame + 1 < holds.size():
			_dummy_show(_dummy.animation, _dummy.frame + 1)
		else:
			_dummy_state = &"idle"
			_dummy_show(&"idle", 0)


## The middle hurtbox (of a drawing's three, top to bottom) - the one used for pushing.
func _middle_box(spr: AnimatedSprite2D) -> Array[Rect2]:
	var all := _boxes(spr, BOXES.HURT)
	var out: Array[Rect2] = []
	if not all.is_empty():
		out.append(all[all.size() / 2])
	return out


## When the two fighters' middle hurtboxes touch they push each other apart (Kvon: only the middle boxes): the
## overlap is split between them, so walking into the other shoves it along at half speed; one against a screen
## edge can't move, so the other takes all of it.
func _push_apart() -> void:
	var overlap := 0.0
	for a: Rect2 in _middle_box(_sprite):
		for b: Rect2 in _middle_box(_dummy):
			if a.intersects(b):
				overlap = maxf(overlap, minf(a.end.x, b.end.x) - maxf(a.position.x, b.position.x))
	if overlap <= 0.0:
		return
	var side := 1.0 if _dummy.position.x >= _sprite.position.x else -1.0  # the dummy's side of Sora
	var dummy_to := clampf(_dummy.position.x + side * overlap * 0.5, LEFT_LIMIT, RIGHT_LIMIT)
	var moved := absf(dummy_to - _dummy.position.x)
	_dummy.position.x = dummy_to
	_sprite.position.x = clampf(_sprite.position.x - side * (overlap - moved), LEFT_LIMIT, RIGHT_LIMIT)


## A fighter's boxes for its current drawing in world coordinates (table = BOXES.HURT or BOXES.HIT). Boxes are
## stored in the drawing's own frame pixels, so they get the same offset as the sprite, and are mirrored for a
## fighter facing left (negative x scale).
func _boxes(spr: AnimatedSprite2D, table: Dictionary) -> Array[Rect2]:
	var out: Array[Rect2] = []
	var path := spr.sprite_frames.get_frame_texture(spr.animation, spr.frame).resource_path
	var key := path.get_base_dir().get_file() + "/" + path.get_file()
	if not table.has(key):
		return out
	for r: Rect2 in table[key]:
		var local := Rect2(spr.offset + r.position, r.size)
		if spr.scale.x < 0.0:
			local.position.x = -(local.position.x + local.size.x)
		out.append(Rect2(spr.position + local.position, local.size))
	return out


## Sora's attack hits the dummy when one of its hitboxes overlaps one of the dummy's hurtboxes - once per attack.
func _check_hits() -> void:
	if _attack_hit or _dummy_state == &"down":
		return  # one hit per attack; a knocked-down fighter can't be hit until it stands
	var hits := _boxes(_sprite, BOXES.HIT)
	if hits.is_empty():
		return
	for h: Rect2 in hits:
		for b: Rect2 in _boxes(_dummy, BOXES.HURT):
			if h.intersects(b):
				_attack_hit = true
				var attack := String(_sprite.animation)
				var strength := &"heavy" if attack.ends_with("heavy") else (&"medium" if attack.ends_with("medium")
					else &"light")
				_hp[1] = maxi(_hp[1] - DAMAGE[strength], 0)
				_lost_wait[1] = LOST_HP_DELAY
				_freeze = HIT_FREEZE[strength]
				var away := 1.0 if _dummy.position.x >= _sprite.position.x else -1.0
				if _sprite.animation == &"attack_cheavy" or _dummy_state == &"air":
					# The launcher sends it flying; any hit while it is in the air pops it up again (a juggle).
					var launch := _dummy_state != &"air"
					_dummy_state = &"air"
					_dummy_vy = -(LAUNCH_SPEED if launch else JUGGLE_SPEED)
					_dummy_vx = LAUNCH_VX * away
					_dummy_tick = 0
					_dummy_fall = 0
					_dummy_show(&"hurt_air", 0)
				else:
					_dummy_state = &"stun"
					_dummy_stun = HITSTUN[strength]
					_dummy_stun_len = _dummy_stun
					_dummy_show(&"hurt_ground", 0)
				if _trace:
					print("HIT ", _tick, " ", attack, " ", DAMAGE[strength], " dummy_hp=", _hp[1], " ", _dummy_state)
				return


## The red part of each bar (health just lost) waits a moment, then drains down to the real health.
func _drain_lost_hp() -> void:
	for i in 2:
		if _lost_wait[i] > 0:
			_lost_wait[i] -= 1
		else:
			_lost_hp[i] = move_toward(_lost_hp[i], float(_hp[i]), LOST_HP_DRAIN)


func _draw_boxes() -> void:
	if not _show_boxes:
		return
	for spr: AnimatedSprite2D in [_sprite, _dummy]:
		for r: Rect2 in _boxes(spr, BOXES.HURT):
			_box_view.draw_rect(r, Color(0.2, 0.5, 1.0, 0.22))
			_box_view.draw_rect(r, Color(0.3, 0.6, 1.0, 0.9), false, 2.0)
		for r: Rect2 in _middle_box(spr):
			_box_view.draw_rect(r, Color(1.0, 0.9, 0.2, 0.9), false, 2.0)  # yellow outline: the push box
		for r: Rect2 in _boxes(spr, BOXES.HIT):
			_box_view.draw_rect(r, Color(1.0, 0.15, 0.15, 0.28))
			_box_view.draw_rect(r, Color(1.0, 0.2, 0.2, 0.95), false, 2.0)


## Kingdom Hearts style health bars (Kvon): a dark frame with a light rim, a green bar with a bright top stripe
## and a darker bottom, red for health just lost. Sora's on the left, the dummy's (player 2's) on the right;
## each drains from its inner end toward the screen edge, with the name and health above it.
func _draw_bars() -> void:
	var font := ThemeDB.fallback_font
	var ink := Color8(10, 16, 40)
	for i in 2:
		var bar := Rect2(40.0 if i == 0 else 720.0, 34.0, 520.0, 20.0)
		_bars.draw_rect(bar.grow(4.0), ink)
		_bars.draw_rect(bar.grow(4.0), Color8(185, 200, 232), false, 2.0)
		_bars.draw_rect(bar, Color8(28, 34, 58))
		for part in 2:
			var share: float = (_lost_hp[i] if part == 0 else float(_hp[i])) / MAX_HP
			var w := bar.size.x * share
			var fill := Rect2(bar.position.x if i == 0 else bar.end.x - w, bar.position.y, w, bar.size.y)
			if part == 0:
				_bars.draw_rect(fill, Color8(214, 40, 40))
			else:
				_bars.draw_rect(fill, Color8(46, 196, 64))
				_bars.draw_rect(Rect2(fill.position, Vector2(w, 5)), Color8(150, 245, 150))
				_bars.draw_rect(Rect2(fill.position + Vector2(0, 15), Vector2(w, 5)), Color8(24, 128, 44))
		var label := "SORA" if i == 0 else "TRAINING DUMMY"
		var side := HORIZONTAL_ALIGNMENT_LEFT if i == 0 else HORIZONTAL_ALIGNMENT_RIGHT
		var other := HORIZONTAL_ALIGNMENT_RIGHT if i == 0 else HORIZONTAL_ALIGNMENT_LEFT
		var at := Vector2(bar.position.x, 26)
		_bars.draw_string_outline(font, at, label, side, bar.size.x, 18, 4, ink)
		_bars.draw_string(font, at, label, side, bar.size.x, 18, Color8(235, 240, 255))
		_bars.draw_string_outline(font, at, str(_hp[i]), other, bar.size.x, 16, 4, ink)
		_bars.draw_string(font, at, str(_hp[i]), other, bar.size.x, 16, Color8(170, 255, 170))


func _capture(path: String) -> void:
	await get_tree().create_timer(1.5).timeout
	await RenderingServer.frame_post_draw
	var error := get_viewport().get_texture().get_image().save_png(path)
	print("CAPTURE ", path, " error=", error, " x=", _sprite.position.x, " anim=", _sprite.animation)
	get_tree().quit()
