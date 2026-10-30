class_name Fighter
extends Node2D
## One Sora on the stage - player 1, player 2, the CPU or the training dummy. match.gd creates two, feeds each
## one its buttons every game frame (step) and handles everything between them (hits, pushing, health bars).
## His movement and attacks are the approved Sora move set (moved here from the old one-Sora test script);
## he faces right (facing 1) or left (-1), and "forward" / "back" in his input are relative to that.
## Animation is stepped once per physics tick (60 per second, the project default), like a fighting game: each
## drawing is held an exact number of game frames.

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
	# Guard (Kvon): the Keyblade held across in front, both hands - one drawing each for standing, crouching and in
	# the air (held for the blockstun by the code).
	&"guard_stand": ["res://assets/sora/guard_384/", "sora_guard_", [1], [], [0]],
	&"guard_crouch": ["res://assets/sora/guard_384/", "sora_guard_", [1], [], [1]],
	&"guard_air": ["res://assets/sora/guard_384/", "sora_guard_", [1], [], [2]],
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

## Combat numbers (Kvon, October 29): 10000 health, damage / hit-freeze / hitstun / blockstun / pushback per strength.
const MAX_HP := 10000
const DAMAGE := {&"light": 300, &"medium": 500, &"heavy": 800}
const HIT_FREEZE := {&"light": 11, &"medium": 13, &"heavy": 16}
const HITSTUN := {&"light": 15, &"medium": 19, &"heavy": 23}
const BLOCKSTUN := {&"light": 11, &"medium": 15, &"heavy": 19}
const PUSHBACK := {&"light": 4.0, &"medium": 5.0, &"heavy": 6.0}
const PUSH_SLOW := 0.82
## Launcher (the Crouching Heavy; Kvon: launch + air juggle): the one launched flies up about 250 px under a light
## gravity (Sora's jump gravity, so the attacker can jump after it); every hit while it is airborne pops it up a
## little; it drifts away from the attacker, then lands into the knockdown (lie down, get up), untouchable until it
## stands. A fighter hit out of a jump is knocked down the same way.
const LAUNCH_SPEED := 17.2
const JUGGLE_SPEED := 7.0
const LAUNCH_VX := 1.5
## Hitstun decay (Kvon: per hit): each hit in the same combo gives 10% less hitstun and air pop, never below 40%.
const DECAY_PER_HIT := 0.1
const DECAY_FLOOR := 0.4

## Which way he faces: 1 = right, -1 = left. "Forward" / "back" in his input are relative to it.
var facing := 1.0
var hp := MAX_HP
## &"input": guards by holding back (players, the CPU). Training dummy modes: &"none", &"stand", &"crouch", &"auto".
var guard_mode := &"input"
## Prefix for --trace lines ("" = no trace). Player 1 prints "TRACE ..." like the old test scene.
var trace_tag := ""
var sprite: AnimatedSprite2D
## The current attack has already hit (one hit per attack).
var attack_hit := false
## Hits in the combo he is taking (hitstun decay), his pushback speed and direction (world), knocked out.
var combo_hits := 0
var push_v := 0.0
var push_dir := 1.0
var ko := false
## &"control" (moving / attacking by input), &"stun" (reeling), &"guard" (blocking), &"hurt_air" (launched,
## juggled or knocked down through the air), &"down" (lying, then getting up).
var state := &"control"

var _smear: Sprite2D
var _smear_frames := {}
var _tick := 0
var _hold := 0
var _air := false
var _vy := 0.0
var _vx := 0.0  # sideways speed in the air, relative to facing (+ = forward)
var _air_input := 0.0
var _takeoff_vx := 0.0
var _jump2_used := false
var _spin_tick := -1
var _air_atk_tick := -1
var _air_atk_anim := &"attack_jlight"
var _dash_used := false
var _dash_tick := -1
var _after_dash := false
var _dash_back := false
var _bd_tick := -1
var _glide := false
var _was := {}
var _last_forward_press := -1000
var _last_back_press := -1000
var _back_held := false
var _down_held := false
## Hurt states: frames left, length (for stretching the hurt animation), air speeds (world), gravity, timers.
var _stun := 0
var _stun_len := 1
var _hvx := 0.0
var _hvy := 0.0
var _hgrav := HURT_GRAVITY
var _htick := 0
var _hfall := 0


