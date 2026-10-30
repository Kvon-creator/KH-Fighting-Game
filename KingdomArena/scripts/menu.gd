extends Control
## Title menu (Kvon, October 29): Player vs. Player, Player vs. CPU, Training. Choose with the mouse, or move
## with W / S or the arrow keys and confirm with Enter, Space or U. The choice is stored on the scene tree's root
## as "mode" for match.gd. `--pick=<n>` presses item n after 1 second (automated checks).

const ITEMS := [["PLAYER  VS.  PLAYER", "pvp"], ["PLAYER  VS.  CPU", "cpu"], ["TRAINING", "training"]]

var _buttons: Array[Button] = []
## Input is ignored for the first quarter second (a key or click still held when the window opens).
var _ready_at := 0


func _ready() -> void:
	var bg := TextureRect.new()
	bg.texture = load("res://assets/arena_background.svg")
	bg.size = Vector2(1280, 720)
	bg.stretch_mode = TextureRect.STRETCH_SCALE
	add_child(bg)
	var shade := ColorRect.new()
	shade.color = Color(0.03, 0.05, 0.14, 0.55)
	shade.size = Vector2(1280, 720)
	add_child(shade)
	var title := Label.new()
	title.text = "KINGDOM ARENA"
	title.position = Vector2(0, 150)
	title.size = Vector2(1280, 80)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 64)
	title.add_theme_color_override("font_color", Color8(255, 226, 120))
	title.add_theme_color_override("font_outline_color", Color8(10, 16, 40))
	title.add_theme_constant_override("outline_size", 12)
	add_child(title)
	for i in ITEMS.size():
		var b := Button.new()
		b.text = ITEMS[i][0]
		b.position = Vector2(440, 320 + 76 * i)
		b.size = Vector2(400, 56)
		b.add_theme_font_size_override("font_size", 26)
		b.pressed.connect(_pick.bind(i))
		add_child(b)
		_buttons.append(b)
	for i in _buttons.size():
		_buttons[i].focus_neighbor_top = _buttons[(i - 1 + _buttons.size()) % _buttons.size()].get_path()
		_buttons[i].focus_neighbor_bottom = _buttons[(i + 1) % _buttons.size()].get_path()
	_buttons[0].grab_focus()
	var help := Label.new()
	help.text = "W / S or arrows: choose     Enter / Space / U: start"
	help.position = Vector2(0, 640)
	help.size = Vector2(1280, 30)
	help.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	help.add_theme_font_size_override("font_size", 18)
	add_child(help)
	_ready_at = Time.get_ticks_msec() + 250
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--capture="):
			await get_tree().create_timer(1.0).timeout
			await RenderingServer.frame_post_draw
			print("CAPTURE ", get_viewport().get_texture().get_image().save_png(arg.trim_prefix("--capture=")))
			get_tree().quit()
		if arg.begins_with("--pick="):
			await get_tree().create_timer(1.0).timeout
			_pick(int(arg.trim_prefix("--pick=")))


func _unhandled_key_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo):
		return
	var focused := _buttons.find(get_viewport().gui_get_focus_owner() as Button)
	if focused < 0:
		focused = 0
	match event.physical_keycode:
		KEY_W:
			_buttons[(focused - 1 + _buttons.size()) % _buttons.size()].grab_focus()
		KEY_S:
			_buttons[(focused + 1) % _buttons.size()].grab_focus()
		KEY_U:
			_pick(focused)


func _pick(i: int) -> void:
	if Time.get_ticks_msec() < _ready_at:
		return
	get_tree().root.set_meta("mode", ITEMS[i][1])
	print("MENU pick ", ITEMS[i][1])
	get_tree().change_scene_to_file("res://scenes/match.tscn")
