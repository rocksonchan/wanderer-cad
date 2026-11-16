import os as _os; _HERE = _os.path.dirname(_os.path.abspath(__file__)); _SRC = _os.environ.get('WANDERER_SRC') or _os.path.join(_HERE, '..', 'wanderer_cad', '__init__.py')
exec(open(_os.path.join(_HERE,'harness.py')).read())
exec(open(_os.path.join(_HERE,'prec_lib.py')).read())
# CPlane 3 points / Vertical: the picked points use Wanderer's object snaps (End, Mid, Cen, Int...) like the drawing tools,
# not only the corners of a mesh face. The curves sit at a height (z=3..5), so a missed snap lands on the world plane (z=0).
import sys as _sys
from mathutils import Vector as _V
_core = m

def poly_obj(name,pts):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'
    sp=cu.splines.new('POLY'); sp.points.add(len(pts)-1)
    for p_,q in zip(sp.points,pts): p_.co=(q[0],q[1],q[2],1.0)
    ob=bpy.data.objects.new(name,cu); bpy.context.scene.collection.objects.link(ob); bpy.context.view_layer.update(); return ob

def frame():
    st=_core.cp_state(rv3d); return st["cur"] if st else None

def close(a,b,tol=1e-4): return a is not None and (_V(a)-_V(b)).length<tol

def setup():
    clear(); _core.cp_set(rv3d,None,record=False)
    # A=(0,0,3) -> B=(10,0,3) -> D=(10,8,5); midpoint of AB = (5,0,3)
    poly_obj("PL",[(0,0,3),(10,0,3),(10,8,5)])

st_=bpy.context.scene.dessin

# 1. 3 points on curve snaps: End A (origin), Mid AB (X axis), End D (Y side) - clicks are 3-5 px off the points
setup()
new,res,o=run("cplane",['THREE',C(0.4,0.3),C(5.3,0.2),C(10.3,8.2)])
fr=frame()
ok=fr is not None and close(fr[0],(0,0,3)) and close(fr[1],(1,0,0))
yz=None if fr is None else fr[2]
want_y=(_V((10,8,5))-_V((0,0,3))); want_y=(want_y-_V((1,0,0))*want_y.x).normalized()
rec("CPlane","3 points snap to End / Mid / End of a curve at z=3..5",ok and close(yz,want_y),
    None if fr is None else [tuple(round(c,4) for c in v) for v in fr[:3]])

# 2. Same clicks with OSnap disabled: the points stay where clicked, on the world plane (z=0)
setup()
old=st_.osnap_disable; st_.osnap_disable=True
new,res,o=run("cplane",['THREE',C(0.4,0.3),C(5.3,0.2),C(10.3,8.2)])
st_.osnap_disable=old
fr=frame()
rec("CPlane","OSnap disabled: free points on the world plane",fr is not None and close(fr[0],(0.4,0.3,0)),
    None if fr is None else tuple(round(c,4) for c in fr[0]))

# 3. Vertical plane: two snapped points (End A, End B) give a plane through z=3 standing on AB
setup()
new,res,o=run("cplane",['V',C(0.3,-0.3),C(9.7,0.3)])
fr=frame()
rec("CPlane","Vertical: snaps to the two ends of a curve",fr is not None and close(fr[0],(0,0,3)) and close(fr[1],(1,0,0)),
    None if fr is None else [tuple(round(c,4) for c in v) for v in fr[:2]])

# 4. Mesh face corners still snap (the original behaviour): plane of a raised quad, corners clicked 4 px off
clear(); _core.cp_set(rv3d,None,record=False)
me=bpy.data.meshes.new("Q"); me.from_pydata([(20,0,2),(30,0,2),(30,10,2),(20,10,2)],[],[(0,1,2,3)])
ob=bpy.data.objects.new("Q",me); bpy.context.scene.collection.objects.link(ob); bpy.context.view_layer.update()
new,res,o=run("cplane",['THREE',C(20.3,0.3),C(29.7,0.3),C(29.7,9.7)])
fr=frame()
rec("CPlane","Mesh quad corners still snap",fr is not None and close(fr[0],(20,0,2)) and close(fr[1],(1,0,0)) and close(fr[2],(0,1,0)),
    None if fr is None else [tuple(round(c,4) for c in v) for v in fr[:3]])
_core.cp_set(rv3d,None,record=False)
summary()
