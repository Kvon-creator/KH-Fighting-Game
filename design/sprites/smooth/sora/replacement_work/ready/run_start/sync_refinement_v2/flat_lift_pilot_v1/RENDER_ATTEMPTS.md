# Local rendering diagnostics

The first PowerShell launch was stopped by local script execution policy: `running scripts is disabled on this system`. This is a local execution-policy restriction, not image-tool content moderation. An approved process-only override was then used; system policy was not changed.

The first render failed the painter's pixel-preservation guard before saving a candidate: `Painting touched protected face/free arm/lower body: 19173`. Drawing the complete PNG through GDI changes some antialias colors when converting alpha. The painter now clones native pixels and verifies the clone before applying direct local paint. Source assets remain unchanged. This is a local validation failure, not a service or permission rejection. No failed candidate was exported.
