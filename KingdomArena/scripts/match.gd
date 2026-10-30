extends Node2D
## A match between two Soras (Kvon, October 29). The mode comes from the menu (stored on the scene tree's root as
## "mode") or `--mode=pvp|cpu|training`; started on its own, it is Training.
## - Player vs. Player: player 1 = WASD + U / I / O, player 2 = arrow keys + number pad 7 / 8 / 9.
## - Player vs. CPU: player 2 is a simple fighter AI.
## - Training: player 2 is a standing dummy (G cycles its guard: off / standing / crouching / auto); H = take a
##   hit (hold A to guard it), J = knockdown, R = reset. Health refills.
## Fighters always face each other (they turn around when they cross; in the air on landing). "Back" (away from
## the opponent) guards. Best of 3 rounds in the two match modes, then back to the menu (Esc also returns).
## F1 shows hitboxes (red), hurtboxes (blue) and push boxes (yellow).
## Combat rules: one hit per attack; hit-freeze; hitstun with per-hit decay; launcher + juggles; pushback; the
## middle hurtboxes push the fighters apart; crouching attacks hit low, jumping attacks overhead.
## Automated checks (player 1, as in the old test scene): `--walk-demo-ticks=N`, `--back-demo-ticks=N`,
## `--crouch-demo-ticks=N` (from `--crouch-demo-from=M`), `--glide-demo-ticks=N`, `--jump-demo-at=N`
## (`--jump-hold-to=N`, `--jump2-demo-at=M`, `--dash-demo-at=M`), `--bdash-demo-at=N`, `--hit-demo-at=N`,
## `--knock-demo-at=N`, `--light/medium/heavy-demo-at=N[,N...]`; the same with a `p2-` prefix for player 2
## (e.g. `--p2-walk-demo-ticks=N`); `--dummy-guard=0-3`, `--show-boxes`, `--trace`, `--capture=<png>`.

const BOXES := preload("res://scripts/sora_boxes.gd")
const FLOOR_Y := 600.0
const START_X := [420.0, 860.0]
const LOST_HP_DELAY := 30
const LOST_HP_DRAIN := 120.0
const SPARK_FRAMES := 10
const BARRIER_FRAMES := 16
const GUARD_MODES := [&"none", &"stand", &"crouch", &"auto"]
const GUARD_NAMES := ["OFF", "STANDING", "CROUCHING", "AUTO"]
const SCREEN_CENTER := Vector2(640, 360)
const HEAD_ABOVE_FEET := 294.0
const CAMERA_MARGIN := 40.0
const CAMERA_EASE := 0.25
const SKY_COLOR := Color8(19, 28, 57)
## Rounds: game frames for "ROUND n" + "FIGHT!", the K.O. pause, and the winner screen.
const INTRO_FRAMES := 100
const KO_FRAMES := 150
const WIN_FRAMES := 210
const ROUNDS_TO_WIN := 2

var mode := "training"
var p: Array[Fighter] = []
var _hp_shown: Array[float] = [10000.0, 10000.0]
var _lost_wait := [0, 0]
var _freeze := 0
var _frames := 0
var _fx: Array[Dictionary] = []
var _show_boxes := false
var _trace := false
var _guard_mode := 0
var _demo: Array[Dictionary] = [{}, {}]
var _was_test := {}
var _phase := "fight"  # intro / fight / ko / win (match modes); training stays in fight
var _phase_t := 0
var _round := 1
var _wins := [0, 0]
var _winner := -1
var _camera: Camera2D
var _box_view: Node2D
var _fx_view: Node2D
var _hud: Control
## CPU: planned button holds [{"at": frame, "keys": [...], "len": frames}], next decision frame, the attack of the
## opponent it last decided about.
var _cpu_plan: Array[Dictionary] = []
var _cpu_next := 0
var _cpu_seen_attack := ""
var _rng := RandomNumberGenerator.new()
## `--start-hp=N`: rounds start with this much health (automated checks of the round flow).
var _start_hp := Fighter.MAX_HP


