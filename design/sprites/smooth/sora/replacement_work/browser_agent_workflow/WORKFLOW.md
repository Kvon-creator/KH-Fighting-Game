# Gemini browser workflow

User authorization covers sprite-generation prompts, project art-reference uploads to Gemini, reviewing its outputs and sending concrete corrections. Google authentication is performed by the user. Final artwork approval belongs to the user.

Latest correction: the user rejects the discontinuous poses and malformed weapons. No generated sheet is an approved animation. The current still-image trial anchors the transition to the actual approved idle and checks small anatomical changes before extending it. See `ready/run_start/gemini_browser_trial/CONTINUITY_PLAN.md` and candidate review notes. Phone pairing is deferred.

## Connection

From PowerShell:

```powershell
& 'D:\KH Fighting Game\design\sprites\smooth\sora\replacement_work\browser_agent_workflow\Start-BraveGemini.ps1'
```

The launcher uses installed Brave, port 9222 on loopback and a separate profile under `.local/browser-agent/`. It checks the resolved workspace, executable, listener address and owning process. Existing personal Brave windows do not need to close. The profile and browser diagnostics are excluded from Git. No extensions, packages, firewall rules or global Codex settings are changed.

Sign in to Gemini in that separate window. Tell Codex when the chat is ready. A port is a connection mechanism, not a replacement for platform approval or login.

## References to upload

1. `ready/standing_idle/sora_stand_idle_00.png` — approved style and KH2 design.
2. `ready/run_loop/layers/frame_00_review_v1/sora_run_loop_00_review.png` — reviewed carry/grip/pose; not full-cycle approval.
3. `design/references/Sora_KHIV_Render.webp` — weapon and same-arm shoulder carry only.
4. Optional `ready/run_loop/layers/art_pass_05/kingdom_key_master_finished.png` — connected geometry construction reference. The approved finished idle governs detailed design; do not require its simplified angular cutouts to override the idle's rounded cutouts. This reference does not change the complete-image output requirement.

Paths beginning `ready/` are relative to `design/sprites/smooth/sora/replacement_work/`.

`PILOT_PROMPT.txt` is the historical near-arm pilot, not the current production prompt. No repository instructions, personal files, credentials or browser-profile files are uploaded.

October10 correction: the user prefers the opposite far arm/back shoulder, with the shaft behind Sora's head. Attempt06 did not change the original carry. A fresh conversation with `--reference-set far-carry` uploaded only the approved idle and KHIV photo; attempt08 establishes the new provisional carry with both arms. Keep earlier near-arm art preserved. For this fresh context, use `FAR_CARRY_PILOT.txt`/`FAR_CARRY_REFINE_08.txt` rather than historical near-arm prompts. The new nine-pose run-start request is `RUN_START_09_POSES.txt`.

The nine-pose result was rejected for discontinuity/missing and malformed weapons. The first guided opening segment still contains tiny captions, nearly duplicated00/01 poses and registration changes from the idle. Middle sheet04 reversed facing; edits05/06 retained the wrong weapon angle; fresh07 changed the angle but changed proportions and grip. Preserve these diagnostic/rejected attempts. `build_start_pose_guides.py` exports whole-frame schematic references with a fixed225px projected weapon axis; the current `guides_clean/` removes labels/ground lines. Older annotated `guides/` remains historical. Neither guide set is accepted final geometry or finished sprite layers.

Run-start08 (`RUN_START_ADJACENT_01.txt`, `--reference-set idle-only`) retains planted boots and a connected weapon but makes too large a lean for the first adjacent frame. Use it only as a provisional deep-anticipation endpoint. Run-start09 (`RUN_START_COMPRESSION_INBETWEENS.txt`, `--reference-set anticipation-endpoints`) requests four genuine complete-image intermediates between the actual idle and08. Inspect the actual grid, extract it, and build the six-pose diagnostic with `build_anticipation_review.py`. This helper uses unaligned whole canvases, preserves source hashes and creates normal/slow/128px previews with a shared palette. It does not repair poses, create layers or confer approval. Review the endpoint transition, head/weapon scale and every adjacent pose before further lift/stride production.

