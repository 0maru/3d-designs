"""Compact upright Bambu spool case v2, build123d 0.13.0, mm.
Prototype: 35 degree cam bayonet lid, external continuous gasket, integral feet.
Run python filament_case.py. Physical fit, torque and moisture sealing untested.
"""
from pathlib import Path
from math import sin, cos, radians, atan, degrees
import json
from build123d import (Align, Box, Cylinder, Cone, Pos, Rot, Solid, Plane, Wire,
                      Compound, Color, CenterOf, export_step, export_stl)

OUT=Path(__file__).resolve().parent
P=dict(spool_diameter=200.0,spool_width=67.0,spool_bore_assumed=55.0,
       cavity_radius=101.5,wall=2.8,floor=2.4,support_height=1.6,
       body_height=74.0,rim_radius=106.5,rim_bottom=66.0,ramp_bottom=63.8,
       lid_thickness=3.6,lid_radius=111.0,skirt_inner=106.8,skirt_bottom=62.0,
       basket_radius=24.0,basket_inner_radius=22.0,basket_top=73.2,
       slot_width=1.2,slots=32,seal_radius=104.0,seal_groove_width=3.0,
       seal_groove_depth=1.3,seal_cord=2.0,lug_radius=108.3,lug_bottom=64.0,
       lug_height=2.5,lug_half_angle=4.5,lock_angle=35.0,closed_lift=0.2,
       track_outer=108.8,foot_x=35.0,foot_width=18.0,ground_y=-113.0,
       foot_depth=80.0,foot_rail_top_y=-108.8)
A=(Align.CENTER,Align.CENTER,Align.MIN)

def cyl(r,h,z=0):return Pos(0,0,z)*Cylinder(r,h,align=A)
def ring(ro,ri,h,z=0):return cyl(ro,h,z)-cyl(ri,h+2,z-1)
def sector(ro,ri,low,high,z,h):
    s=Solid.make_cylinder(ro,h,Plane.XY.offset(z),angle=high-low)
    return Rot(0,0,low)*(s-cyl(ri,h+2,z-1))

def cam_floor(phi):
    if phi<=6:return 63.0
    if phi<=25:return 63.0+(phi-6)*0.95/19
    if phi<=29:return 63.95-(phi-25)*0.15/4
    return 63.8

def track_cutter(angle):
    wires=[]
    # Ruled short segments retain the intended shallow cam and final dwell.
    for phi in [-6,-3,0,3,6,9,12,15,18,21,24,25,27,29,32,35,38,40.2]:
        a=radians(angle+phi);z=cam_floor(phi)
        points=[(r*cos(a),r*sin(a),zz) for r,zz in
                [(106.55,z),(P['track_outer'],z),(P['track_outer'],z+3.2),(106.55,z+3.2)]]
        wires.append(Wire.make_polygon(points,close=True))
    return Solid.make_loft(wires,ruled=True)

def make_parts():
    p=P;ri=p['cavity_radius'];ro=ri+p['wall'];h=p['body_height']
    print('Building compact body and integral feet',flush=True)
    body=cyl(ro,h)-cyl(ri,h+1,p['floor'])
    ramp=Pos(0,0,p['ramp_bottom'])*Cone(ro,p['rim_radius'],p['rim_bottom']-p['ramp_bottom'],align=A)
    body+=ramp-cyl(ri,h+2,-1)
    body+=ring(p['rim_radius'],ri,h-p['rim_bottom'],p['rim_bottom'])
    for x in [-p['foot_x'],p['foot_x']]:
        # Main brace is below the moving lid skirt, and outside the cavity.
        foot=Pos(x,(p['ground_y']-91)/2,0)*Box(p['foot_width'],-91-p['ground_y'],62,align=A)
        foot-=cyl(ri,64,-1)
        rail=Pos(x,(p['ground_y']+p['foot_rail_top_y'])/2,0)*Box(
            p['foot_width'],p['foot_rail_top_y']-p['ground_y'],p['foot_depth'],align=A)
        body+=foot+rail
    basket=ring(p['basket_radius'],p['basket_inner_radius'],p['basket_top']-p['floor'],p['floor'])
    cutters=[]
    for i in range(p['slots']):
        for low,high in [(3.0,33.0),(36.0,71.7)]:
            cutters.append(Rot(0,0,i*360/p['slots'])*Pos(23,0,low)*Box(6,p['slot_width'],high-low,align=A))
    body+=basket.cut(*cutters)
    for i in range(8):
        body+=Rot(0,0,i*45+22.5)*Pos(62,0,p['floor'])*Box(70,4,p['support_height'],align=A)
    body-=ring(p['seal_radius']+p['seal_groove_width']/2,p['seal_radius']-p['seal_groove_width']/2,
               p['seal_groove_depth']+1,h-p['seal_groove_depth'])
    for angle in [45,135,225,315]:
        body+=sector(p['lug_radius'],ro-0.5,angle-p['lug_half_angle'],angle+p['lug_half_angle'],p['lug_bottom'],p['lug_height'])
    print('Building bayonet lid, four cam tracks, and finger scallops',flush=True)
    lid=cyl(p['lid_radius'],p['lid_thickness'],h)
    lid+=ring(p['lid_radius'],p['skirt_inner'],h-p['skirt_bottom'],p['skirt_bottom'])
    for angle in [45,135,225,315]:
        entry=sector(p['track_outer'],106.55,angle-6,angle+6,p['skirt_bottom']-1,5.5)
        lid=lid.cut(entry,track_cutter(angle))
    for i in range(32):
        a=radians(i*360/32)
        lid-=Pos(113*cos(a),113*sin(a),0)*cyl(2.5,18,61)
    spool=ring(p['spool_diameter']/2,p['spool_bore_assumed']/2,p['spool_width'],p['floor']+p['support_height'])
    body.label='Compact body with silica basket and integral standing feet'
    lid.label='35 degree cam bayonet lid'
    body.color=Color(0.35,0.55,0.55);lid.color=Color(0.7,0.74,0.76)
    return body,lid,spool

