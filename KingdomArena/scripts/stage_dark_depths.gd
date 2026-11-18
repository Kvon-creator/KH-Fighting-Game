extends Node2D
## Dark Depths' living background (Kvon, November 18): the sky's clouds drift (Parallax2D autoscroll) and the embers /
## dark motes float (CPUParticles2D) on their own; this script only pulses the Heartless emblem's glow.

const PULSE_SECONDS := 3.2   # one slow breath: dim -> bright -> dim
const GLOW_MIN := 0.2
const GLOW_MAX := 0.8

var _t := 0.0

@onready var _glow: Sprite2D = $Pillars/EmblemGlow


func _process(delta: float) -> void:
	_t = fmod(_t + delta, PULSE_SECONDS)
	_glow.modulate.a = lerpf(GLOW_MIN, GLOW_MAX, 0.5 - 0.5 * cos(TAU * _t / PULSE_SECONDS))
