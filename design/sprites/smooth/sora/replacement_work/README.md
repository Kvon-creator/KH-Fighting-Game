# Sora animation folders

All animation-specific artwork and exports live under ready/:

- standing_idle/: standing guard, ten breathing frames, source sheet, sprite sheet, GIF, manifest and Preview.html.
- crouch_cycle/: source transition sheet, draft, full-cycle previews, combined sheet and manifest, plus Preview.html.
  - duck_down/: eight lowering frames, sheet and local manifest.
  - crouching_idle/: guard, source, four breathing frames, GIF and local manifest.
  - stand_up/: eight rising frames and local manifest.
- shimmy_forward/: source, ten frames, sheet, GIF, local manifest and Preview.html.
- shimmy_backward/: ten shared/reversed frames, sheet, GIF, local manifest, unused draft and Preview.html.
- attack_windup/: original wind-up retained because replacement generation was blocked.

Open a flow's Preview.html in a browser to play, pause, step, change speed or mirror facing.

Combined viewers:
- [Idle and crouch](ready/Animation_Previews.html)
- [Forward and backward shimmies](ready/Shimmy_Previews.html)

Shared manifests, metrics, generation logs and production status remain in ready/. Packaging scripts and AnimationPackaging.cs remain here because they serve multiple flows; templates/ holds shared viewer templates. Build scripts resolve sources in the flow folders and invoke organize_animation_flows.ps1 after export.

Future batches should get their own ready/<animation_flow>/ folders, such as run_start, run_loop and run_stop. Do not mix new animation frames into ready/ or the Sora root.

Organization checks: 72 unique PNG/GIF files retained identical hashes; 114 manifest frame/sheet paths and 76 viewer frame references resolved after the move. No Godot scripts, scenes or project settings were changed.
