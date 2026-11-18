# Developing the personal version

## Retired: reset appearance (2026-11-14 to 2026-11-17)

`codex/theme-reset` added **Reset to Blender Default** to Wanderer's Appearance
preferences. Upstream 2.96.128 removed every theme button from the add-on (the
themes are now `.xml` files in `themes/`, loaded from Blender's Preferences >
Themes, which has its own reset). The operator and `tests/t_theme_reset.py` were
dropped in the 17 November update; both remain in Git history (`718b135`).

## Version and Git history

Keep `bl_info.version`, `blender_manifest.toml` and the extension ID unchanged
for personal changes. When bringing in a release, adopt the author's version
unchanged: the current upstream base is **2.96.128** (previously 2.96.127).
Use the branch and Git commit hash to identify a custom build. The official
upstream changelog is left alone; personal development notes live here.

The original repository is the `upstream` remote. In this checkout its push URL
is disabled, and `push.default` is `nothing`. `upstream/main` tracks the author's
baseline after fetching. Our `main` holds the tested personal version and
tracks `origin/main`. The personal fork is
[rocksonchan/wanderer-cad](https://github.com/rocksonchan/wanderer-cad), connected
as `origin`. Publish our main branch explicitly:

```sh
git push -u origin main
```

Start each new feature on a new `codex/` branch from our updated `main`. Test it,
then merge it into our `main` and push.

## Reload without reinstalling

The installed extension directory can be a symbolic link to this checkout's
`wanderer_cad` folder. Blender retains its normal extension module name and
preferences, but reads the edited Python files directly. Back up the original
installed folder outside Blender's extension repository before making the link.
This one-time setup is host-specific, not part of the packaged add-on.

After editing:

1. Save the source files and finish or cancel any active Wanderer command.
2. Run `scripts/reload_addon.py` inside Blender via MCP or the Text Editor.
3. Try the changed behaviour. No ZIP installation is needed.

The helper disables only Wanderer, reloads its modules, and enables it again.
It refuses to run if the active Wanderer does not resolve to this checkout or
a Wanderer command is active. It does not reload every other Blender add-on.

For the Python Console, use an absolute path:

```python
import runpy
_ = runpy.run_path('/absolute/path/to/wanderer-cad/scripts/reload_addon.py', run_name='__main__')
```

Keep the checkout at its linked location. While linked, update through Git;
installing an extension ZIP over this development link could overwrite source
files. To return to the installed release, disable Wanderer, remove only the
symbolic link, restore the backed-up directory, and enable Wanderer again.

## Blender orbit after switching views

The upstream default enabled `view_pan` even with Navigation style set to
Blender. `navigation.start_navigation()` deliberately sends the orbit button
to Blender's pan operator in aligned orthographic views. This explains why MMB
orbits in perspective but pans immediately after choosing Top, Front or Side.
Leaving the axis-aligned view stops that override; it is not a stuck mouse.

Our default leaves `view_pan` off. Selecting Blender navigation also clears a
previously saved pan override. Selecting Rhino enables side-view panning, and
Custom preserves the chosen setting. The checkbox remains available to opt in,
with a visible explanation when enabled. Existing saved preferences are not
silently migrated: select Blender again, or turn off **Pan in orthographic side
views**, then save preferences. This correction was applied to the development
Blender session through MCP.

Normal Blender navigation remains MMB orbit, Shift+MMB pan and Ctrl+MMB zoom
(the inspected Mac keymap also accepts Command+MMB for zoom). No replacement
orbit implementation or changes to named-view storage are needed.

Focused regression checks:

```sh
blender --background --factory-startup --python-exit-code 1 --python tests/t_navigation.py
blender --factory-startup --enable-event-simulate --python tests/t_navigation_mouse.py
```

The second command opens and closes a disposable Blender window. It reproduces
the old Top-view pan, tests real MMB drags from all six axis views, then checks
Shift pan and Ctrl/Command zoom. Require `PASS navigation mouse suite` in its
output. Both suites preserve scene objects; never run them in a working session.
Note: both suites load this checkout's `wanderer_cad`, not `WANDERER_SRC`.

## Kept against upstream: DWG import and export (always keep)

**Rockson's rule: this feature stays in the fork whatever the author does.**
Upstream 2.96.128 removed DWG (no outside programs). Branch `codex/dwg-restore`
(18 November 2026) puts back the author's own 2.96.127 code, unchanged:

- `import_dxf.py`: `cad_converter()` finds ODA File Converter (or LibreDWG),
  `cad_convert()` / `dxf_file_to()`; Import and Export Model accept `.dwg`, with
  a DWG version (2018 default).
- `layout.py`: `DESSIN_OT_layout_export_dwg` and the **DWG** button in Print.
- `preferences.py` + `core.py`: the `oda_path` setting (default `""`) and the
  "DXF / DWG" preferences section.
- `command_line.py`, `languages.py`: `importdwg`, `dwgin`, `exportdwg`,
  `dwgout`, `saveasdwg` and their labels.

Every fork line carries a `FORK` comment (`grep -n FORK wanderer_cad/*.py`).

Tests: `tests/t_dwg.py` (32 checks: the author's 2.96.127 DWG tests with a fake
converter, plus a real round trip through `/Applications/ODAFileConverter.app`
when installed). The author's tests that check DWG is *gone* are flipped in the
fork: `t_cadio.py` section 4 and one check of `t_modeicons.py`.

Known limit (same as 2.96.127): Wanderer's R12 DXF keeps its units in a
comment, which ODA drops, so an exported DWG is "unitless" (the numbers are in
the unit chosen at export). When re-importing such a DWG, set Units by hand.

**Backup:** `fork-features/dwg-restore.patch` (code + tests), a copy in the study
folder `~/Documents/Claude/Projects/Wanderer blender addon study/fork-features/`.
If an author update breaks or removes DWG, re-apply it on the update branch:

```sh
git apply --3way fork-features/dwg-restore.patch
```

## Replaced by upstream: radius dimension on fillet corners

Our `codex/fillet-radius-dim` (16 November 2026, `8540b50`) let **Radius /
Diameter** measure a fillet. Upstream 2.96.128 added the same feature its own
way (`dimensions.arc_run()`), so the 17 November update took the author's
`dimensions.py` and dropped ours. `tests/t_filletdim.py` is kept: the author's
version passes all 9 checks.

## Rectangle tools ignore Ortho for the opposite corner

Our `codex/rect-ortho-diagonal` (17 November 2026, `bbcba85`) let Rectangle,
Plane, Ellipse: By Corners and Box skip Ortho (F8) / Polar (F10) for the
opposite corner. Upstream 2.96.128 added the same idea as `CORNER_STAGES = (1,)`
on Rectangle, Plane and Box, so the update took the author's code. The only
personal line left is `CORNER_STAGES = (1,)` on `DESSIN_OT_ellipse_coin` in
`tools_draw.py`. Regression check: `tests/t_rectortho.py` (10 checks).

## Snapping in CPlane 3 points and Vertical

Branch `codex/cplane-3pt-snap` (16 November 2026). **CPlane** is a plain
operator, not a `DessinBase` tool, so its 3-point (3) and Vertical (V) picks
only found a corner of the mesh face under the cursor (`cp_pick`) and otherwise
dropped the point on the current plane. Curve ends, midpoints, centres and
intersections were never snapped.

`DESSIN_OT_cplane.pick()` now asks Wanderer's object snaps first, the way
PushPull and the Gumball do: `collect_snap_points` once per command, then
`find_snap_in` (it follows the OSnap panel, and Disable turns it off), with the
last picked point as the Perp / Tan reference. If nothing is snapped it falls
back to `cp_pick` unchanged. The snapped point keeps its own height: it is not
projected onto the current plane, since it defines the new one. The usual snap
marker is drawn (`cp_snap_px_cb`). The change is limited to `cplane.py`.

Regression check: `tests/t_cplanesnap.py` (End / Mid / End on a raised curve,
Vertical on two curve ends, OSnap disabled, mesh face corners as before).
`t_prec6`, `t_autocp`, `t_compactbar` and `t_stressvar cplane` pass before and
after; `t_newcmds` keeps its two known baseline failures, unchanged.

## Test safely

Run each suite in a **separate background Blender process**:

```sh
blender --background --factory-startup --python-exit-code 1 --python tests/t_cplanesnap.py
```

For isolated tests, set `BLENDER_USER_RESOURCES`
(and any `BLENDER_USER_CONFIG` / `SCRIPTS` / `EXTENSIONS` overrides) to temporary
directories so theme and alias files cannot overwrite the working installation.

The other upstream suites may reset scenes. Do not run those suites inside a
working Blender session. Live MCP checks should be narrowly scoped to the
feature, with current scene and preferences preserved as appropriate.

## Bring in author updates

### Update on 17 November 2026

Merged upstream `f4601c5` (2.96.128) on `codex/upstream-update-20261117`. The
author uploaded through GitHub's web page (commits "Delete wanderer_cad
directory" / "Add files via upload"); Git still merged it normally. Conflicts:
`base.py`, `core.py`, `layout_engine.py`, `preferences.py`, `registration.py`,
`tests/t_prefsui.py`. Resolution: take the author's file for all of them, then
put back only the orbit fix (`view_pan` default off in `core.py` and
`preferences.py`, with its info label). Also took the author's `dimensions.py`,
`tools_draw.py` and `solids.py` (fillet radius and rectangle Ortho now upstream).
Dropped: theme reset and its test, English comment translations (`10fb3e4`).
Kept, merged cleanly: CPlane snapping (`cplane.py`), orbit fix (`navigation.py`).
After the update, the add-on differs from upstream in `core.py`, `cplane.py`,
`navigation.py`, `preferences.py` and one line of `tools_draw.py` only.

### Update on 16 November 2026

Merged upstream `05a534e` (2.96.127) into the personal history based on `a57d591`.
Integration was prepared in a separate Git worktree, leaving the linked Blender
checkout untouched during testing. Conflicts were limited to `preferences.py`
and `registration.py`: retained upstream's reorganized preference panels, six
themes, previous-theme restoration and new operators, then placed our factory
theme reset in Appearance and registered it alongside the upstream operators.
The default and Blender-style orbit correction remain in `core.py`,
`navigation.py` and `preferences.py`. Ghost was replaced by Carbon upstream;
the reset tests now cover all six current themes.

Validation on Blender 5.2.0 LTS: all 16 targeted suites passed (the 13 upstream
suites added or changed in this release, plus theme reset, navigation and real
mouse-event checks). This is not a run of the entire upstream suite. The Blend
Surface test needed a macOS-only harness correction: read state from the tool's
owning module instead of `invoke.__globals__`, since registration wraps `invoke`
on macOS. Its geometry assertions remain unchanged. The background test runner
now excludes the GUI-only mouse test, which is run separately.

### Next update

Save work and commit it first. Fetching downloads the author's commits without
changing the working files. Start an update branch from our current `main`,
using a fresh branch name for each update, and inspect the author's changes:

```sh
git switch main
git pull --ff-only origin main
git fetch upstream
git switch -c codex/upstream-update-YYYYMMDD
git log --oneline HEAD..upstream/main
git diff HEAD...upstream/main -- wanderer_cad/preferences.py wanderer_cad/registration.py
git merge upstream/main
```

**Fork features to keep after every update (check before merging into main):**

- [ ] **DWG import / export** — run `tests/t_dwg.py`. If it fails, or the merge
  removed DWG, re-apply `fork-features/dwg-restore.patch` (see "Kept against
  upstream: DWG import and export") and test again.

Resolve any conflicts by preserving the author's new behaviour and the
personal features. Run the focused suite again, inspect affected upstream tests, and
reload the add-on after the merge is complete. A clean text merge still needs
behaviour checks. Do not force-push or overwrite the author's files wholesale.

Once the update is tested and any conflict resolutions are committed, bring it
into our main branch and publish it to our fork:

```sh
git switch main
git merge --ff-only codex/upstream-update-YYYYMMDD
git push origin main
```

If `main` has advanced meanwhile, integrate its changes on the update branch
and test again before merging. Author updates are not automatic: merge them
when ready, preserving both our features and theirs.

## Package

`python3 scripts/build_zip.py` produces the normal installable ZIP. Keep custom
builds in a directory labelled with the Git commit hash so their origin is clear
without changing the add-on version or extension ID.