func _ready() -> void:
	mode = str(get_tree().root.get_meta("mode", "training"))
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--mode="):
			mode = arg.trim_prefix("--mode=")
	_rng.seed = 2610
	var sky := ColorRect.new()
	sky.color = SKY_COLOR
	sky.position = Vector2(0, -600)
	sky.size = Vector2(1280, 600)
	sky.z_index = -10
	add_child(sky)
	move_child(sky, 0)
	var frames := Fighter.load_frames()
	var smears := Fighter.load_smears()
	for i in 2:
		var f := Fighter.new()
		add_child(f)
		f.setup(frames, smears, START_X[i], 1.0 if i == 0 else -1.0)
		p.append(f)
	_camera = Camera2D.new()
	_camera.position = SCREEN_CENTER
	_camera.limit_left = 0
	_camera.limit_right = 1280
	_camera.limit_bottom = 720
	add_child(_camera)
	_camera.make_current()
	_box_view = Node2D.new()
	_box_view.z_index = 50
	_box_view.draw.connect(_draw_boxes)
	add_child(_box_view)
	_fx_view = Node2D.new()
	_fx_view.z_index = 60
	_fx_view.draw.connect(_draw_fx)
	add_child(_fx_view)
	_hud = Control.new()
	_hud.size = Vector2(1280, 720)
	_hud.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_hud.draw.connect(_draw_hud)
	$HUD.add_child(_hud)
	for child in $HUD.get_children():
		if child is Label:
			child.visible = mode == "training"  # the old test scene's title / controls text
	for i in 2:
		_demo[i] = _parse_demo("" if i == 0 else "p2-")
	for arg in OS.get_cmdline_user_args():
		if arg == "--trace":
			_trace = true
			p[0].trace_tag = "TRACE"
			p[1].trace_tag = "TRACE2"
		elif arg.begins_with("--dummy-guard="):
			_set_guard_mode(int(arg.trim_prefix("--dummy-guard=")))
		elif arg == "--show-boxes":
			_show_boxes = true
		elif arg.begins_with("--start-hp="):
			_start_hp = int(arg.trim_prefix("--start-hp="))
		elif arg.begins_with("--capture="):
			_capture(arg.trim_prefix("--capture="))
	if mode == "training":
		_set_guard_mode(_guard_mode)
	else:
		_start_round()


func _parse_demo(prefix: String) -> Dictionary:
	var d := {"walk": -1, "back": -1, "crouch": -1, "crouch_from": 1, "glide": -1, "jump": -1, "jump_hold": -1,
		"jump2": -1, "dash": -1, "bdash": -1, "hit": -1, "knock": -1, "light": [], "medium": [], "heavy": []}
	var names := {"walk-demo-ticks": "walk", "back-demo-ticks": "back", "crouch-demo-ticks": "crouch",
		"crouch-demo-from": "crouch_from", "glide-demo-ticks": "glide", "jump-demo-at": "jump",
		"jump-hold-to": "jump_hold", "jump2-demo-at": "jump2", "dash-demo-at": "dash", "bdash-demo-at": "bdash",
		"hit-demo-at": "hit", "knock-demo-at": "knock"}
	for arg in OS.get_cmdline_user_args():
		if not arg.begins_with("--" + prefix):
			continue
		var rest := arg.trim_prefix("--" + prefix)
		if prefix == "" and rest.begins_with("p2-"):
			continue
		for n: String in names:
			if rest.begins_with(n + "="):
				d[names[n]] = int(rest.trim_prefix(n + "="))
		for k in ["light", "medium", "heavy"]:
			if rest.begins_with(k + "-demo-at="):
				for v in rest.trim_prefix(k + "-demo-at=").split(","):
					d[k].append(int(v))
	return d


func _physics_process(_delta: float) -> void:
	_frames += 1
	if _freeze > 0:
		_freeze -= 1  # hit-freeze: both fighters hold still (effects and bars keep going)
	else:
		_phase_step()
		for i in 2:
			var inp := _input_for(i) if _phase == "fight" else {}
			p[i].step(inp)
		_training_tests()
		for i in 2:
			var dx := p[1 - i].position.x - p[i].position.x
			if absf(dx) > 1.0:
				p[i].face_toward(signf(dx))
		_pushback_step()
		_push_apart()
		_hits()
	for e: Dictionary in _fx:
		e["age"] += 1
	_fx = _fx.filter(func(e: Dictionary) -> bool:
		return e["age"] < (SPARK_FRAMES if e["kind"] == &"spark" else BARRIER_FRAMES))
	for i in 2:
		if _lost_wait[i] > 0:
			_lost_wait[i] -= 1
		else:
			_hp_shown[i] = move_toward(_hp_shown[i], float(p[i].hp), LOST_HP_DRAIN)
	var top := minf(p[0].position.y, p[1].position.y) - HEAD_ABOVE_FEET
	_camera.position.y = lerpf(_camera.position.y, minf(SCREEN_CENTER.y, top - CAMERA_MARGIN + SCREEN_CENTER.y),
		CAMERA_EASE)
	_box_view.queue_redraw()
	_fx_view.queue_redraw()
	_hud.queue_redraw()
	if _trace and _frames % 4 == 0:
		print("POS ", _frames, " sora=", snappedf(p[0].position.x, 0.1), " dummy=", snappedf(p[1].position.x, 0.1),
			",", snappedf(p[1].position.y, 0.1), " ", p[1].state, " freeze=", _freeze, " facing=", p[0].facing, ",",
			p[1].facing)