def mesh_json(shape):
    vs,fs=shape.tessellate(0.65,0.25)
    return dict(v=[[round(v.X,3),round(v.Y,3),round(v.Z,3)] for v in vs],f=[list(t) for t in fs])

def overlap(a,b):
    inter=a.intersect(b)
    if inter is None:return 0.0
    return abs(inter.volume) if hasattr(inter,'volume') else sum(abs(s.volume) for s in inter)

def main():
    body,lid,spool=make_parts()
    closed=Pos(0,0,P['closed_lift'])*Rot(0,0,-P['lock_angle'])*lid
    report={'version':2,'parameters_mm':P,'prototype':True,'parts':{}}
    for name,part in [('body',body),('lid',lid)]:
        assert part.is_valid and len(part.solids())==1,name
        size=part.bounding_box().size
        report['parts'][name]=dict(valid=part.is_valid,solids=len(part.solids()),bounds_mm=[round(size.X,3),round(size.Y,3),round(size.Z,3)],volume_cm3=round(part.volume/1000,2))
        assert max(size.X,size.Y,size.Z)<=256
        export_step(part,OUT/f'{name}.step')
        printable=part if name=='body' else Pos(0,0,P['body_height']+P['lid_thickness'])*Rot(180,0,0)*part
        export_stl(printable,OUT/f'{name}.stl',tolerance=0.04,angular_tolerance=0.15)
    print('Checking lid/spool clearances and cam motion',flush=True)
    for name,a,b in [('body_lid',body,closed),('body_spool',body,spool),('lid_spool',closed,spool)]:
        vol=overlap(a,b);report[name+'_interference_mm3']=round(vol,6);assert vol<0.001,(name,vol)
    motion=[]
    for angle in [0,6,12,18,24,30,35]:
        # Flat lug contacts the highest point of the cam across its angular width.
        phis=[angle-P['lug_half_angle']+i*P['lug_half_angle']/10 for i in range(21)]
        lift=P['lug_bottom']-max(cam_floor(phi) for phi in phis)-0.03
        pose=Pos(0,0,lift)*Rot(0,0,-angle)*lid
        vol=overlap(body,pose);assert vol<0.01,('cam',angle,lift,vol)
        motion.append(dict(angle_deg=angle,lift_mm=round(lift,4),interference_mm3=round(vol,6)))
    for lift in [1,5,12,18]:
        assert overlap(body,Pos(0,0,lift)*lid)<0.01,('entry',lift)
    report['sampled_bayonet_motion']=motion
    # Geometric static balance, assuming homogeneous printed solids.
    # This is not a dynamic stability or strength test.
    cases={'empty_body':[(body.volume,body.center(CenterOf.MASS))],
           'empty_closed':[(body.volume,body.center(CenterOf.MASS)),(closed.volume,closed.center(CenterOf.MASS))]}
    report['static_balance']={}
    for name,pieces in cases.items():
        mass=sum(m for m,c in pieces)
        center=[sum(m*getattr(c,k) for m,c in pieces)/mass for k in ['X','Y','Z']]
        margin=min(44-abs(center[0]),center[2],80-center[2])
        assert margin>0
        report['static_balance'][name]=dict(center_cad_mm=[round(v,3) for v in center],support_margin_mm=round(margin,3))
    export_step(Compound(children=[body,closed]),OUT/'case_assembly.step')
    standing=Pos(0,40,113)*Rot(90,0,0)
    export_step(Compound(children=[standing*body,standing*closed]),OUT/'case_standing.step')
    (OUT/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    work=OUT.parents[1]/'work';work.mkdir(exist_ok=True)
    (work/'case_meshes_v2.json').write_text(json.dumps(dict(body=mesh_json(body),lid=mesh_json(lid),parameters=P),separators=(',',':')),encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':main()