## Builds his sprite (sharing one SpriteFrames between fighters) and smear layer.
func setup(frames: SpriteFrames, smear_frames: Dictionary, start_x: float, face: float) -> void:
	sprite = AnimatedSprite2D.new()
	sprite.sprite_frames = frames
	sprite.centered = false
	sprite.offset = -FEET
	add_child(sprite)
	_smear = Sprite2D.new()
	_smear.centered = false
	_smear.visible = false
	sprite.add_child(_smear)
	_smear_frames = smear_frames
	reset(start_x, face)


## Back to standing at x, full health, facing face (round start / reset).
func reset(start_x: float, face: float) -> void:
	position = Vector2(start_x, FLOOR_Y)
	hp = MAX_HP
	ko = false
	state = &"control"
	combo_hits = 0
	push_v = 0.0
	_air = false
	_vx = 0.0
	_vy = 0.0
	_dash_tick = -1
	_spin_tick = -1
	_air_atk_tick = -1
	_bd_tick = -1
	_glide = false
	set_facing(face)
	show_anim(&"idle")


static func load_frames() -> SpriteFrames:
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
	return frames


static func load_smears() -> Dictionary:
	var out := {}
	for anim: StringName in SMEARS:
		var list: Array[Texture2D] = []
		for k in ANIMATIONS[anim][2].size():
			list.append(load(SMEARS[anim][0] + SMEARS[anim][1] + "%02d.png" % k) as Texture2D)
		out[anim] = list
	return out


func set_facing(face: float) -> void:
	facing = face
	sprite.scale.x = face


## Turns him to face dir if he can turn now: standing on the ground in control, not attacking, back-dashing or
## gliding (in the air he turns when he lands).
func face_toward(dir: float) -> void:
	if dir == facing or state != &"control" or _air or _bd_tick >= 0:
		return
	var anim := String(sprite.animation)
	if anim.begins_with("attack_") or sprite.animation in GLIDE_ANIMS or sprite.animation == &"jump_start":
		return
	set_facing(dir)


func is_attacking() -> bool:
	return String(sprite.animation).begins_with("attack_")


func is_airborne() -> bool:
	return _air or state == &"hurt_air"


