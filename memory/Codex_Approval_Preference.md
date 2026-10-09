# Routine work and approval prompts

**Fact or rule:** K'von wants work permitted by Agent Setup to proceed without
repeated "Allow" prompts. Routine actions within the requested task are already
authorized. Agent Setup's ask-first cases still apply when the necessary explicit
authorization has not already been given. Existing authorizations remain valid.

**Why:** K'von clarified this preference on October 9, 2026, after repeated
permission interruptions during the local sprite workflow.

**Settings:** The project-specific Codex settings file is `.codex/config.toml`.
The intended defaults are `approval_policy = "on-request"`,
`approvals_reviewer = "auto_review"`, and `sandbox_mode = "workspace-write"`.
This is the supported Approve for me combination: eligible runtime approvals
go to automatic review while the workspace boundary remains. A supplemental
review policy preserves Agent Setup's restrictions. The global settings at
`C:\Users\kvong\.codex\config.toml` are not changed.

**Activation and limits:** Reload Codex/start a new session to load project
defaults. A chat's explicit permission selection or managed requirements can
override local defaults. If the active selector still says Ask for approval,
choose Approve for me. Automatic review may deny an action; separate platform
prompts can still require a person. Do not promise that a local file suppresses
every possible platform approval or overrides Agent Setup.

**Instructions:** Root `AGENTS.md` directs the agent to read the original
Agent Setup and honor this preference. The Agent Setup file itself is unchanged.
