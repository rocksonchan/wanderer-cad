"""Real mouse-event regression in a disposable GUI Blender, never a working session.

    blender --factory-startup --enable-event-simulate --python tests/t_navigation_mouse.py

The process exits itself. Check for PASS navigation mouse suite in its output.
"""
from pathlib import Path
import sys
import traceback

import addon_utils
import bpy


def main():
    required = {'--factory-startup', '--enable-event-simulate'}
    if bpy.app.background or not required.issubset(sys.argv):
        raise RuntimeError('Use a disposable GUI Blender with --factory-startup --enable-event-simulate')
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    bpy.context.preferences.view.show_splash = False
    assert addon_utils.enable('wanderer_cad', default_set=True) is not None
    prefs = bpy.context.preferences.addons['wanderer_cad'].preferences
    bpy.context.preferences.view.smooth_view = 0
    win = bpy.context.window
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    rv = area.spaces.active.region_3d
    before_objects = [(o.name, o.as_pointer()) for o in bpy.data.objects]

    def steps():
        yield 0.7  # allow startup/keymap registration to finish
        # First prove the reported behaviour with the old setting, then the fix.
        cases = [(True, 'Top', {}, 'pan')]
        cases += [(False, name, {}, 'orbit') for name in ('Top', 'Front', 'Right', 'Bottom', 'Back', 'Left')]
        cases += [(False, 'Top', {'shift': True}, 'pan'),
                  (False, 'Top', {'ctrl': True}, 'zoom')]
        if sys.platform == 'darwin':
            cases.append((False, 'Top', {'oskey': True}, 'zoom'))
        for legacy, name, mods, expected in cases:
            prefs.view_pan = legacy
            with bpy.context.temp_override(window=win, area=area, region=region):
                bpy.ops.dessin.view_restore(name='Perspective')
                bpy.ops.dessin.view_restore(name=name)
            yield 0.15
            rot, loc, dist = rv.view_rotation.copy(), rv.view_location.copy(), rv.view_distance
            x, y = region.x + region.width // 2, region.y + region.height // 2
            win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=x, y=y)
            yield 0.1
            win.event_simulate(type='MIDDLEMOUSE', value='PRESS', x=x, y=y, **mods)
            yield 0.1
            for delta in (15, 30, 45, 60):
                win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=x + delta, y=y + delta, **mods)
                yield 0.06
            win.event_simulate(type='MIDDLEMOUSE', value='RELEASE', x=x + 60, y=y + 60, **mods)
            yield 0.15
            rotated = abs(rot.dot(rv.view_rotation)) < 0.99999
            moved = (loc - rv.view_location).length > 0.00001
            zoomed = abs(dist - rv.view_distance) > 0.00001
            if expected == 'orbit':
                assert rotated, (name, 'MMB did not orbit', moved, zoomed)
            elif expected == 'pan':
                assert moved and not rotated, (name, 'pan failed', moved, rotated)
            else:
                assert zoomed and not rotated, (name, 'zoom failed', zoomed, rotated)
            print('PASS mouse', 'legacy' if legacy else 'fixed', name, mods, expected, flush=True)
        assert [(o.name, o.as_pointer()) for o in bpy.data.objects] == before_objects
        print('PASS navigation mouse suite', flush=True)

    sequence = steps()

    def tick():
        try:
            return next(sequence)
        except StopIteration:
            bpy.ops.wm.quit_blender()
        except Exception:
            traceback.print_exc()
            print('FAIL navigation mouse suite', flush=True)
            bpy.ops.wm.quit_blender()
        return None

    bpy.app.timers.register(tick, first_interval=0.2)


if __name__ == '__main__':
    main()
