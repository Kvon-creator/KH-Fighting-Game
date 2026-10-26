extends Node2D
## Movement test for Sora: battle idle by default. Hold D or Right to shuffle forward, A or Left
## to shuffle back. The shuffle's first drawing is the idle stance, so it starts straight from the
## idle; when the key is released he finishes the current step (back to the idle stance) and
## stands. Hold S or Down to crouch (Keyblade in one hand); release to stand back up. Crouching
## wins over walking; during a step he crouches once the step finishes. Double-tap D or Right and
## hold to glide low across the floor; on release he skids to a stop into the idle. Press W or Up to
## jump straight up (takeoff, then the air drawing follows his vertical speed, then the landing).
## R resets his position.
## Automated checks: `-- --walk-demo-ticks=N` holds forward for N game frames, `-- --back-demo-ticks=N`
## holds back, `-- --crouch-demo-ticks=N` holds crouch (from game frame `--crouch-demo-from=M`,
## default 1), `-- --glide-demo-ticks=N` double-taps forward (held on frames 1-3 and 7-N),
## `-- --jump-demo-at=N` presses jump on game frame N;
## `--capture=<png path>` saves a screenshot after 1.5 s and quits.
##
## Animation is stepped once per physics tick (60 per second, the project default), like a
## fighting game: each drawing is held an exact number of game frames.

## Floor surface of arena.tscn.
const FLOOR_Y := 600.0
## Pixel in each 384 x 384 frame that sits on the floor (shared by every Sora animation).
const FEET := Vector2(192, 354)
## How far he may walk toward either screen edge.
const LEFT_LIMIT := 120.0
const RIGHT_LIMIT := 1280.0 - 120.0
## The second forward press must come within this many game frames of the first to start a glide.
const DOUBLE_TAP_FRAMES := 15
## The glide push-off ends on the loop's first pose, so it hands over to this glide_loop drawing.
const GLIDE_ENTRY_DRAWING := 1
## Jump: peak height in px and game frames from leaving the floor to the peak; gravity and launch
## speed follow from these (a 0.6 s hop).
const JUMP_HEIGHT := 200.0
const JUMP_RISE_FRAMES := 18.0
const JUMP_GRAVITY := 2.0 * JUMP_HEIGHT / (JUMP_RISE_FRAMES * JUMP_RISE_FRAMES)
const JUMP_SPEED := JUMP_GRAVITY * JUMP_RISE_FRAMES
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
	# 600 px/s (no planted feet, so it can stop after any drawing), skid landing into the idle.
	&"glide_start": ["res://assets/sora/glide_start_384/", "sora_glide_start_",
		[2, 2, 3, 3], [3.61, 14.44, 18.05, 28.88]],
	&"glide_loop": ["res://assets/sora/glide_loop_384/", "sora_glide_loop_",
		[3, 3, 3, 3, 3, 3], [30.0, 30.0, 30.0, 30.0, 30.0, 30.0]],
	&"glide_stop": ["res://assets/sora/glide_stop_384/", "sora_glide_stop_",
		[2, 3, 3, 3, 3], [30.0, 18.05, 9.03, 3.61, 0.0]],
	# Jump: takeoff on the ground, then one "air" animation whose drawing is picked from his vertical
	# speed each game frame (rising 1, rising 2, apex, swing up, falling 1, falling 2), then the landing.
	&"jump_start": ["res://assets/sora/jump_start_384/", "sora_jump_start_", [2, 2, 2], []],
	&"jump_air": ["res://assets/sora/jump_rise_384/", "sora_jump_rise_", [1, 1, 1, 1, 1, 1], [],
		[0, 1, 0, 0, 1, 2], ["sora_jump_rise_", "sora_jump_rise_", "sora_jump_apex_", "sora_jump_fall_",
		"sora_jump_fall_", "sora_jump_fall_"], ["res://assets/sora/jump_rise_384/",
		"res://assets/sora/jump_rise_384/", "res://assets/sora/jump_apex_384/", "res://assets/sora/jump_fall_384/",
		"res://assets/sora/jump_fall_384/", "res://assets/sora/jump_fall_384/"]],
	&"jump_land": ["res://assets/sora/jump_land_384/", "sora_jump_land_", [3, 3, 4], []],
}

