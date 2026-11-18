# Fork features kept against upstream

Patches of personal features that must survive every author update.
After merging an author update, run each feature's test; if it fails, re-apply its patch
on the update branch (`git apply --3way fork-features/<name>.patch`), then test again.

| Patch | Feature | Test | Made |
|---|---|---|---|
| `dwg-restore.patch` | DWG import / export through ODA File Converter (removed upstream in 2.96.128) | `tests/t_dwg.py` | 2026-11-18, on upstream 2.96.128 |

Regenerate a patch after changing its feature: `git diff <base> HEAD -- wanderer_cad tests > fork-features/<name>.patch`.
A copy of this folder lives in `~/Documents/Claude/Projects/Wanderer blender addon study/fork-features/`.
