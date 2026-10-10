# Project Location

**Fact or rule:** The current project workspace is D:\KH Fighting Game. Use this location rather than the previous OneDrive directory. Resolve asset and script paths relative to the project where possible.

**Why:** K'von moved the project and explicitly confirmed this path.

**October10 visibility correction:** K'von reported today's files missing from VS Code. Copy Path showed `C:\Users\kvong\OneDrive\Documents\KH Fighting Game\design\sprites\smooth\sora\replacement_work\ready`, the old copy. Current work and pushed commits are in `D:\KH Fighting Game`. Opened D's workspace and latest sprite using `code --new-window` in a separate window. Do not copy or move current work into the old OneDrive project to hide this mismatch; keep D as the canonical workspace. When files appear missing in an editor, compare its absolute folder path with the tool workspace before regenerating art.