## This frame's buttons for fighter i, as forward / back (relative to where he faces), up, down, light, medium, heavy.
func _input_for(i: int) -> Dictionary:
	var f := p[i]
	var right := false
	var left := false
	var inp := {}
	if i == 0:
		right = Input.is_physical_key_pressed(KEY_D)
		left = Input.is_physical_key_pressed(KEY_A)
		inp = {"up": Input.is_physical_key_pressed(KEY_W), "down": Input.is_physical_key_pressed(KEY_S),
			"light": Input.is_physical_key_pressed(KEY_U), "medium": Input.is_physical_key_pressed(KEY_I),
			"heavy": Input.is_physical_key_pressed(KEY_O)}
	elif mode == "pvp":
		right = Input.is_physical_key_pressed(KEY_RIGHT)
		left = Input.is_physical_key_pressed(KEY_LEFT)
		inp = {"up": Input.is_physical_key_pressed(KEY_UP), "down": Input.is_physical_key_pressed(KEY_DOWN),
			"light": Input.is_physical_key_pressed(KEY_KP_7), "medium": Input.is_physical_key_pressed(KEY_KP_8),
			"heavy": Input.is_physical_key_pressed(KEY_KP_9)}
	elif mode == "cpu":
		inp = _cpu_input(f, p[0])
	else:
		inp = {"down": GUARD_MODES[_guard_mode] == &"crouch"}  # the training dummy
	if right or left:
		inp["forward"] = (right and f.facing > 0.0) or (left and f.facing < 0.0)
		inp["back"] = (left and f.facing > 0.0) or (right and f.facing < 0.0)
	# Timed demo presses for automated checks (relative to his facing).
	var d: Dictionary = _demo[i]
	var t := f._tick + 1
	if t <= d["walk"] or (d["glide"] > 0 and (t <= 3 or (t >= 7 and t <= d["glide"]))) \
			or (d["dash"] > 0 and (t - d["dash"]) in [0, 1, 5, 6]):
		inp["forward"] = true
	if t <= d["back"] or (d["bdash"] > 0 and (t - d["bdash"]) in [0, 1, 5, 6]):
		inp["back"] = true
	if d["crouch_from"] <= t and t <= d["crouch"]:
		inp["down"] = true
	if t == d["jump"] or t == d["jump2"] or (d["jump"] > 0 and d["jump"] <= t and t <= d["jump_hold"]):
		inp["up"] = true
	for k in ["light", "medium", "heavy"]:
		if t in d[k]:
			inp[k] = true
	return inp


## Training tests for player 1: H = a medium hit from in front (guarded if A is held), J = a knockdown.
func _training_tests() -> void:
	if mode != "training":
		return
	var f := p[0]
	var t := f._tick
	var hit: bool = t == _demo[0]["hit"] or Input.is_physical_key_pressed(KEY_H)
	var knock: bool = t == _demo[0]["knock"] or Input.is_physical_key_pressed(KEY_J)
	if hit and not _was_test.get("hit", false) and f.state != &"down":
		var guarded := f.take_hit(&"medium", &"mid", false, -f.facing)
		_add_fx(&"barrier" if guarded else &"spark", f.position + Vector2(60 * f.facing, -150), -f.facing)
		_lost_wait[0] = LOST_HP_DELAY
	if knock and not _was_test.get("knock", false) and f.state != &"down":
		f.knockdown()
	_was_test["hit"] = hit
	_was_test["knock"] = knock
	for i in 2:
		if p[i].hp == 0:
			p[i].hp = Fighter.MAX_HP  # training: health refills
			p[i].ko = false


