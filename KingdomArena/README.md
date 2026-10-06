# Kingdom Arena Prototype â€” Godot 4.x

## Open and play
1. Extract the ZIP.
2. In Godot Project Manager choose Import and select KingdomArena/project.godot.
3. Open the project and press F6 on scenes/demo.tscn, or F5 to run the project.

Controls: A/D or Left/Right to move; Space/W/Up to jump; R to reset.

## Contents
- scenes/arena.tscn: reusable arena, background, solid floor, side walls, ceiling, and two spawn markers.
- scenes/demo.tscn: playable test scene with instructions.
- scenes/test_fighter.tscn: temporary CharacterBody2D with a 36 x 96 collider.
- scripts/test_fighter.gd: editable movement settings and controller.
- assets/arena_background.svg: original vector twilight courtyard background.

## Arena measurements
1280 x 720 viewport. Floor surface at y=600. Playable horizontal bounds x=0 to x=1280. Side walls are invisible, with their inner faces at the screen edges; the background has no boundary pillars. Walls extend above and below the viewport to prevent jumping around them. The invisible ceiling sits at y=0. Spawn positions refer to the center of a 96-pixel-tall character, placing its feet on the floor.

## Use in an existing Godot 4 project
Copy assets, scenes, and scripts into the project's root, preserving these folder names and paths. Avoid overwriting matching files in an existing project; if you move this package into a subfolder, update the res:// references in its scene files. Instance scenes/arena.tscn into your main scene. Add your own fighters at PlayerOneSpawn and PlayerTwoSpawn. The arena uses collision layer 1; the placeholder fighter uses layer 2 and collides with layer 1. The HUD and placeholder fighter exist only in the demo.

The prototype uses direct physical keyboard checks, so no Input Map setup is required. When building the combat system, replace these with configurable input actions. It includes no combat, camera tracking, or copyrighted Kingdom Hearts artwork.

Compatibility: uses Godot 4 CharacterBody2D and move_and_slide. Godot 3 is not supported. Runtime validation must be performed in Godot; no Godot executable was available in the creation environment.

