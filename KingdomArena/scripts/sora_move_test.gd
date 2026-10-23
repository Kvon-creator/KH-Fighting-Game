extends Node2D
## Movement test for Sora: battle idle by default. Hold D or Right to shuffle forward, A or Left
## to shuffle back. The shuffle's first drawing is the idle stance, so it starts straight from the
## idle; when the key is released he finishes the current step (back to the idle stance) and
## stands. Hold S or Down to crouch (Keyblade in one hand); release to stand back up. Crouching
## wins over walking; during a step he crouches once the step finishes. Double-tap D or Right and
## hold to run; on release he finishes his stride (left foot forward) and brakes into the idle.
## R resets his position.
## Automated checks: `-- --walk-demo-ticks=N` holds forward for N game frames, `-- --back-demo-ticks=N`
## holds back, `-- --crouch-demo-ticks=N` holds crouch (from game frame `--crouch-demo-from=M`,
## default 1), `-- --run-demo-ticks=N` double-taps forward (held on frames 1-3 and 7-N);
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
## The second forward press must come within this many game frames of the first to start a run.
const DOUBLE_TAP_FRAMES := 15
## The run start ends on the loop's passing pose, so it hands over to this run_loop drawing.
const RUN_ENTRY_DRAWING := 3
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
	# Run (matched to Gemini's generated running poses, Gemini rounds 14-17): ~594 px/s, 198.5 px per
	# 20-frame cycle.
	&"run_start": ["res://assets/sora/run_start_384/", "sora_run_start_",
		[2, 2, 3, 3], [10.83, 19.86, 27.07, 29.66]],
	&"run_loop": ["res://assets/sora/run_loop_384/", "sora_run_loop_",
		[2, 3, 2, 3, 2, 3, 2, 3], [21.66, 21.66, 32.49, 23.46, 21.66, 21.66, 32.49, 23.46]],
	&"run_stop": ["res://assets/sora/run_stop_384/", "sora_run_stop_",
		[2, 3, 3, 3, 3], [27.07, 14.44, 7.22, 1.8, 0.0]],
}

var _sprite: AnimatedSprite2D
var _start_x := 420.0
## Game frames to hold forward / back / crouch in the timed demos (-1 = not used).
var _demo_forward_ticks := -1
var _demo_back_ticks := -1
var _demo_crouch_ticks := -1
var _demo_crouch_from := 1
var _demo_run_ticks := -1
var _tick := 0
## Game frames the current drawing has been shown.
var _hold := 0
## Double-tap tracking: forward held last frame, the frame it was last pressed, and whether the
## current hold is a run.
var _forward_was := false
var _last_forward_press := -1000
var _run := false
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
		for i: int in order:
			frames.add_frame(anim, load(folder + prefix + "%02d.png" % i) as Texture2D)

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
		elif arg.begins_with("--run-demo-ticks="):
			_demo_run_ticks = int(arg.trim_prefix("--run-demo-ticks="))
		elif arg == "--trace":
			_trace = true
		elif arg.begins_with("--capture="):
			_capture(arg.trim_prefix("--capture="))


func _physics_process(_delta: float) -> void:
	_tick += 1
	var forward := _tick <= _demo_forward_ticks or Input.is_physical_key_pressed(KEY_D) \
		or Input.is_physical_key_pressed(KEY_RIGHT) \
		or (_demo_run_ticks > 0 and (_tick <= 3 or (_tick >= 7 and _tick <= _demo_run_ticks)))
	var back := _tick <= _demo_back_ticks or Input.is_physical_key_pressed(KEY_A) \
		or Input.is_physical_key_pressed(KEY_LEFT)
	var crouch := (_demo_crouch_from <= _tick and _tick <= _demo_crouch_ticks) \
		or Input.is_physical_key_pressed(KEY_S) or Input.is_physical_key_pressed(KEY_DOWN)
	# A new forward press soon after the previous one is a double tap: run while it stays held.
	if forward and not _forward_was:
		_run = _tick - _last_forward_press <= DOUBLE_TAP_FRAMES
		_last_forward_press = _tick
	if not forward:
		_run = false
	_forward_was = forward
	var wanted: StringName = &"crouch_down" if crouch else (
		&"shuffle_forward" if forward and not back else (
		&"shuffle_back" if back and not forward else &"idle"))
	var run_wanted := _run and wanted == &"shuffle_forward"
	var anim := _sprite.animation
	if run_wanted and anim in [&"idle", &"shuffle_forward", &"shuffle_back"]:
		_show(&"run_start")  # from the idle stance (a step just begun snaps back to it)
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
		if anim == &"run_start" and at_end:
			_show(&"run_loop", RUN_ENTRY_DRAWING)
		elif anim == &"run_loop" and at_end:
			# End of the stride, left foot about to plant: keep running or brake.
			_show(&"run_loop" if run_wanted else &"run_stop")
		elif not at_end:
			_show(anim, _sprite.frame + 1)
		elif anim == &"idle":
			_show(&"idle")
		elif anim == &"crouch_down" or anim == &"crouch_hold":
			_show(&"crouch_hold")
		else:
			# End of a step cycle, standing up or the run brake: the feet are in the idle stance, so
			# he can stand, crouch, switch direction or keep going without any pop.
			_show(wanted)


## Shows a drawing and applies its root motion as it starts.
func _show(anim: StringName, drawing: int = 0) -> void:
	_sprite.animation = anim
	_sprite.frame = drawing
	_hold = 0
	var motion: Array = ANIMATIONS[anim][3]
	if drawing < motion.size():
		_sprite.position.x = clampf(_sprite.position.x + motion[drawing], LEFT_LIMIT, RIGHT_LIMIT)
	if _trace:
		print("TRACE ", _tick, " ", anim, " ", drawing, " ", snappedf(_sprite.position.x, 0.01))


func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_R:
		_sprite.position.x = _start_x


func _capture(path: String) -> void:
	await get_tree().create_timer(1.5).timeout
	await RenderingServer.frame_post_draw
	var error := get_viewport().get_texture().get_image().save_png(path)
	print("CAPTURE ", path, " error=", error, " x=", _sprite.position.x, " anim=", _sprite.animation)
	get_tree().quit()