## One game frame. inp holds this frame's held buttons: forward, back, up, down, light, medium, heavy.
func step(inp: Dictionary) -> void:
	_tick += 1
	_back_held = inp.get("back", false)
	_down_held = inp.get("down", false)
	if state != &"control":
		_hurt_step()
		for k: String in ["forward", "back", "up", "light", "medium", "heavy"]:
			_was[k] = inp.get(k, false)  # presses during hitstun don't come out afterwards
		return
	var forward: bool = inp.get("forward", false)
	var back: bool = inp.get("back", false)
	var crouch: bool = inp.get("down", false)
	var pressed := {}
	for k: String in ["forward", "back", "up", "light", "medium", "heavy"]:
		pressed[k] = inp.get(k, false) and not _was.get(k, false)
		_was[k] = inp.get(k, false)
	# A new back press soon after the previous one is a back-dash (on the ground or in the air).
	var back_tap := false
	if pressed["back"]:
		back_tap = _tick - _last_back_press <= DOUBLE_TAP_FRAMES
		_last_back_press = _tick
	# A new forward press soon after the previous one is a double tap: glide while it stays held (on the
	# ground) or air-dash (in the air).
	var double_tap := false
	if pressed["forward"]:
		_glide = _tick - _last_forward_press <= DOUBLE_TAP_FRAMES
		double_tap = _glide
		_last_forward_press = _tick
	if not forward:
		_glide = false
	var wanted: StringName = &"crouch_down" if crouch else (
		&"shuffle_forward" if forward and not back else (
		&"shuffle_back" if back and not forward else &"idle"))
	var glide_wanted := _glide and wanted == &"shuffle_forward"
	var anim := sprite.animation
	var jump: bool = inp.get("up", false)
	var jump_pressed: bool = pressed["up"]
	var light_pressed: bool = pressed["light"]
	var medium_pressed: bool = pressed["medium"]
	var heavy_pressed: bool = pressed["heavy"]
	if _air:
		_air_input = (1.0 if forward and not back else 0.0) - (1.0 if back and not forward else 0.0)
		if (double_tap or back_tap) and not _dash_used and _dash_tick < 0 and _spin_tick < 0 and _air_atk_tick < 0:
			_dash_used = true  # air dash (forward or back): a straight horizontal burst, once per jump
			_dash_back = back_tap and not double_tap
			_dash_tick = 0
			_after_dash = false
		elif (light_pressed or medium_pressed or heavy_pressed) and _dash_tick < 0 and _air_atk_tick < 0:
			# Jumping Light / Medium / Heavy: plays over the jump (no air-dash during it)
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
		and sprite.frame == ANIMATIONS[&"jump_land"][2].size() - 1)
	if (jump_pressed and (back_dashing or anim in GROUND_CANCEL)) or (jump and upright and not back_dashing):
		_takeoff_vx = _ground_speed(anim, forward, back)
		var moving := absf(_takeoff_vx) > 0.0
		_bd_tick = -1
		position.y = FLOOR_Y
		show_anim(&"jump_start", 1 if moving else 0)  # already moving: skip the crouch drawing
		return
	# Ground attacks: from any ground move (not mid back-dash); they play to the end (only a hit interrupts),
	# then he returns to whatever is held. Holding down gives the crouching version.
	if (light_pressed or medium_pressed or heavy_pressed) and not back_dashing and anim in GROUND_CANCEL:
		var strength := "heavy" if heavy_pressed else ("medium" if medium_pressed else "light")
		position.y = FLOOR_Y
		show_anim(StringName("attack_" + ("c" if crouch else "") + strength))
		return
	if back_tap and not back_dashing and anim in GROUND_CANCEL:
		_bd_tick = 0
		_back_dash_step()
		return
	if glide_wanted and (back_dashing or (anim in GROUND_CANCEL and not (anim in GLIDE_ANIMS))):
		_bd_tick = -1
		position.y = FLOOR_Y
		show_anim(&"glide_start")
		return
	if back_dashing:
		_back_dash_step()
		return
	if crouch and anim in [&"shuffle_forward", &"shuffle_back", &"jump_land", &"glide_stop"]:
		show_anim(&"crouch_down")  # crouch at once instead of finishing the step or landing
		return
	if anim == &"jump_land" and wanted != &"idle":
		show_anim(wanted)  # walk out of a landing at once
		return
	if anim == &"idle" and wanted != &"idle":
		show_anim(wanted)  # drawing 1 of the shuffle is the idle stance; the crouch starts from it too
		return
	# Changing your mind halfway: crouch_up drawing k is crouch_down drawing 6 - k, so turn around
	# from the matching drawing instead of starting over.
	var last: int = ANIMATIONS[&"crouch_down"][2].size() - 1
	if anim == &"crouch_down" and not crouch:
		show_anim(&"crouch_up", last - sprite.frame)
		return
	if anim == &"crouch_up" and crouch:
		show_anim(&"crouch_down", last - sprite.frame)
		return
	if anim == &"crouch_hold" and not crouch:
		show_anim(&"crouch_up")
		return
	# Advance one game frame; move to the next drawing when this one's hold is used up.
	_hold += 1
	var holds: Array = ANIMATIONS[anim][2]
	if _hold >= holds[sprite.frame]:
		var at_end := sprite.frame + 1 == holds.size()
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
			show_anim(&"glide_loop", GLIDE_ENTRY_DRAWING)
		elif anim == &"glide_loop" and not glide_wanted:
			show_anim(&"glide_stop")  # hovering, nothing planted: land after any drawing
		elif anim == &"glide_loop" and at_end:
			show_anim(&"glide_loop")
		elif not at_end:
			show_anim(anim, sprite.frame + 1)
		elif anim == &"idle":
			show_anim(&"idle")
		elif anim == &"crouch_down" or anim == &"crouch_hold":
			show_anim(&"crouch_hold")
		elif anim in [&"attack_clight", &"attack_cmedium", &"attack_cheavy"]:
			# It ends in the crouch guard: stay down, or stand up from the full crouch.
			show_anim(&"crouch_hold" if crouch else &"crouch_up")
		else:
			# End of a step cycle, standing up or the glide landing: the feet are in the idle stance, so
			# he can stand, crouch, switch direction or keep going without any pop.
			show_anim(wanted)


