"""Navigation regression checks in an isolated background Blender process.

    blender --background --factory-startup --python-exit-code 1 --python tests/t_navigation.py
"""
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import Mock, patch

import addon_utils
import bpy


def main():
    if not bpy.app.background:
        raise RuntimeError('Run in a separate background Blender, not your working session')
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    assert addon_utils.enable('wanderer_cad', default_set=True) is not None
    from wanderer_cad import navigation as nav
    from wanderer_cad.core import PREF_DEFAULTS

    prefs = bpy.context.preferences.addons['wanderer_cad'].preferences
    assert prefs.nav_style == 'BLENDER'
    assert prefs.view_pan is False, 'Default Blender style must not replace orbit with pan'
    assert PREF_DEFAULTS['view_pan'] is False
    before_objects = [(o.name, o.as_pointer()) for o in bpy.data.objects]
    area = next(a for a in bpy.context.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    bpy.context.preferences.view.smooth_view = 0

    def bindings():
        return [(km.name, kmi.idname, kmi.type, kmi.shift, kmi.ctrl, kmi.alt)
                for km, kmi in nav._VIEW_KEYMAPS]

    assert not nav._VIEW_KEYMAPS, 'Standard navigation should fall through to Blender'
    with bpy.context.temp_override(area=area, region=region):
        for name in ('Top', 'Front', 'Right', 'Bottom', 'Back', 'Left'):
            assert bpy.ops.dessin.view_restore(name='Perspective') == {'FINISHED'}
            assert not nav.in_side_view(bpy.context)
            assert bpy.ops.dessin.view_restore(name=name) == {'FINISHED'}
            assert nav.in_side_view(bpy.context), name
            assert not bpy.context.region_data.lock_rotation
            assert nav.start_navigation(bpy.context) is False, name
            assert not nav._VIEW_KEYMAPS
            print('PASS Perspective ->', name, ': native navigation remains available')

        # Reproduce the old opt-in path without starting a modal mouse operator
        # in background mode. Verify the actual routing against a real Top view.
        bpy.ops.dessin.view_restore(name='Top')
        prefs.view_pan = True
        assert any(item[1:3] == ('dessin.orbit_pan', 'MIDDLEMOUSE') for item in bindings())
        move, rotate = Mock(), Mock()
        fake_bpy = SimpleNamespace(ops=SimpleNamespace(view3d=SimpleNamespace(move=move, rotate=rotate)))
        with patch.object(nav, 'bpy', fake_bpy):
            assert nav.start_navigation(bpy.context) is True
        move.assert_called_once_with('INVOKE_DEFAULT')
        rotate.assert_not_called()

        # An existing installation may have saved the old True value.
        # Re-selecting Blender must repair it, not merely change the default.
        prefs.nav_style = 'BLENDER'
        assert prefs.view_pan is False
        assert not nav._VIEW_KEYMAPS
        assert nav.start_navigation(bpy.context) is False
        print('PASS legacy pan override -> select Blender -> native orbit restored')

        for _ in range(3):
            prefs.nav_style = 'RHINO'
            assert prefs.view_pan is True
            assert prefs.mouse_orbit == 'RIGHT'
            assert any(item[1:3] == ('dessin.orbit_pan', 'RIGHTMOUSE') for item in bindings())
            assert len(bindings()) == len(set(bindings())), 'Duplicate navigation bindings'
            prefs.nav_style = 'BLENDER'
            assert prefs.view_pan is False
            assert prefs.mouse_orbit == prefs.mouse_menu == 'DEFAULT'
            assert not nav._VIEW_KEYMAPS, 'Stale navigation overrides after style change'
        print('PASS repeated Rhino / Blender switching without stale bindings')

        prefs.view_pan = True
        prefs.nav_style = 'CUSTOM'
        assert prefs.view_pan is True, 'Custom style must preserve explicit choices'
        prefs.nav_style = 'BLENDER'
        assert not nav._VIEW_KEYMAPS
    assert [(o.name, o.as_pointer()) for o in bpy.data.objects] == before_objects
    addon_utils.disable('wanderer_cad', default_set=False)
    print('PASS navigation suite; scene objects preserved')


if __name__ == '__main__':
    main()
