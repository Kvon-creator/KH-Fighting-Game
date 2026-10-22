extends Node2D
## Test scene for Sora's approved battle idle (sprite2d_v3): two copies stand on the arena floor
## facing each other, so both facings can be checked at once. Press F to swap their facing.
## Run with `-- --capture=<absolute png path>` to save a screenshot after 2 seconds and quit.

## 192 x 192 frames (1.5x the 128 px set), made from the 512 px renders so they stay sharp.
const FRAME_DIR := "res://assets/sora/idle_battle_192/"
## Frame durations of sprite2d_v3 in milliseconds (1000 ms loop).
const FRAME_MS: Array[int] = [100, 90, 90, 100, 120, 100, 90, 90, 100, 120]
## Floor surface of arena.tscn.
const FLOOR_Y := 600.0
## Pixel in each 192 x 192 frame that sits on the floor: body centre, just below the soles.
const FEET := Vector2(96, 177)

var _sprites: Array[AnimatedSprite2D] = []


func _ready() -> void:
	var frames := SpriteFrames.new()
	frames.add_animation(&"idle")
	# At 10 frames per second one duration unit is 100 ms, so 90 ms becomes 0.9.
	frames.set_animation_speed(&"idle", 10.0)
	frames.set_animation_loop_mode(&"idle", SpriteFrames.LOOP_LINEAR)
	for i in FRAME_MS.size():
		var texture: Texture2D = load(FRAME_DIR + "sora_idle_%02d.png" % i)
		frames.add_frame(&"idle", texture, FRAME_MS[i] / 100.0)

	# Left Sora faces right (the art's facing); right Sora is mirrored to face left.
	for spawn_x in [420.0, 860.0]:
		var sprite := AnimatedSprite2D.new()
		sprite.sprite_frames = frames
		sprite.centered = false
		sprite.offset = -FEET
		sprite.position = Vector2(spawn_x, FLOOR_Y)
		sprite.flip_h = spawn_x > 640.0
		add_child(sprite)
		sprite.play(&"idle")
		_sprites.append(sprite)

	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--capture="):
			_capture(arg.trim_prefix("--capture="))


func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_F:
		for sprite in _sprites:
			sprite.flip_h = not sprite.flip_h


func _capture(path: String) -> void:
	await get_tree().create_timer(2.0).timeout
	await RenderingServer.frame_post_draw
	var error := get_viewport().get_texture().get_image().save_png(path)
	print("CAPTURE ", path, " error=", error)
	get_tree().quit()