## One airborne game frame: move by the vertical speed, apply gravity, pick the air drawing from the
## speed, and land when the feet reach the floor.
func _air_step() -> void:
	if _dash_tick >= 0:
		# Air dash: no gravity, a straight horizontal move with its own drawings, holds and speeds. Forward:
		# brief tuck (the apex drawing), burst, dash 1, dash 2, brake. Back: push, hop, hop 2. Then he falls,
		# carrying some sideways momentum.
		var holds_d: Array = BACK_DASH_HOLDS.slice(0, 3) if _dash_back else AIR_DASH_HOLDS
		var speeds_d: Array = BACK_DASH_SPEED.slice(0, 3) if _dash_back else AIR_DASH_SPEED
		var step_d := _step_of(_dash_tick, holds_d)
		_dash_tick += 1
		if step_d < holds_d.size():
			position.x = clampf(position.x + speeds_d[step_d] * facing, LEFT_LIMIT, RIGHT_LIMIT)
			if _dash_back:
				if sprite.animation != &"back_dash" or sprite.frame != step_d:
					show_anim(&"back_dash", step_d)
			elif step_d == 0:
				if sprite.animation != &"jump_air" or sprite.frame != 2:
					show_anim(&"jump_air", 2)
			elif sprite.animation != &"jump_dash" or sprite.frame != step_d - 1:
				show_anim(&"jump_dash", step_d - 1)
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
	position.x = clampf(position.x + _vx * facing, LEFT_LIMIT, RIGHT_LIMIT)
	position.y += _vy
	_vy += JUMP_GRAVITY
	if position.y >= FLOOR_Y:
		_land()
		show_anim(&"jump_land")
		return
	if _air_atk_tick >= 0:
		# Air attack: its drawings by its own holds while the jump carries on; then the speed-picked air drawing.
		var holds_a: Array = ANIMATIONS[_air_atk_anim][2]
		var step_a := _step_of(_air_atk_tick, holds_a)
		_air_atk_tick += 1
		if step_a < holds_a.size():
			if sprite.animation != _air_atk_anim or sprite.frame != step_a:
				show_anim(_air_atk_anim, step_a)
			return
		_air_atk_tick = -1
	if _spin_tick >= 0:
		# Second-jump spin: one drawing every 2 game frames, then back to the speed-picked air drawing.
		var spin_drawing := _spin_tick / 2
		_spin_tick += 1
		if spin_drawing < ANIMATIONS[&"jump_spin"][2].size():
			if sprite.animation != &"jump_spin" or sprite.frame != spin_drawing:
				show_anim(&"jump_spin", spin_drawing)
			return
		if _spin_tick <= SPIN_SWING_END:
			# Then the swing-up drawing (air drawing 3) for a moment, so the Keyblade rises smoothly into the
			# falling pose instead of jumping straight to it.
			if sprite.animation != &"jump_air" or sprite.frame != 3:
				show_anim(&"jump_air", 3)
			return
		_spin_tick = -1
	var t := _vy / JUMP_SPEED  # -1 at launch, 0 at the peak, about +1 on landing
	var drawing := 0 if t < -0.55 else (1 if t < -0.15 else (2 if t <= 0.15 else (
		3 if t < 0.4 else (4 if t < 0.75 else 5))))
	if _after_dash:
		drawing = maxi(drawing, 4)  # the brake already raised the Keyblade: straight into falling 1
	if sprite.animation != &"jump_air" or sprite.frame != drawing:
		show_anim(&"jump_air", drawing)


func _land() -> void:
	position.y = FLOOR_Y
	_air = false
	_spin_tick = -1
	_dash_tick = -1
	_air_atk_tick = -1  # landing cuts an air attack short
	_after_dash = false
	_vx = 0.0


## Sideways speed (px per game frame, + = forward) a jump starts with, from what he was doing on the ground.
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
static func _step_of(frame: int, holds: Array) -> int:
	var step_i := 0
	for h: int in holds:
		if frame < h:
			return step_i
		frame -= h
		step_i += 1
	return step_i


## One game frame of the ground back-dash: move back, hop low over the hop drawings, then the touch
## down and settle, then the idle.
func _back_dash_step() -> void:
	var step_b := _step_of(_bd_tick, BACK_DASH_HOLDS)
	if step_b >= BACK_DASH_HOLDS.size():
		_bd_tick = -1
		position.y = FLOOR_Y
		show_anim(&"idle")
		return
	var hop_start: int = BACK_DASH_HOLDS[0]
	var hop_len: int = BACK_DASH_HOLDS[1] + BACK_DASH_HOLDS[2]
	var u := float(_bd_tick - hop_start) / hop_len
	position.y = FLOOR_Y - (BACK_DASH_HEIGHT * sin(PI * u) if u > 0.0 and u < 1.0 else 0.0)
	position.x = clampf(position.x + BACK_DASH_SPEED[step_b] * facing, LEFT_LIMIT, RIGHT_LIMIT)
	_bd_tick += 1
	if sprite.animation != &"back_dash" or sprite.frame != step_b:
		show_anim(&"back_dash", step_b)


