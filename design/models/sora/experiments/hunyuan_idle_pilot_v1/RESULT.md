# Hunyuan3D2.1 idle-image pilot

The user authorized uploading the approved idle to the official Tencent Hunyuan3D2.1 Hugging Face demo. The source is unchanged; `reference_idle.png` is a byte-identical copy with SHA256 `baf8959c0e0d42b74bf7f6100a83ccf5c208a9decd5b98b95110f3129fbacdc7`.

The upload succeeded. `POST https://tencent-hunyuan3d-2-1.hf.space/call/generation_all` returned HTTP200 and event ID `93a82ac3e9e647a5a407e6585d1c16a9`. The event stream then returned exactly:

```text
event: error
data: null
```

No model or cause was returned. This is an accepted job ending in an unspecified service execution failure. There was no HTTP400/422 submission-validation response, HTTP401/403 permissions rejection or explicit content refusal. An internal validation, quota, authentication, moderation or runtime cause cannot be determined from `null`. No automatic retry or fallback submission was made.

Actual tool: `mcp__node_repl__js`, using built-in fetch without installing a package. Exact service arguments are in [request.json](request.json), with [API schema](api_info.json), [upload response](upload_response.txt), [submission response](submission_response.txt), [complete event stream](events.sse), [receipt](receipt.json) and [classification](failure_classification.json). The live schema exposes12 API parameters; its internal caption state is excluded. Used service defaults30steps, guidance5, seed1234, resolution256, background removal enabled,8000chunks and seed randomization disabled. This was image-conditioned generation, with no text prompt.

Blender modeling/rendering was verified separately. No Sora mesh was produced, so rigging or visual approval of an AI character cannot proceed from this result. No paid service, additional model/software installation, engine changes or production sprite replacement occurred.
