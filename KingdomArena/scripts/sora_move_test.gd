extends Node2D
## Movement test for Sora: battle idle by default; hold D or Right to step forward.
## R resets his position. Run with `-- --walk-demo --capture=<png path>` to walk for a moment,
## save a screenshot and quit (used for automated checks).

## Floor surface of arena.tscn.
const FLOOR_Y := 600.0
## Pixel in each 384 x 384 frame that sits on the floor (shared by every Sora animation).
const FEET := Vector2(192, 354)
## Rightmost position he may walk to.
const RIGHT_LIMIT := 1280.0 - 120.0
## Animations run on 60 fps game frames: each drawing is held a whole number of game frames.
const GAME_FPS := 60.0
## name -> [folder, file prefix, game frames per drawing, root motion in px per drawing]
## Root motion is how far his body moves forward as each drawing starts, taken from the render
## (metres x 180.5 px per metre), so planted feet stay exactly in place. Every walk drawing moves
## him, so the loop has no pause: 90 px per 40-frame cycle, about 135 px/s.
const ANIMATIONS := {
	&"idle": ["res://assets/sora/idle_battle_384/", "sora_idle_",
		[6, 5, 5, 6, 7, 6, 5, 5, 6, 7], []],
	&"walk_forward": ["res://assets/sora/walk_fwd_384/", "sora_walk_fwd_",
		[4, 3, 3, 4, 4, 4, 4, 3, 3, 4, 4],
		[2.7, 6.3, 11.7, 13.5, 9.0, 8.1, 8.1, 9.0, 9.9, 7.2, 4.5]],
}

var _sprite: AnimatedSprite2D
var _start_x := 420.0
var _demo_walk := false


func _ready() -> void:
	var frames := SpriteFrames.new()
	for anim: StringName in ANIMATIONS:
		var folder: String = ANIMATIONS[anim][0]
		var prefix: String = ANIMATIONS[anim][1]
		var durations: Array = ANIMATIONS[anim][2]
		frames.add_animation(anim)
		# At 60 fps one duration unit is one game frame.
		frames.set_animation_speed(anim, GAME_FPS)
		frames.set_animation_loop_mode(anim, SpriteFrames.LOOP_LINEAR)
		for i in durations.size():
			var texture: Texture2D = load(folder + prefix + "%02d.png" % i)
			frames.add_frame(anim, texture, durations[i])

	_sprite = AnimatedSprite2D.new()
	_sprite.sprite_frames = frames
	_sprite.centered = false
	_sprite.offset = -FEET
	_sprite.position = Vector2(_start_x, FLOOR_Y)
	add_child(_sprite)
	_sprite.frame_changed.connect(_on_frame_changed)
	_sprite.play(&"idle")

	for arg in OS.get_cmdline_user_args():
		if arg == "--walk-demo":
			_demo_walk = true
		elif arg.begins_with("--capture="):
			_capture(arg.trim_prefix("--capture="))


func _process(_delta: float) -> void:
	var forward := _demo_walk or Input.is_physical_key_pressed(KEY_D) or Input.is_physical_key_pressed(KEY_RIGHT)
	if forward:
		if _sprite.animation != &"walk_forward":
			_sprite.play(&"walk_forward")
	elif _sprite.animation != &"idle":
		_sprite.play(&"idle")


## Moves Sora by the current frame's root motion whenever a new frame starts.
func _on_frame_changed() -> void:
	var motion: Array = ANIMATIONS[_sprite.animation][3]
	if _sprite.frame < motion.size():
		_sprite.position.x = minf(_sprite.position.x + motion[_sprite.frame], RIGHT_LIMIT)


func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_R:
		_sprite.position.x = _start_x


func _capture(path: String) -> void:
	await get_tree().create_timer(1.5).timeout
	await RenderingServer.frame_post_draw
	var error := get_viewport().get_texture().get_image().save_png(path)
	print("CAPTURE ", path, " error=", error, " x=", _sprite.position.x, " anim=", _sprite.animation)
	get_tree().quit()
