# Developing the personal version

## First change: reset appearance

`codex/theme-reset` adds **Reset to Blender Default** in Wanderer's Appearance
preferences. It uses Blender's own theme reset and restores Wanderer's default
toolbar icon palette. As of upstream 2.96.127, it sits alongside the six theme
buttons and the author's separate **Restore my previous theme** action.
It keeps other Wanderer settings and keyboard shortcuts. It follows Blender's
normal preference-saving setting; it does not force-save all preferences.

The runtime change is limited to `preferences.py` and operator registration in
`registration.py`. Tests and development helpers are separate files.

## Version and Git history

Keep `bl_info.version`, `blender_manifest.toml` and the extension ID unchanged
for personal changes. When bringing in a release, adopt the author's version
unchanged: the current upstream base is **2.96.127** (previously 2.96.126).
Use the branch and Git commit hash to identify a custom build. The official
upstream changelog is left alone; personal development notes live here.

The original repository is the `upstream` remote. In this checkout its push URL
is disabled, and `push.default` is `nothing`. `upstream/main` tracks the author's
baseline after fetching. Our `main` holds the tested personal version, including
the reset feature, and tracks `origin/main`. The personal fork is
[rocksonchan/wanderer-cad](https://github.com/rocksonchan/wanderer-cad), connected
as `origin`. Publish our main branch explicitly:

```sh
git push -u origin main
```

Start each new feature on a new `codex/` branch from our updated `main`. Test it,
then merge it into our `main` and push. The original `codex/theme-reset` branch
is retained as a reference for the first feature.

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
The theme-reset suite remains a separate regression check.

## Test safely

Run the integration suite in a **separate background Blender process**:

```sh
blender --background --factory-startup --python-exit-code 1 --python tests/t_theme_reset.py
```

It applies Blueprint, Carbon, Midnight, Graphite, Vellum and Ivory; compares all readable theme values
against Blender's factory theme; checks the icon palette and repeated resets;
and verifies other sample settings, objects and shortcut counts are preserved.
It refuses to run in an interactive working session. It can also run through
the repository's existing `python scripts/run_tests.py theme_reset` with `bpy`.
It also checks that the author's previous-theme backup survives a factory reset
and can still be restored. For isolated tests, set `BLENDER_USER_RESOURCES`
(and any `BLENDER_USER_CONFIG` / `SCRIPTS` / `EXTENSIONS` overrides) to temporary
directories so theme and alias files cannot overwrite the working installation.

The other upstream suites may reset scenes. Do not run those suites inside a
working Blender session. Live MCP checks should be narrowly scoped to the
feature, with current scene and preferences preserved as appropriate.

## Bring in author updates

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

Resolve any conflicts by preserving the author's new behaviour and the reset
feature. Run the focused suite again, inspect affected upstream tests, and
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
