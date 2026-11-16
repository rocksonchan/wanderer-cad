"""Theme reset integration test. Run in an isolated Blender background process.

    blender --background --factory-startup --python-exit-code 1 --python tests/t_theme_reset.py

Also works with the existing bpy-based scripts/run_tests.py runner.
"""
from pathlib import Path
import sys

import addon_utils
import bpy


def theme_values(value):
    """Read actual theme properties, including nested widget/editor colors."""
    result = {}
    for prop in value.bl_rna.properties:
        key = prop.identifier
        if key in {'rna_type', 'filepath', 'name'}:
            continue
        item = getattr(value, key)
        if prop.type == 'POINTER':
            if item is not None:
                result[key] = theme_values(item)
        elif prop.type == 'COLLECTION':
            result[key] = [theme_values(child) for child in item]
        elif getattr(prop, 'is_array', False):
            result[key] = list(item)
        else:
            result[key] = item
    return result


def main():
    if not bpy.app.background:
        raise RuntimeError("Run this suite in a separate background Blender, not your working session")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    module = addon_utils.enable('wanderer_cad', default_set=True)
    assert module is not None
    from wanderer_cad import preferences as theme_module
    prefs = bpy.context.preferences.addons['wanderer_cad'].preferences
    prefs.snap_budget = 7.0
    prefs.enter_last = False
    before_objects = [(o.name, o.as_pointer()) for o in bpy.data.objects]
    before_keymaps = [(km.name, len(km.keymap_items)) for km in bpy.context.window_manager.keyconfigs.addon.keymaps]
    bpy.ops.preferences.reset_default_theme()
    default = theme_values(bpy.context.preferences.themes[0])
    assert {key for key, _ in theme_module.THEME_NAMES} == {
        'BLUEPRINT', 'VELLUM', 'CARBON', 'MIDNIGHT', 'GRAPHITE', 'IVORY'}
    for theme, _ in theme_module.THEME_NAMES:
        assert bpy.ops.dessin.install_theme(which=theme) == {'FINISHED'}
        assert theme_values(bpy.context.preferences.themes[0]) != default
        prefs.icon_palette = 'TARGET'
        assert bpy.ops.dessin.theme_reset() == {'FINISHED'}
        assert theme_values(bpy.context.preferences.themes[0]) == default, theme
        assert prefs.icon_palette == 'EARTH'
        assert prefs.snap_budget == 7.0 and prefs.enter_last is False
        assert [(o.name, o.as_pointer()) for o in bpy.data.objects] == before_objects
        assert [(km.name, len(km.keymap_items)) for km in bpy.context.window_manager.keyconfigs.addon.keymaps] == before_keymaps
        assert bpy.ops.dessin.theme_reset() == {'FINISHED'}
        assert theme_values(bpy.context.preferences.themes[0]) == default
        print('PASS', theme, 'full theme reset, icons, repeat reset, settings, objects and keymaps')
    # Upstream's restore-previous-theme and our factory reset must coexist.
    bpy.context.preferences.themes[0].user_interface.wcol_regular.inner = (0.125, 0.25, 0.5, 1.0)
    custom_signature = theme_module._theme_signature(bpy.context)
    assert custom_signature is not None
    assert bpy.ops.dessin.install_theme(which='BLUEPRINT') == {'FINISHED'}
    backup = Path(theme_module.theme_backup_path()).read_bytes()
    assert bpy.ops.dessin.install_theme(which='CARBON') == {'FINISHED'}
    assert Path(theme_module.theme_backup_path()).read_bytes() == backup
    assert bpy.ops.dessin.theme_reset() == {'FINISHED'}
    assert theme_values(bpy.context.preferences.themes[0]) == default
    assert Path(theme_module.theme_backup_path()).read_bytes() == backup
    assert bpy.ops.dessin.restore_theme() == {'FINISHED'}
    assert theme_module._theme_signature(bpy.context) == custom_signature
    assert bpy.ops.dessin.theme_reset() == {'FINISHED'}
    assert theme_values(bpy.context.preferences.themes[0]) == default
    print('PASS previous-theme backup survives switching themes and factory reset')
    addon_utils.disable('wanderer_cad', default_set=False)
    print('PASS theme reset suite')


if __name__ == '__main__':
    main()