func _hits() -> void:
	# Both directions are found first so two attacks landing on the same frame trade.
	var found: Array[Dictionary] = []
	for i in 2:
		var h := _find_hit(p[i], p[1 - i])
		if not h.is_empty():
			found.append(h)
	for h: Dictionary in found:
		var a: Fighter = h["a"]
		var d: Fighter = h["d"]
		var attack := String(a.sprite.animation)
		var strength := &"heavy" if attack.ends_with("heavy") else (&"medium" if attack.ends_with("medium")
			else &"light")
		# Crouching attacks hit low, jumping attacks overhead, standing attacks mid (Kvon's guard rule).
		var level := &"low" if attack.begins_with("attack_c") else (&"overhead" if attack.begins_with("attack_j")
			else &"mid")
		var away := 1.0 if d.position.x >= a.position.x else -1.0
		a.attack_hit = true
		_freeze = maxi(_freeze, Fighter.HIT_FREEZE[strength])
		var guarded := d.take_hit(strength, level, a.sprite.animation == &"attack_cheavy", away)
		_add_fx(&"barrier" if guarded else &"spark", h["contact"], -away)
		if not guarded:
			_lost_wait[p.find(d)] = LOST_HP_DELAY
		if _trace:
			if guarded:
				print("GUARD ", a._tick, " ", attack, " ", level, " ", d.sprite.animation)
			else:
				print("HIT ", a._tick, " ", attack, " ", Fighter.DAMAGE[strength], " dummy_hp=", d.hp, " ",
					d.state, " combo=", d.combo_hits)
	if mode != "training" and _phase == "fight" and (p[0].hp == 0 or p[1].hp == 0):
		_phase = "ko"
		_phase_t = 0
		_winner = -1 if p[0].hp == 0 and p[1].hp == 0 else (0 if p[1].hp == 0 else 1)
		if _winner >= 0:
			_wins[_winner] += 1
		if _trace:
			print("KO winner=", _winner, " wins=", _wins)


## Attacker a's hitbox overlapping defender d's hurtbox (a knocked-down fighter can't be hit).
func _find_hit(a: Fighter, d: Fighter) -> Dictionary:
	if a.attack_hit or a.state != &"control" or d.state == &"down":
		return {}
	for hb: Rect2 in a.boxes(BOXES.HIT):
		for b: Rect2 in d.boxes(BOXES.HURT):
			if hb.intersects(b):
				return {"a": a, "d": d, "contact": hb.intersection(b).get_center()}
	return {}


## Pushback after a hit or guard: the one hit slides away, slowing; pinned at a screen edge, the attacker slides
## back instead.
func _pushback_step() -> void:
	for i in 2:
		var d := p[i]
		if d.push_v < 0.2 or d.state == &"hurt_air":
			d.push_v = 0.0
			continue
		var to := clampf(d.position.x + d.push_dir * d.push_v, Fighter.LEFT_LIMIT, Fighter.RIGHT_LIMIT)
		var left := d.push_v - absf(to - d.position.x)
		d.position.x = to
		if left > 0.0:
			var a := p[1 - i]
			a.position.x = clampf(a.position.x - d.push_dir * left, Fighter.LEFT_LIMIT, Fighter.RIGHT_LIMIT)
		d.push_v *= Fighter.PUSH_SLOW


## When the two fighters' middle hurtboxes touch they push each other apart (Kvon): the overlap is split, so
## walking into the other shoves it along at half speed; one at a screen edge can't move, so the other takes it.
func _push_apart() -> void:
	var overlap := 0.0
	for a: Rect2 in p[0].middle_box(BOXES.HURT):
		for b: Rect2 in p[1].middle_box(BOXES.HURT):
			if a.intersects(b):
				overlap = maxf(overlap, minf(a.end.x, b.end.x) - maxf(a.position.x, b.position.x))
	if overlap <= 0.0:
		return
	var side := 1.0 if p[1].position.x >= p[0].position.x else -1.0
	var to := clampf(p[1].position.x + side * overlap * 0.5, Fighter.LEFT_LIMIT, Fighter.RIGHT_LIMIT)
	var moved := absf(to - p[1].position.x)
	p[1].position.x = to
	p[0].position.x = clampf(p[0].position.x - side * (overlap - moved), Fighter.LEFT_LIMIT, Fighter.RIGHT_LIMIT)


