extends Node2D
## Movement test for Sora: battle idle by default. Hold D or Right to shuffle forward, A or Left
## to shuffle back. The shuffle's first drawing is the idle stance, so it starts straight from the
## idle; when the key is released he finishes the current step (back to the idle stance) and
## stands. R resets his position.
## Automated checks: `-- --walk-demo-ticks=N` holds forward for N game frames, `-- --back-demo-ticks=N`
## holds back; `--capture=<png path>` saves a screenshot after 1.5 s and quits.
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
## name -> [folder, file prefix, game frames per drawing, root motion in px per drawing]
## Root motion is how far his body moves as each drawing starts, taken from the render (metres x
## 180.5 px per metre), so planted feet stay exactly in place: 64.5 px per 20-frame cycle, ~193 px/s.
const ANIMATIONS := {
	&"idle": ["res://assets/sora/idle_battle_384/", "sora_idle_",
		[6, 5, 5, 6, 7, 6, 5, 5, 6, 7], []],
	&"shuffle_forward": ["res://assets/sora/shuffle_fwd_384/", "sora_shuffle_fwd_",
		[3, 3, 2, 4, 2, 3, 3], [1.61, 8.07, 14.51, 9.67, 9.67, 14.51, 6.44]],
	&"shuffle_back": ["res://assets/sora/shuffle_back_384/", "sora_shuffle_back_",
		[3, 3, 2, 4, 2, 3, 3], [-1.61, -8.07, -14.51, -9.67, -9.67, -14.51, -6.44]],
}

var _sprite: AnimatedSprite2D
var _start_x := 420.0
## Game frames to hold forward / back in the timed demos (-1 = not used).
var _demo_forward_ticks := -1
var _demo_back_ticks := -1
var _tick := 0
## Game frames the current drawing has been shown.
var _hold := 0


func _ready() -> void:
	var frames := SpriteFrames.new()
	for anim: StringName in ANIMATIONS:
		frames.add_animation(anim)
		var folder: String = ANIMATIONS[anim][0]
		var prefix: String = ANIMATIONS[anim][1]
		for i in ANIMATIONS[anim][2].size():
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
		elif arg.begins_with("--capture="):
			_capture(arg.trim_prefix("--capture="))


func _physics_process(_delta: float) -> void:
	_tick += 1
	var forward := _tick <= _demo_forward_ticks or Input.is_physical_key_pressed(KEY_D) \
		or Input.is_physical_key_pressed(KEY_RIGHT)
	var back := _tick <= _demo_back_ticks or Input.is_physical_key_pressed(KEY_A) \
		or Input.is_physical_key_pressed(KEY_LEFT)
	var wanted: StringName = &"shuffle_forward" if forward and not back else (
		&"shuffle_back" if back and not forward else &"idle")
	if _sprite.animation == &"idle" and wanted != &"idle":
		_show(wanted)  # drawing 1 of the shuffle is the idle stance
		return
	# Advance one game frame; move to the next drawing when this one's hold is used up.
	_hold += 1
	var holds: Array = ANIMATIONS[_sprite.animation][2]
	if _hold >= holds[_sprite.frame]:
		if _sprite.frame + 1 < holds.size():
			_show(_sprite.animation, _sprite.frame + 1)
		elif _sprite.animation == &"idle":
			_show(&"idle")
		else:
			# End of a step cycle: the feet are back in the idle stance, so he can stand, switch
			# direction or keep going without any pop.
			_show(wanted)


## Shows a drawing and applies its root motion as it starts.
func _show(anim: StringName, drawing: int = 0) -> void:
	_sprite.animation = anim
	_sprite.frame = drawing
	_hold = 0
	var motion: Array = ANIMATIONS[anim][3]
	if drawing < motion.size():
		_sprite.position.x = clampf(_sprite.position.x + motion[drawing], LEFT_LIMIT, RIGHT_LIMIT)


func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_R:
		_sprite.position.x = _start_x


func _capture(path: String) -> void:
	await get_tree().create_timer(1.5).timeout
	await RenderingServer.frame_post_draw
	var error := get_viewport().get_texture().get_image().save_png(path)
	print("CAPTURE ", path, " error=", error, " x=", _sprite.position.x, " anim=", _sprite.animation)
	get_tree().quit()