## Shows a drawing and applies its root motion (in the direction he faces) as it starts.
func show_anim(anim: StringName, drawing: int = 0) -> void:
	sprite.animation = anim
	sprite.frame = drawing
	_hold = 0
	if drawing == 0 and String(anim).begins_with("attack_"):
		attack_hit = false  # a new attack: it may hit once
	var shift: float = DRAW_SHIFT[anim][drawing] if DRAW_SHIFT.has(anim) else 0.0
	var shift_y: float = DRAW_SHIFT_Y[anim][drawing] if DRAW_SHIFT_Y.has(anim) else 0.0
	sprite.offset = -(TALL_FEET[anim] if TALL_FEET.has(anim) else FEET) + Vector2(shift, shift_y)
	_smear.visible = _smear_frames.has(anim)
	if _smear.visible:
		_smear.texture = _smear_frames[anim][drawing]
		_smear.offset = sprite.offset
	var motion: Array = ANIMATIONS[anim][3]
	if drawing < motion.size():
		position.x = clampf(position.x + motion[drawing] * facing, LEFT_LIMIT, RIGHT_LIMIT)
	if trace_tag != "":
		print(trace_tag, " ", _tick, " ", anim, " ", drawing, " ", snappedf(position.x, 0.01), " ",
			snappedf(position.y, 0.01))


## His boxes for the current drawing in world coordinates (table = BOXES.HURT or BOXES.HIT): stored in the
## drawing's own frame pixels, so they get the sprite's offset, mirrored when he faces left.
func boxes(table: Dictionary) -> Array[Rect2]:
	var out: Array[Rect2] = []
	var path := sprite.sprite_frames.get_frame_texture(sprite.animation, sprite.frame).resource_path
	var key := path.get_base_dir().get_file() + "/" + path.get_file()
	if not table.has(key):
		return out
	for r: Rect2 in table[key]:
		var local := Rect2(sprite.offset + r.position, r.size)
		if facing < 0.0:
			local.position.x = -(local.position.x + local.size.x)
		out.append(Rect2(position + local.position, local.size))
	return out


## The middle hurtbox (of a drawing's three, top to bottom) - the push box (Kvon).
func middle_box(table: Dictionary) -> Array[Rect2]:
	var all := boxes(table)
	var out: Array[Rect2] = []
	if not all.is_empty():
		out.append(all[all.size() / 2])
	return out


## The guard pose he blocks an attack of this level with, or &"" if it gets through. Players guard by holding
## back (crouching blocks lows and mids, standing blocks mids and overheads, in the air everything) while not
## attacking, dashing or reeling; the training dummy follows its guard mode.
func guard_pose(level: StringName) -> StringName:
	if state != &"control" and state != &"guard":
		return &""
	if is_attacking() or _air_atk_tick >= 0 or _dash_tick >= 0 or _bd_tick >= 0 or sprite.animation in GLIDE_ANIMS:
		return &""
	match guard_mode:
		&"input":
			if not _back_held:
				return &""
			if _air:
				return &"guard_air"
			if _down_held:
				return &"guard_crouch" if level != &"overhead" else &""
			return &"guard_stand" if level != &"low" else &""
		&"stand":
			return &"guard_stand" if level != &"low" else &""
		&"crouch":
			return &"guard_crouch" if level != &"overhead" else &""
		&"auto":
			return &"guard_crouch" if level == &"low" else &"guard_stand"
	return &""


## An attack reaches him. strength light / medium / heavy, level low / mid / overhead, launch = the launcher,
## away = the direction he is knocked (world). Returns true if he guarded it.
func take_hit(strength: StringName, level: StringName, launch: bool, away: float) -> bool:
	var guard := guard_pose(level)
	push_v = PUSHBACK[strength]
	push_dir = away
	if guard != &"":
		# Blocked: no damage, the guard pose for the blockstun (still falling if in the air), pushback.
		state = &"guard"
		_stun = BLOCKSTUN[strength]
		show_anim(guard)
		return true
	hp = maxi(hp - DAMAGE[strength], 0)
	var decay := maxf(DECAY_FLOOR, 1.0 - DECAY_PER_HIT * combo_hits)
	combo_hits += 1
	_end_moves()
	if hp == 0:
		# Knocked out: thrown down and stays down.
		ko = true
		_start_hurt_air(-KNOCK_SPEED * 0.8, KNOCK_VX * away, HURT_GRAVITY)
	elif launch or state == &"hurt_air" or _air:
		# The launcher sends him flying; any hit while airborne pops him up again (a juggle) - less each hit.
		_start_hurt_air(-(LAUNCH_SPEED if launch else JUGGLE_SPEED) * decay, LAUNCH_VX * away, JUMP_GRAVITY)
	else:
		state = &"stun"
		_stun = maxi(1, roundi(HITSTUN[strength] * decay))
		_stun_len = _stun
		show_anim(&"hurt_ground")
	return false


