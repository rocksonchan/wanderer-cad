import os as _os; _HERE = _os.path.dirname(_os.path.abspath(__file__)); _SRC = _os.environ.get('WANDERER_SRC') or _os.path.join(_HERE, '..', 'wanderer_cad', '__init__.py')
exec(open(_os.path.join(_HERE,'harness.py')).read())
exec(open(_os.path.join(_HERE,'prec_lib.py')).read())
# Ortho (F8) / Polar (F10) on: corner-to-corner tools (Rectangle, Plane, Ellipse by Corners, Box base) ignore them for the
# opposite corner, so a diagonal click gives the full shape. Line / Polyline stay locked to the plane axes.
# Fork feature, 2026-11-17 (branch codex/rect-ortho-diagonal).
SEC="ortho"
st_=bpy.context.scene.dessin
def info(ob):
    V=mverts(ob); mn,mx=bbox(V); v,a,nk,nm=vol_area(ob); return V,mn,mx,v,a,nk,nm
def with_modes(ortho,polar,fn):
    old=(st_.ortho,st_.polar)
    st_.polar=False; st_.ortho=ortho; st_.polar=polar
    try: return fn()
    finally: st_.polar=False; st_.ortho,st_.polar=old

for mode,(o_,p_) in (("Ortho",(True,False)),("Polar",(False,True))):
    # 1. Rectangle: (0,0) -> (8,5) gives 8 x 5, not a flat line
    clear(); new,r,o=with_modes(o_,p_,lambda: run("rectangle",[C(0,0),C(8,5)]))
    P=ctrl_pts(new[0])[0] if new else None
    mn,mx=bbox(P) if P is not None else (None,None)
    rec(SEC,f"{mode} on: Rectangle diagonal (0,0)-(8,5) = 8 x 5",P is not None and near(mn,(0,0,0),1e-9) and near(mx,(8,5,0),1e-9),
        None if P is None else tuple(np.round(mx-mn,6)))
    # 2. Plane (one face)
    clear(); new,r,o=with_modes(o_,p_,lambda: run("plan",[C(0,0),C(7,3)]))
    V=mverts(new[0]) if new else None
    mn,mx=bbox(V) if V is not None else (None,None)
    rec(SEC,f"{mode} on: Plane diagonal (0,0)-(7,3) = 7 x 3",V is not None and near(mn,(0,0,0),1e-9) and near(mx,(7,3,0),1e-9),
        None if V is None else tuple(np.round(mx-mn,6)))
    # 3. Ellipse by corners
    clear(); new,r,o=with_modes(o_,p_,lambda: run("ellipse_coin",[C(0,0),C(10,4)]))
    B=bez_eval(new[0]) if new else None
    mn,mx=bbox(B) if B is not None else (None,None)
    rec(SEC,f"{mode} on: Ellipse by corners (0,0)-(10,4) fills the box",B is not None and near(mn,(0,0,0),2e-3) and near(mx,(10,4,0),2e-3),
        None if B is None else (tuple(np.round(mn,4)),tuple(np.round(mx,4))))
    # 4. Box: base corner is free
    clear(); new,r,o=with_modes(o_,p_,lambda: run("boite",[C(0,0),C(6,4),C(6,7)]))
    if new:
        V,mn,mx,v,a,nk,nm=info(new[0])
    rec(SEC,f"{mode} on: Box base (0,0)-(6,4) = 6 x 4, closed",bool(new) and near(mn[:2],(0,0),1e-6) and near(mx[:2],(6,4),1e-6) and nk==0,
        None if not new else tuple(np.round(mx-mn,6)))

# 5. Line / Polyline still obey Ortho: (0,0) -> (8,5) ends on the X axis at (8,0)
clear(); new,r,o=with_modes(True,False,lambda: run("polyligne",[C(0,0),C(8,5),'RET']))
P=ctrl_pts(new[0])[0] if new else None
rec(SEC,"Ortho on: Polyline (0,0)->(8,5) still locks to (8,0)",P is not None and near(P[-1],(8,0,0),1e-9),
    None if P is None else tuple(np.round(P[-1],6)))
# 6. Ortho off: Rectangle unchanged
clear(); new,r,o=with_modes(False,False,lambda: run("rectangle",[C(0,0),C(8,5)]))
P=ctrl_pts(new[0])[0] if new else None
mn,mx=bbox(P) if P is not None else (None,None)
rec(SEC,"Ortho off: Rectangle (0,0)-(8,5) = 8 x 5",P is not None and near(mx-mn,(8,5,0),1e-9),None if P is None else tuple(np.round(mx-mn,6)))
summary()
