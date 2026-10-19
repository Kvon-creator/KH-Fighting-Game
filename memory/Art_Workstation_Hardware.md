# Art workstation hardware and Blender

**Fact or rule:** Kvon confirmed24GB system RAM on October19. Earlier inspection showed about23.4GiB usable memory and a GTX1650 with about4GB VRAM. System RAM and GPU VRAM are separate; do not describe the24GB as GPU memory or assume it satisfies an AI model's VRAM requirement.

**Why:** The user clarified his RAM while asking whether his installed Blender would work for the3D-to-sprite experiment.

**Software verification:** Blender5.2.2 LTS, buildd13f752e3b9c, installed at `C:\Users\kvong\AppData\Local\Programs\Blender5.2\blender.exe`. `--version`, CPU model/render export and saved-scene reopening succeeded. Blender was not on PATH or in project-local tools; locate installed software through registry metadata before assuming it is absent. No reinstall needed. Existing portable ComfyUI's unavailable CUDA is a result for that runtime, not proof Blender cannot use the graphics card. The first Blender test deliberately used CPU.
