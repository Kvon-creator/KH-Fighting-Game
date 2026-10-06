extends CharacterBody2D
## Temporary movement controller. Replace this scene with your fighters later.
@export var move_speed: float = 360.0
@export var jump_speed: float = 680.0
@export var gravity: float = 1800.0
var spawn_position: Vector2
var facing: float = 1.0

func _ready() -> void:
	spawn_position = global_position
	queue_redraw()

func _physics_process(delta: float) -> void:
	var left := Input.is_physical_key_pressed(KEY_A) or Input.is_physical_key_pressed(KEY_LEFT)
	var right := Input.is_physical_key_pressed(KEY_D) or Input.is_physical_key_pressed(KEY_RIGHT)
	var direction := float(right) - float(left)
	velocity.x = direction * move_speed
	if direction != 0.0:
		facing = direction
		queue_redraw()
	if not is_on_floor():
		velocity.y += gravity * delta
	move_and_slide()

func _unhandled_key_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.physical_keycode in [KEY_SPACE, KEY_W, KEY_UP] and is_on_floor():
			velocity.y = -jump_speed
		if event.physical_keycode == KEY_R:
			global_position = spawn_position
			velocity = Vector2.ZERO

func _draw() -> void:
	draw_rect(Rect2(-18, -18, 36, 52), Color("55c7d4"))
	draw_circle(Vector2(0, -29), 17, Color("f2d5b0"))
	draw_rect(Rect2(-17, 34, 13, 14), Color("25324e"))
	draw_rect(Rect2(4, 34, 13, 14), Color("25324e"))
	draw_circle(Vector2(facing * 8, -31), 3, Color("25324e"))