## Rounds (match modes): "ROUND n" / "FIGHT!", fight, K.O. pause, then the next round or the winner, then the menu.
func _phase_step() -> void:
	if mode == "training":
		return
	_phase_t += 1
	if _phase == "intro" and _phase_t >= INTRO_FRAMES:
		_phase = "fight"
	elif _phase == "ko" and _phase_t >= KO_FRAMES:
		if _wins[0] >= ROUNDS_TO_WIN or _wins[1] >= ROUNDS_TO_WIN:
			_phase = "win"
			_phase_t = 0
		else:
			_round += 1
			_start_round()
	elif _phase == "win" and _phase_t >= WIN_FRAMES:
		_to_menu()


func _start_round() -> void:
	_phase = "intro"
	_phase_t = 0
	_cpu_plan.clear()
	for i in 2:
		p[i].reset(START_X[i], 1.0 if i == 0 else -1.0)
		p[i].hp = _start_hp
		_hp_shown[i] = float(_start_hp)
	if _trace:
		print("ROUND ", _round, " wins=", _wins)


func _to_menu() -> void:
	if _trace:
		print("TO MENU")
	get_tree().change_scene_to_file("res://scenes/menu.tscn")


## The simple CPU (Kvon): walks in or backs off, attacks when in range (lows and jump-ins too), guards some
## attacks by holding back (crouching against lows), and after landing its launcher jumps in for a juggle.
## Every decision is a short plan of held buttons; a few frames pass between decisions.
func _cpu_input(me: Fighter, foe: Fighter) -> Dictionary:
	var now := _frames
	if me.state != &"control":
		_cpu_plan.clear()
		_cpu_next = now + _rng.randi_range(4, 10)
	var foe_attack := String(foe.sprite.animation) if foe.is_attacking() else ""
	var dist := absf(foe.position.x - me.position.x)
	if foe_attack != "" and foe_attack != _cpu_seen_attack and me.state == &"control" and dist < 330.0:
		_cpu_seen_attack = foe_attack
		if _rng.randf() < 0.5:
			_cpu_plan = [{"at": now + _rng.randi_range(2, 6), "keys": ["back"] + (["down"] if
				foe_attack.begins_with("attack_c") else []), "len": 26}]
			_cpu_next = now + 30
	if foe_attack == "":
		_cpu_seen_attack = ""
	if foe.state == &"hurt_air" and me.state == &"control" and not me.is_airborne() and _cpu_plan.is_empty() \
			and _rng.randf() < 0.6:
		# Juggle: jump in after it and strike.
		_cpu_plan = [{"at": now, "keys": ["up", "forward"], "len": 4},
			{"at": now + 14, "keys": ["medium" if _rng.randf() < 0.5 else "light"], "len": 2}]
		_cpu_next = now + 50
	if now >= _cpu_next and _cpu_plan.is_empty() and me.state == &"control":
		var r := _rng.randf()
		if dist > 300.0:
			if r < 0.2:
				_cpu_plan = [{"at": now, "keys": ["up", "forward"], "len": 4},
					{"at": now + 20, "keys": ["heavy"], "len": 2}]
			else:
				_cpu_plan = [{"at": now, "keys": ["forward"], "len": _rng.randi_range(18, 34)}]
		elif dist > 190.0:
			if r < 0.35:
				_cpu_plan = [{"at": now, "keys": ["forward"], "len": _rng.randi_range(10, 18)}]
			elif r < 0.6:
				_cpu_plan = [{"at": now, "keys": ["medium"], "len": 2}]
			elif r < 0.75:
				_cpu_plan = [{"at": now, "keys": ["down", "medium"], "len": 3}]
			else:
				_cpu_plan = [{"at": now, "keys": ["back"], "len": _rng.randi_range(8, 14)}]
		else:
			if r < 0.25:
				_cpu_plan = [{"at": now, "keys": ["light"], "len": 2}]
			elif r < 0.45:
				_cpu_plan = [{"at": now, "keys": ["down", "light"], "len": 3}]
			elif r < 0.6:
				_cpu_plan = [{"at": now, "keys": ["down", "heavy"], "len": 3}]
			elif r < 0.75:
				_cpu_plan = [{"at": now, "keys": ["heavy"], "len": 2}]
			else:
				_cpu_plan = [{"at": now, "keys": ["back"], "len": _rng.randi_range(10, 18)}]
		_cpu_next = now + _rng.randi_range(14, 30)
	var inp := {}
	var keep: Array[Dictionary] = []
	for step: Dictionary in _cpu_plan:
		if now >= step["at"] and now < step["at"] + step["len"]:
			for k: String in step["keys"]:
				inp[k] = true
		if now < step["at"] + step["len"]:
			keep.append(step)
	_cpu_plan = keep
	return inp


