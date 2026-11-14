"""Reload this checkout in Blender without uninstalling the extension.

Run from Blender's Text Editor or through MCP. The installed extension directory
must point to this checkout's wanderer_cad directory (see docs/development.md).
Finish any active Wanderer command before reloading.
"""
from pathlib import Path
import importlib
import sys

import addon_utils
import bpy


def reload_addon():
    source = Path(__file__).resolve().parents[1] / 'wanderer_cad' / '__init__.py'
    matches = [addon.module for addon in bpy.context.preferences.addons
               if getattr(sys.modules.get(addon.module), '__file__', None)
               and Path(sys.modules[addon.module].__file__).resolve() == source]
    if len(matches) != 1:
        raise RuntimeError('Expected one enabled Wanderer linked to this checkout; see docs/development.md')
    name = matches[0]
    module = sys.modules[name]
    commands = sys.modules[name + '.views']._CMD
    if any(commands['op'].values()) or commands['input'] is not None:
        raise RuntimeError('Finish or cancel the active Wanderer command before reloading')
    addon_utils.disable(name, default_set=False)
    importlib.invalidate_caches()
    importlib.reload(module)
    loaded = addon_utils.enable(name, default_set=False)
    if loaded is None or not addon_utils.check(name)[1]:
        raise RuntimeError('Wanderer failed to reload; inspect the Blender console')
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()
    print('Reloaded', name, 'from', source)
    return name


if __name__ == '__main__':
    reload_addon()