var _sprite: AnimatedSprite2D
var _start_x := 420.0
## Game frames to hold forward / back / crouch in the timed demos (-1 = not used).
var _demo_forward_ticks := -1
var _demo_back_ticks := -1
var _demo_crouch_ticks := -1
var _demo_crouch_from := 1
var _demo_glide_ticks := -1
var _demo_jump_at := -1
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
	_show(&"idle")

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
		elif arg.begins_with("--jump-demo-at="):
			_demo_jump_at = int(arg.trim_prefix("--jump-demo-at="))
		elif arg == "--trace":
			_trace = true
		elif arg.begins_with("--capture="):
			_capture(arg.trim_prefix("--capture="))


func _physics_process(_delta: float) -> void:
	_tick += 1
	var forward := _tick <= _demo_forward_ticks or Input.is_physical_key_pressed(KEY_D) \
		or Input.is_physical_key_pressed(KEY_RIGHT) \
		or (_demo_glide_ticks > 0 and (_tick <= 3 or (_tick >= 7 and _tick <= _demo_glide_ticks)))
	var back := _tick <= _demo_back_ticks or Input.is_physical_key_pressed(KEY_A) \
		or Input.is_physical_key_pressed(KEY_LEFT)
	var crouch := (_demo_crouch_from <= _tick and _tick <= _demo_crouch_ticks) \
		or Input.is_physical_key_pressed(KEY_S) or Input.is_physical_key_pressed(KEY_DOWN)
	# A new forward press soon after the previous one is a double tap: glide while it stays held.
	if forward and not _forward_was:
		_glide = _tick - _last_forward_press <= DOUBLE_TAP_FRAMES
		_last_forward_press = _tick
	if not forward:
		_glide = false
	_forward_was = forward
	var wanted: StringName = &"crouch_down" if crouch else (
		&"shuffle_forward" if forward and not back else (
		&"shuffle_back" if back and not forward else &"idle"))
	var glide_wanted := _glide and wanted == &"shuffle_forward"
	var anim := _sprite.animation
	var jump := _tick == _demo_jump_at or Input.is_physical_key_pressed(KEY_W) 		or Input.is_physical_key_pressed(KEY_UP)
	var jump_pressed := jump and not _jump_was
	_jump_was = jump
	if _air:
		_air_step()
		return
	if jump_pressed and anim in [&"idle", &"shuffle_forward", &"shuffle_back"]:
		_show(&"jump_start")  # from the idle stance (a step just begun snaps back to it)
		return
	if glide_wanted and anim in [&"idle", &"shuffle_forward", &"shuffle_back"]:
		_show(&"glide_start")  # from the idle stance (a step just begun snaps back to it)
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
		else:
			# End of a step cycle, standing up or the glide landing: the feet are in the idle stance, so
			# he can stand, crouch, switch direction or keep going without any pop.
			_show(wanted)


## One airborne game frame: move by the vertical speed, apply gravity, pick the air drawing from the
## speed, and land when the feet reach the floor.
func _air_step() -> void:
	_sprite.position.y += _vy
	_vy += JUMP_GRAVITY
	if _sprite.position.y >= FLOOR_Y:
		_sprite.position.y = FLOOR_Y
		_air = false
		_show(&"jump_land")
		return
	var t := _vy / JUMP_SPEED  # -1 at launch, 0 at the peak, about +1 on landing
	var drawing := 0 if t < -0.55 else (1 if t < -0.15 else (2 if t <= 0.15 else (
		3 if t < 0.4 else (4 if t < 0.75 else 5))))
	if _sprite.animation != &"jump_air" or _sprite.frame != drawing:
		_show(&"jump_air", drawing)


## Shows a drawing and applies its root motion as it starts.
func _show(anim: StringName, drawing: int = 0) -> void:
	_sprite.animation = anim
	_sprite.frame = drawing
	_hold = 0
	var motion: Array = ANIMATIONS[anim][3]
	if drawing < motion.size():
		_sprite.position.x = clampf(_sprite.position.x + motion[drawing], LEFT_LIMIT, RIGHT_LIMIT)
	if _trace:
		print("TRACE ", _tick, " ", anim, " ", drawing, " ", snappedf(_sprite.position.x, 0.01), " ",
			snappedf(_sprite.position.y, 0.01))


func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_R:
		_sprite.position.x = _start_x


func _capture(path: String) -> void:
	await get_tree().create_timer(1.5).timeout
	await RenderingServer.frame_post_draw
	var error := get_viewport().get_texture().get_image().save_png(path)
	print("CAPTURE ", path, " error=", error, " x=", _sprite.position.x, " anim=", _sprite.animation)
	get_tree().quit()