func _set_guard_mode(m: int) -> void:
	_guard_mode = m
	if mode == "training":
		p[1].guard_mode = GUARD_MODES[m]


func _unhandled_key_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo):
		return
	match event.physical_keycode:
		KEY_F1:
			_show_boxes = not _show_boxes
		KEY_ESCAPE:
			_to_menu()
		KEY_G:
			if mode == "training":
				_set_guard_mode((_guard_mode + 1) % GUARD_MODES.size())
		KEY_R:
			if mode == "training":
				for i in 2:
					p[i].reset(START_X[i], 1.0 if i == 0 else -1.0)
					_hp_shown[i] = float(Fighter.MAX_HP)


func _add_fx(kind: StringName, pos: Vector2, dir: float) -> void:
	_fx.append({"kind": kind, "pos": pos, "dir": dir, "age": 0})


func _draw_boxes() -> void:
	if not _show_boxes:
		return
	for f: Fighter in p:
		for r: Rect2 in f.boxes(BOXES.HURT):
			_box_view.draw_rect(r, Color(0.2, 0.5, 1.0, 0.22))
			_box_view.draw_rect(r, Color(0.3, 0.6, 1.0, 0.9), false, 2.0)
		for r: Rect2 in f.middle_box(BOXES.HURT):
			_box_view.draw_rect(r, Color(1.0, 0.9, 0.2, 0.9), false, 2.0)
		for r: Rect2 in f.boxes(BOXES.HIT):
			_box_view.draw_rect(r, Color(1.0, 0.15, 0.15, 0.28))
			_box_view.draw_rect(r, Color(1.0, 0.2, 0.2, 0.95), false, 2.0)


## Hit spark: a white flash with gold rays. Guard barrier (Kingdom Hearts style): a pale blue hexagon shield.
func _draw_fx() -> void:
	for e: Dictionary in _fx:
		var pos: Vector2 = e["pos"]
		if e["kind"] == &"spark":
			var t := float(e["age"]) / SPARK_FRAMES
			for k in 8:
				var d := Vector2.from_angle(TAU * k / 8.0 + 0.3)
				var inner := 8.0 + 18.0 * t
				var outer := inner + (46.0 if k % 2 == 0 else 26.0) * (1.0 - 0.4 * t)
				_fx_view.draw_line(pos + d * inner, pos + d * outer, Color(1.0, 0.9, 0.45, 1.0 - t), 5.0)
			_fx_view.draw_circle(pos, 16.0 * (1.0 - t), Color(1, 1, 1, 1.0 - t))
		else:
			var t := float(e["age"]) / BARRIER_FRAMES
			var center := pos + Vector2(e["dir"] * 8.0, 0)
			for ring in 2:
				var r := (78.0 + 22.0 * t) * (1.0 if ring == 0 else 0.7)
				var pts := PackedVector2Array()
				for k in 7:
					var ang := TAU * k / 6.0 + PI / 6.0
					pts.append(center + Vector2(cos(ang) * r * 0.6, sin(ang) * r))
				if ring == 0:
					_fx_view.draw_colored_polygon(pts.slice(0, 6), Color(0.55, 0.85, 1.0, 0.45 * (1.0 - t)))
				_fx_view.draw_polyline(pts, Color(0.9, 0.98, 1.0, 1.0 - t), 4.0 if ring == 0 else 2.5)


