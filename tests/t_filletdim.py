import os as _os; _HERE = _os.path.dirname(_os.path.abspath(__file__)); _SRC = _os.environ.get('WANDERER_SRC') or _os.path.join(_HERE, '..', 'wanderer_cad', '__init__.py')
exec(open(_os.path.join(_HERE,'harness.py')).read())
exec(open(_os.path.join(_HERE,'prec_lib.py')).read())
# Radius dimension on fillet corners (like Rhino's DimRadius): a fillet is an arc inside a polyline, a Bézier curve or a
# mesh outline, tangent to the lines on both sides. The tool must measure the arc alone, not the whole outline.
from mathutils import Vector as _V
from mathutils import Matrix as _Mx

def arc_pts(cx,cy,r,a0,a1,step=2.5):
    """Points of an arc (degrees, a0 -> a1), the way Fillet Curve writes them (2.5 degree steps)."""
    n=max(2,int(math.ceil(abs(a1-a0)/step)))
    return [(cx+r*math.cos(math.radians(a0+(a1-a0)*i/n)), cy+r*math.sin(math.radians(a0+(a1-a0)*i/n)), 0.0) for i in range(n+1)]

def poly_obj(name,pts,closed=False):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'
    sp=cu.splines.new('POLY'); sp.points.add(len(pts)-1)
    for p_,q in zip(sp.points,pts): p_.co=(q[0],q[1],q[2],1.0)
    sp.use_cyclic_u=closed
    ob=bpy.data.objects.new(name,cu); bpy.context.scene.collection.objects.link(ob); bpy.context.view_layer.update(); return ob

def mesh_obj(name,pts):
    me=bpy.data.meshes.new(name); me.from_pydata(pts,[(i,i+1) for i in range(len(pts)-1)],[])
    ob=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(ob); bpy.context.view_layer.update(); return ob

def dims():
    return [o_ for o_ in bpy.data.objects if o_.type=='CURVE' and "dessin_cotation" in o_]

def has_point(ob,q,tol=1e-3):
    mw=ob.matrix_world
    for sp in ob.data.splines:
        for p_ in sp.points:
            if (mw@_V(p_.co[:3])-_V(q)).length<tol: return True
    return False

def check(label,arc_mid,where,r,centre):
    new,res,o=run("cotation_rayon",[C(*arc_mid),C(*where)])
    d_=dims()
    ok=len(d_)==1 and abs(float(d_[0]["dessin_cotation"])-r)<1e-3 and has_point(d_[0],centre)
    rec("Fillet",f"{label}: R{r} at centre {centre}",ok,
        [(x.name,round(float(x["dessin_cotation"]),4),has_point(x,centre)) for x in d_])

bpy.context.scene.dessin.unite_cote='SCENE'
s2=math.sqrt(0.5)

# 1. L corner, polyline with a fillet r=2 (corner (10,0), centre (8,2))
clear()
poly_obj("L",[(0,0,0)]+arc_pts(8,2,2,-90,0)+[(10,8,0)])
check("Polyline L corner",(8+2*s2,2-2*s2),(13,-3),2.0,(8,2,0))

# 2. Rounded rectangle, closed polyline 20 x 10 with r=3 corners; dimension the top-right corner
clear()
x0,y0,x1,y1,rr=-30,10,-10,20,3.0
pts=(arc_pts(x1-rr,y0+rr,rr,-90,0)+arc_pts(x1-rr,y1-rr,rr,0,90)+arc_pts(x0+rr,y1-rr,rr,90,180)+arc_pts(x0+rr,y0+rr,rr,180,270))
poly_obj("RR",pts,closed=True)
check("Rounded rectangle",(x1-rr+rr*s2,y1-rr+rr*s2),(-6,24),3.0,(x1-rr,y1-rr,0))

# 3. Bezier curve: line, quarter arc r=2 (centre (8,22)), line
clear()
k=0.5522847498*2.0
cu=bpy.data.curves.new("BZ",'CURVE'); cu.dimensions='3D'
sp=cu.splines.new('BEZIER'); sp.bezier_points.add(3)
b0,b1,b2,b3=sp.bezier_points
for bp_,co,hl,hr in ((b0,(0,20,0),(-1,20,0),(1,20,0)),(b1,(8,20,0),(7,20,0),(8+k,20,0)),
                     (b2,(10,22,0),(10,22-k,0),(10,23,0)),(b3,(10,30,0),(10,29,0),(10,31,0))):
    bp_.co=co; bp_.handle_left_type=bp_.handle_right_type='FREE'; bp_.handle_left=hl; bp_.handle_right=hr
ob=bpy.data.objects.new("BZ",cu); bpy.context.scene.collection.objects.link(ob); bpy.context.view_layer.update()
check("Bezier rounded corner",(8+2*s2,22-2*s2),(13,17),2.0,(8,22,0))

# 4. Mesh outline (edges only) with the same fillet as 1, shifted to y=-20
clear()
mesh_obj("ML",[(0,-20,0)]+arc_pts(8,-18,2,-90,0)+[(10,-12,0)])
check("Mesh edge L corner",(8+2*s2,-18-2*s2),(13,-23),2.0,(8,-18,0))

# 5. Longer polyline: first corner filleted r=1.5, second corner sharp
clear()
poly_obj("P5",[(20,-40,0)]+arc_pts(28.5,-38.5,1.5,-90,0)+[(30,-32,0),(38,-32,0)])
check("Fillet on a polyline with a sharp corner",(28.5+1.5*s2,-38.5-1.5*s2),(33,-43),1.5,(28.5,-38.5,0))

# 6. Plain sharp polyline: no circle, no dimension
clear()
poly_obj("SH",[(0,0,0),(10,0,0),(10,8,0),(18,8,0)])
new,res,o=run("cotation_rayon",[C(5,0),C(5,-4)])
rec("Fillet","Sharp polyline: no dimension",len(dims())==0,[x.name for x in dims()])

# 6b. Smooth curves that are not arcs: an ellipse and a sine wave give no radius (curvature drifts, no clean ends)
clear()
poly_obj("EL",[(6*math.cos(2*math.pi*i/96),3*math.sin(2*math.pi*i/96),0) for i in range(96)],closed=True)
new,res,o=run("cotation_rayon",[C(6*math.cos(0.5),3*math.sin(0.5)),C(9,5)])
rec("Fillet","Ellipse: no dimension",len(dims())==0,[x.name for x in dims()])
clear()
poly_obj("SN",[(-30+0.5*i,10+3*math.sin(0.25*i),0) for i in range(121)])
new,res,o=run("cotation_rayon",[C(-30+0.5*20,10+3*math.sin(5.0)),C(-20,0)])
rec("Fillet","Sine wave: no dimension",len(dims())==0,[x.name for x in dims()])

# 7. Full mesh circle still measured as before (unchanged path)
clear()
me=bpy.data.meshes.new("MC"); bm=bmesh.new(); bmesh.ops.create_circle(bm,segments=48,radius=3.0); bm.to_mesh(me); bm.free()
ob=bpy.data.objects.new("MC",me); bpy.context.scene.collection.objects.link(ob); ob.location=(12,0,0); bpy.context.view_layer.update()
check("Mesh circle (unchanged)",(15,0),(18,3),3.0,(12,0,0))
summary()