That bridge failed visual review. The separate `register_anticipation_review.py` diagnostic registers complete drawings to planted soles, recording scale/translation/source hashes. This corrects export framing, not movement or weapon shape; its result still has abrupt joint motion and overshoots. Never use it on stride/airborne poses. Run-start10's minimal compression matches style/framing but lacks a convincingly new joint phase.11 makes a clear near-hand release but extends it too far.12 edits that complete release endpoint to place the empty hand close to the guard. Do not accept a new pose from pixel differences or the provider's prose alone.

For a single adjacent-frame diagnostic, use `build_anticipation_review.py --adjacent-attempt attempt_10 --review adjacent_review_v1`. It keeps the reference and candidate on their original whole canvases. `audit_browser_trials.py` verifies established reference hashes, captured prompt/receipt consistency, original preservation after extraction and actual native image formats. `AUDIT.json` is an updated file-provenance checkpoint, not an automatic art judge.

`extract_sheet_review.py` extracts an already inspected regular grid into opaque512px full-frame PNGs, a contact sheet and normal/slow/128px GIFs. It uses a uniform whole-cell export ratio, never body/weapon parts or per-pose rescaling. It records source hashes and clipping risks and preserves the original download. Pass `--grid-confirmed` only after inspecting the actual image. Frame hashes establish distinct pixels, not correct anatomy or smooth timing; those remain visual checks.

## Review and corrections

1. Preserve every original and prior local candidate. Save each Gemini attempt under `ready/<animation>/gemini_browser_trial/attempt_XX/`, including original output, exact sent prompt, response, dimensions and review notes. Do not overwrite rejected attempts.
2. Inspect the actual downloaded image against the approved idle at working size and at 128px. Check face/hair, silhouette, proportions, KH2 costume, linework, fabric/skin/boot finish, right-facing three-quarter view and complete canvas fit.
3. Check the grip is not inverted. Trace pommel → grip → guard/collar → shaft → key head. Require consistent connected geometry, same-arm shoulder carry and a tip pointing slightly toward the foreground. Check overlaps and the attached chain.
4. If a visual check fails, give Gemini the specific defect and location, what the reference shows, the required correction and the features already accepted. Request a new complete image. Review it again. Do not label an unfinished construction pose approved.
5. If the artwork passes, present the image and findings to the user for final approval. Passing reviewer checks does not replace user approval. Do not replace gameplay assets before that approval.
6. For a refusal, quota/payment prompt, login/CAPTCHA or service error, record the exact message and report it. Do not disguise the character or bypass the refusal. Generation speed and success are not guaranteed.

## Animation production after the pilot

Produce one animation at a time: run start, run loop, run stop. Each is a complete image per frame, without individual layers. Refine running to approved-idle quality before aerial movement.

- Run start: about 8–12 genuine poses from the approved two-hand idle into a forward lean, transfer to the correct shoulder carry, first push-off and contact into the loop. The weapon must travel continuously between endpoint poses.
- Run loop: 16 poses, alternating near/far leading legs. Each half progresses through contact, compression, passing, late passing, heel-off, toe-off, flight and opposite-foot pre-contact. No mirrored substitute for the other stride, scaled copies or repeated static upper body. Coordinate shoulders, pelvis, free-arm counter-swing, small body bob and cloth/chain lag. Review the final-to-first seam at normal and slow speeds.
- Run stop: about 8–12 poses from a loop contact into braking, shortening steps, rising/settling and returning to the approved idle grip and weapon angle. Check both transition seams.

Request 512px RGBA frames or a regular sheet with complete equal-sized cells. Verify native dimensions, actual alpha and ordering; never claim that an upscaled image was generated at native resolution. Build local frame extraction, contact sheets and animated previews only after confirming the layout. Initial loop timing may use 60ms/frame for review; it is not approved gameplay timing.

Known format limitation: the current Gemini image pipeline supplies opaque JPEGs, not true alpha. Do not repeatedly request transparency; complete art review first, then make a separate reviewed transparent export. Native downloads so far are2048px originals;512px is a whole-frame export size.