## Kingdom Hearts style health bars (dark frame + light rim, green bar with a bright top stripe and darker bottom,
## red for health just lost), names, round-win markers, the announcer text and the training guard mode.
func _draw_hud() -> void:
	var font := ThemeDB.fallback_font
	var ink := Color8(10, 16, 40)
	var names := ["SORA", "SORA" if mode == "pvp" else ("SORA (CPU)" if mode == "cpu" else "TRAINING DUMMY")]
	for i in 2:
		var bar := Rect2(40.0 if i == 0 else 720.0, 34.0, 520.0, 20.0)
		_hud.draw_rect(bar.grow(4.0), ink)
		_hud.draw_rect(bar.grow(4.0), Color8(185, 200, 232), false, 2.0)
		_hud.draw_rect(bar, Color8(28, 34, 58))
		for part in 2:
			var share: float = (_hp_shown[i] if part == 0 else float(p[i].hp)) / Fighter.MAX_HP
			var w := bar.size.x * share
			var fill := Rect2(bar.position.x if i == 0 else bar.end.x - w, bar.position.y, w, bar.size.y)
			if part == 0:
				_hud.draw_rect(fill, Color8(214, 40, 40))
			else:
				_hud.draw_rect(fill, Color8(46, 196, 64))
				_hud.draw_rect(Rect2(fill.position, Vector2(w, 5)), Color8(150, 245, 150))
				_hud.draw_rect(Rect2(fill.position + Vector2(0, 15), Vector2(w, 5)), Color8(24, 128, 44))
		var side := HORIZONTAL_ALIGNMENT_LEFT if i == 0 else HORIZONTAL_ALIGNMENT_RIGHT
		var other := HORIZONTAL_ALIGNMENT_RIGHT if i == 0 else HORIZONTAL_ALIGNMENT_LEFT
		var at := Vector2(bar.position.x, 26)
		_hud.draw_string_outline(font, at, names[i], side, bar.size.x, 18, 4, ink)
		_hud.draw_string(font, at, names[i], side, bar.size.x, 18, Color8(235, 240, 255))
		_hud.draw_string_outline(font, at, str(p[i].hp), other, bar.size.x, 16, 4, ink)
		_hud.draw_string(font, at, str(p[i].hp), other, bar.size.x, 16, Color8(170, 255, 170))
		if mode != "training":
			for k in ROUNDS_TO_WIN:
				var c := Vector2((bar.position.x + 12 + 26 * k) if i == 0 else (bar.end.x - 12 - 26 * k), 72)
				_hud.draw_circle(c, 9.0, ink)
				_hud.draw_circle(c, 7.0, Color8(255, 210, 70) if _wins[i] > k else Color8(48, 56, 86))
	if mode == "training":
		var gm := "GUARD: %s  (G)" % GUARD_NAMES[_guard_mode]
		_hud.draw_string_outline(font, Vector2(720, 76), gm, HORIZONTAL_ALIGNMENT_RIGHT, 520.0, 15, 4, ink)
		_hud.draw_string(font, Vector2(720, 76), gm, HORIZONTAL_ALIGNMENT_RIGHT, 520.0, 15, Color8(190, 225, 255))
		return
	var text := ""
	if _phase == "intro":
		text = ("ROUND %d" % _round) if _phase_t < 60 else "FIGHT!"
	elif _phase == "ko":
		text = "K.O." if _phase_t < 80 or _winner < 0 else ("DRAW" if _winner < 0 else "")
		if _phase_t >= 80 and _winner >= 0:
			text = "%s WINS THE ROUND" % ("PLAYER 1" if _winner == 0 else ("CPU" if mode == "cpu" else "PLAYER 2"))
	elif _phase == "win":
		text = "%s WINS!" % ("PLAYER 1" if _wins[0] > _wins[1] else ("CPU" if mode == "cpu" else "PLAYER 2"))
	if text != "":
		_hud.draw_string_outline(font, Vector2(0, 300), text, HORIZONTAL_ALIGNMENT_CENTER, 1280.0, 64, 10, ink)
		_hud.draw_string(font, Vector2(0, 300), text, HORIZONTAL_ALIGNMENT_CENTER, 1280.0, 64, Color8(255, 226, 120))
	var help := "P1: WASD move  U/I/O attack     " + ("P2: arrows move  numpad 7/8/9 attack     " if mode == "pvp"
		else "") + "Esc: menu   F1: boxes"
	_hud.draw_string_outline(font, Vector2(0, 708), help, HORIZONTAL_ALIGNMENT_CENTER, 1280.0, 15, 4, ink)
	_hud.draw_string(font, Vector2(0, 708), help, HORIZONTAL_ALIGNMENT_CENTER, 1280.0, 15, Color8(200, 215, 240))


func _capture(path: String) -> void:
	await get_tree().create_timer(1.5).timeout
	await RenderingServer.frame_post_draw
	var error := get_viewport().get_texture().get_image().save_png(path)
	print("CAPTURE ", path, " error=", error)
	get_tree().quit()