## Knocked down from the ground (the training J test): launched back, head-first fall, lies, gets up.
func knockdown() -> void:
	_end_moves()
	_start_hurt_air(-KNOCK_SPEED, -KNOCK_VX * facing, HURT_GRAVITY)


func _end_moves() -> void:
	_air = false
	_dash_tick = -1
	_spin_tick = -1
	_air_atk_tick = -1
	_bd_tick = -1
	_after_dash = false
	_glide = false


func _start_hurt_air(vy: float, vx: float, gravity: float) -> void:
	state = &"hurt_air"
	push_v = 0.0  # in the air he drifts instead
	_hvy = vy
	_hvx = vx
	_hgrav = gravity
	_htick = 0
	_hfall = 0
	show_anim(&"hurt_air", 0)


## One game frame while not in control: reeling, guarding, flying, lying.
func _hurt_step() -> void:
	match state:
		&"guard":
			_stun -= 1
			if _air:
				# Air guard: keeps falling in the guard pose; landing ends it.
				_vx *= AIR_COAST
				position.x = clampf(position.x + _vx * facing, LEFT_LIMIT, RIGHT_LIMIT)
				position.y += _vy
				_vy += JUMP_GRAVITY
				if position.y >= FLOOR_Y:
					_land()
					state = &"control"
					show_anim(&"jump_land")
				return
			if _stun <= 0:
				_recover()
		&"stun":
			# Reeling: the ground hit animation stretched over the hitstun, then back in control.
			_stun -= 1
			if _stun <= 0:
				_recover()
				return
			var holds_h: Array = ANIMATIONS[&"hurt_ground"][2]
			var total := 0
			for h: int in holds_h:
				total += h
			var elapsed := int(float(_stun_len - _stun) * total / _stun_len)
			var step_h := mini(_step_of(elapsed, holds_h), holds_h.size() - 1)
			if sprite.animation != &"hurt_ground" or sprite.frame != step_h:
				show_anim(&"hurt_ground", step_h)
		&"hurt_air":
			# Flying: the air hit and drift while rising, the head-first fall (timed from the top) coming down.
			var step_a := 0 if _htick < HURT_AIR_HOLDS[0] else 1
			if _hvy >= 0.0:
				_hfall += 1
				step_a = 2 + _step_of(_hfall, HURT_AIR_HOLDS.slice(2))
			_htick += 1
			_hvx *= AIR_COAST
			position.x = clampf(position.x + _hvx, LEFT_LIMIT, RIGHT_LIMIT)
			position.y += _hvy
			_hvy += _hgrav
			if position.y >= FLOOR_Y:
				position.y = FLOOR_Y
				state = &"down"
				_htick = 0
				show_anim(&"hurt_down", 0)
				return
			var anim_a: StringName = &"hurt_air" if step_a < 2 else &"hurt_fall"
			var drawing_a := step_a if step_a < 2 else mini(step_a - 2, 3)
			if sprite.animation != anim_a or sprite.frame != drawing_a:
				show_anim(anim_a, drawing_a)
		&"down":
			# Lying (shoulders hit, settle, LIE_FRAMES), then the get-up plays through; knocked out, he stays.
			_htick += 1
			if sprite.animation == &"hurt_down":
				var holds_d: Array = ANIMATIONS[&"hurt_down"][2]
				if _htick >= 13 + LIE_FRAMES and not ko:
					show_anim(&"hurt_getup", 0)
				else:
					var step_d := mini(_step_of(_htick, holds_d), holds_d.size() - 1)
					if sprite.frame != step_d:
						show_anim(&"hurt_down", step_d)
				return
			_hold += 1
			var holds_g: Array = ANIMATIONS[&"hurt_getup"][2]
			if _hold >= holds_g[sprite.frame]:
				if sprite.frame + 1 < holds_g.size():
					show_anim(&"hurt_getup", sprite.frame + 1)
				else:
					_recover()


## Back in control: standing, or crouching if down is held (or the dummy's crouching-guard mode).
func _recover() -> void:
	state = &"control"
	combo_hits = 0
	_air = false
	show_anim(&"crouch_hold" if _down_held or guard_mode == &"crouch" else &"idle")