Native video was tested once in run-loop09 and refused. Exact provider message: `I can't generate the video you requested right now due to interests of third-party content providers. Can I help you with something else?` Its saved raw response also includes an inconsistent progress footer. This is a provider content refusal, not a permissions rejection, validation failure or verified service outage. No video was produced or extracted; do not retry or disguise that request. Continue only the separately authorized still-image workflow. No media packages were installed.

## Compact agent exchange

The main driver is the installed Node runtime. The optional PowerShell wrapper is blocked by the sandbox's PowerShell execution policy; no policy change is required to run the Node driver directly.

```powershell
node design/sprites/smooth/sora/replacement_work/browser_agent_workflow/gemini_cdp.mjs exchange --prompt design/sprites/smooth/sora/replacement_work/browser_agent_workflow/CORRECTION_05.txt --output design/sprites/smooth/sora/replacement_work/ready/run_loop/gemini_browser_trial/attempt_05
```

One invocation verifies the composer, submits the stored concise prompt once, waits for a new generated image, saves the response/preview and full-size download, and returns a compact status. Receipts record reference hashes and keep final user approval pending. Rerunning a submitted attempt collects its result without sending the prompt again. No visual acceptance or automatic production replacement is performed by the script; Codex reviews the actual artwork and writes the next correction when needed. `inspect --verbose true` is reserved for interface troubleshooting.

If multiple Gemini tabs exist, `inspect` lists their IDs and stops. Select the observed intended tab with `--target ID` on subsequent commands. New receipts bind in-progress attempts to that tab. `--reference-set far-carry` selects the two-reference fresh context; the `upload` command attaches it through the observed image input. Compact inspection suppresses generated prompt descriptions in image alt text.

The second attempt exercised the full exchange successfully inside the sandbox: one correction, one new image, a saved response, 1024px JPEG preview and 2048px JPEG original. Gemini stated that its current pipeline does not support true transparency. Treat these as art candidates requiring a later transparent sprite export; never label them RGBA sprites or native512px outputs.

The example above is the already completed fifth attempt: it returns the saved result and does not submit again. For a new revision, save a concise new prompt in this workflow folder and select a new attempt directory. `--timeout 180` controls the collection deadline (1-600 seconds); a timeout is collected by rerunning the same attempt. Optional `--weapon-reference true` adds the local construction master to that exchange. Use compact status for ordinary work and full inspection only when controls change.

Historical pilot: loop05 received positive general-art feedback with an explicit opposite-arm carry revision request; it is not final approval of that unchanged pose. Loop08 is the provisional far-arm carry reference with both arms restored, still pending final approval and cycle consistency. Attempts01-08 are single-pose revisions, not an animation. Original downloads and local art remain preserved; no production sprites or engine files were replaced.

`CORRECTION_04.txt` and `CORRECTION_05.txt` are historical submitted prompts. Their insistence on rectangular cutouts was a reviewer error corrected by inspecting the approved finished idle. Do not reuse that restriction for new work. `verify_trial.py` checks the four unchanged reference hashes and records actual image formats/dimensions; it is a pilot audit helper, not an automatic visual judge.

`gemini_cdp.mjs` uses the installed Node runtime and its built-in WebSocket/fetch support. No dependencies are installed. It limits target tabs to `https://gemini.google.com/app`, requires a unique target and uses fresh page observations for each action. Inspection/screenshot comes before choosing controls. It does not automate login, change security settings or read cookies.

```powershell
node design/sprites/smooth/sora/replacement_work/browser_agent_workflow/gemini_cdp.mjs inspect
node design/sprites/smooth/sora/replacement_work/browser_agent_workflow/gemini_cdp.mjs screenshot
```

Browser helper failure observed October 10: `node_repl kernel exited unexpectedly`, diagnostics contained `windows sandbox failed: helper_unknown_error: setup refresh had errors`. The launcher and direct connection are a separate supported-port path; verify their actual results before reporting a successful connection.

Sources: [Brave command-line flags](https://support.brave.app/hc/en-us/articles/360044860011-How-Do-I-Use-Command-Line-Flags-in-Brave), [Chromium profile isolation for debugging](https://developer.chrome.com/blog/remote-debugging-port?hl=en), [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/).
