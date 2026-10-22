extends Node2D
## Movement test for Sora: battle idle by default; hold D or Right to step forward. Pressing
## forward plays the idle-to-walk transition once, then loops the walk; releasing it plays the
## brake back into the idle. R resets his position.
## Run with `-- --walk-demo --capture=<png path>` to walk for a moment, save a screenshot and quit,
## or `-- --walk-demo-ticks=N` to hold forward for N game frames and then release (used for
## automated checks).
##
## Animation is stepped once per physics tick (60 per second, the project default), like a
## fighting game: each drawing is held an exact number of game frames, and the transition hands
## over to the walk on the very next frame.

## Floor surface of arena.tscn.
const FLOOR_Y := 600.0
## Pixel in each 384 x 384 frame that sits on the floor (shared by every Sora animation).
const FEET := Vector2(192, 354)
## Rightmost position he may walk to.
const RIGHT_LIMIT := 1280.0 - 120.0
## name -> [folder, file prefix, game frames per drawing, root motion in px per drawing, next]
## `next` is the animation to continue with after the last drawing (itself = loop).
## Root motion is how far his body moves forward as each drawing starts, taken from the render
## (metres x 180.5 px per metre), so planted feet stay exactly in place. The walk moves him at a
## constant 1.625 px per game frame (6.5 px per 4-frame hold, 4.875 px per 3-frame hold):
## 65 px per 40-frame cycle, 97.5 px/s. The transition crouches in place.
const ANIMATIONS := {
	&"idle": ["res://assets/sora/idle_battle_384/", "sora_idle_",
		[6, 5, 5, 6, 7, 6, 5, 5, 6, 7], [], &"idle"],
	&"walk_start": ["res://assets/sora/walk_start_384/", "sora_walk_start_",
		[3, 3, 3, 3], [], &"walk_forward"],
	&"walk_forward": ["res://assets/sora/walk_fwd_384/", "sora_walk_fwd_",
		[4, 3, 3, 4, 4, 4, 4, 3, 3, 4, 4],
		[6.5, 4.875, 4.875, 6.5, 6.5, 6.5, 6.5, 4.875, 4.875, 6.5, 6.5], &"walk_forward"],
	&"walk_stop": ["res://assets/sora/walk_stop_384/", "sora_walk_stop_",
		[3, 3, 3, 3], [], &"idle"],
}

var _sprite: AnimatedSprite2D
var _start_x := 420.0
var _demo_walk := false
## Game frames to hold forward in the timed demo (-1 = not used).
var _demo_ticks := -1
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
		if arg == "--walk-demo":
			_demo_walk = true
		elif arg.begins_with("--walk-demo-ticks="):
			_demo_ticks = int(arg.trim_prefix("--walk-demo-ticks="))
		elif arg.begins_with("--capture="):
			_capture(arg.trim_prefix("--capture="))


func _physics_process(_delta: float) -> void:
	_tick += 1
	var forward := _demo_walk or _tick <= _demo_ticks 		or Input.is_physical_key_pressed(KEY_D) or Input.is_physical_key_pressed(KEY_RIGHT)
	if forward and _sprite.animation == &"idle":
		_show(&"walk_start")
		return
	if not forward and _sprite.animation in [&"walk_start", &"walk_forward"]:
		_show(&"walk_stop")  # brake back into the idle
		return
	if forward and _sprite.animation == &"walk_stop":
		_show(&"walk_start")
		return
	# Advance one game frame; move to the next drawing when this one's hold is used up.
	_hold += 1
	var holds: Array = ANIMATIONS[_sprite.animation][2]
	if _hold >= holds[_sprite.frame]:
		if _sprite.frame + 1 < holds.size():
			_show(_sprite.animation, _sprite.frame + 1)
		else:
			_show(ANIMATIONS[_sprite.animation][4])


## Shows a drawing and applies its root motion as it starts.
func _show(anim: StringName, drawing: int = 0) -> void:
	_sprite.animation = anim
	_sprite.frame = drawing
	_hold = 0
	var motion: Array = ANIMATIONS[anim][3]
	if drawing < motion.size():
		_sprite.position.x = minf(_sprite.position.x + motion[drawing], RIGHT_LIMIT)


func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_R:
		_sprite.position.x = _start_x


func _capture(path: String) -> void:
	await get_tree().create_timer(1.5).timeout
	await RenderingServer.frame_post_draw
	var error := get_viewport().get_texture().get_image().save_png(path)
	print("CAPTURE ", path, " error=", error, " x=", _sprite.position.x, " anim=", _sprite.animation)
	get_tree().quit()
