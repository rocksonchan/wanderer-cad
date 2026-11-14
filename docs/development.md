# Developing the personal version

## First change: reset appearance

`codex/theme-reset` adds **Reset to Blender Default** under the three theme
buttons in Wanderer's Appearance preferences. It uses Blender's own theme reset
and restores Wanderer's default toolbar icon palette, including after Ghost.
It keeps other Wanderer settings and keyboard shortcuts. It follows Blender's
normal preference-saving setting; it does not force-save all preferences.

The runtime change is limited to `preferences.py` and operator registration in
`registration.py`. Tests and development helpers are separate files.

## Version and Git history

Keep `bl_info.version`, `blender_manifest.toml` and the extension ID unchanged
for these personal development changes. The base version is **2.96.126**.
Use the branch and Git commit hash to identify a custom build. The official
upstream changelog is left alone; personal development notes live here.

The original repository is the `upstream` remote. In this checkout its push URL
is disabled, and `push.default` is `nothing`. `main` remains the unmodified
upstream baseline. The personal fork is
[rocksonchan/wanderer-cad](https://github.com/rocksonchan/wanderer-cad), connected
as `origin`. Publish the custom branch explicitly:

```sh
git push -u origin codex/theme-reset
```

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

## Test safely

Run the integration suite in a **separate background Blender process**:

```sh
blender --background --factory-startup --python-exit-code 1 --python tests/t_theme_reset.py
```

It applies Blueprint, Vellum and Ghost; compares all readable theme values
against Blender's factory theme; checks the icon palette and repeated resets;
and verifies other sample settings, objects and shortcut counts are preserved.
It refuses to run in an interactive working session. It can also run through
the repository's existing `python scripts/run_tests.py theme_reset` with `bpy`.

The other upstream suites may reset scenes. Do not run those suites inside a
working Blender session. Live MCP checks should be narrowly scoped to the
feature, with current scene and preferences preserved as appropriate.

## Bring in author updates

Save work and commit it first. Fetching downloads the author's commits without
changing the working files. Inspect the update before merging:

```sh
git fetch upstream
git log --oneline HEAD..upstream/main
git diff HEAD...upstream/main -- wanderer_cad/preferences.py wanderer_cad/registration.py
git switch codex/theme-reset
git merge upstream/main
```

Resolve any conflicts by preserving the author's new behaviour and the reset
feature. Run the focused suite again, inspect affected upstream tests, and
reload the add-on after the merge is complete. A clean text merge still needs
behaviour checks. Do not force-push or overwrite the author's files wholesale.

## Package

`python3 scripts/build_zip.py` produces the normal installable ZIP. Keep custom
builds in a directory labelled with the Git commit hash so their origin is clear
without changing the add-on version or extension ID.
