import bpy
import numpy as np
import colorsys

# --- 0. LIVE UPDATE CALLBACK ---
def trigger_generation(self, context):
    if self.auto_update:
        bpy.ops.object.generate_polynomial()

# --- 1. PROPERTY GROUP ---
class PolyGenProperties(bpy.types.PropertyGroup):
    auto_update: bpy.props.BoolProperty(
        name="Live Auto-Update (Don't Drag!)", 
        default=False,
        description="Updates automatically on change. WARNING: Dragging sliders will freeze Blender!"
    )
    
    formula_type: bpy.props.EnumProperty(
        name="Pattern",
        items=[
            ('NEW_F1', "Degree 9 (Image 1)", ""),
            ('NEW_F2', "Degree 10 (Image 2)", ""),
            ('S2_R1_1', "Tri-Hole Mask (R1-C1)", ""), ('S2_R1_2', "Nested Shells (R1-C2)", ""), ('S2_R1_3', "Triple Vortex (R1-C3)", ""),
            ('S2_R2_1', "Lungs (R2-C1)", ""), ('S2_R2_2', "The Bridge (R2-C2)", ""), ('S2_R2_3', "Triple Core (R2-C3)", ""),
            ('S2_R3_1', "Double Shield (R3-C1)", ""), ('S2_R3_2', "Delta Void (R3-C2)", ""), ('S2_R3_3', "Swirling Clover (R3-C3)", ""),
            ('F4', "Orbital Ring (Formula 4)", ""), ('F1', "Original 5-Fold", "")
        ],
        default='NEW_F1', update=trigger_generation)
    
    spline_type: bpy.props.EnumProperty(name="Spline Type", items=[('POLY', "Poly", ""), ('NURBS', "NURBS", ""), ('BEZIER', "Bezier", "")], default='NURBS', update=trigger_generation)
    n_roots: bpy.props.IntProperty(name="Degree", default=9, min=2, max=32, update=trigger_generation)
    steps_t1: bpy.props.IntProperty(name="Points (t1)", default=400, update=trigger_generation)
    steps_t2: bpy.props.IntProperty(name="Layers (t2)", default=80, update=trigger_generation)
    z_spread: bpy.props.FloatProperty(name="Z-Spread", default=0.005, update=trigger_generation)
    thickness: bpy.props.FloatProperty(name="Thickness", default=0.002, update=trigger_generation)
    smoothness: bpy.props.IntProperty(name="Smoothness", default=12, update=trigger_generation)
    jump_limit: bpy.props.FloatProperty(name="Max Jump", default=1.5, update=trigger_generation)
    use_stabilizer: bpy.props.BoolProperty(name="Dual-Zone Stabilizer", default=True, update=trigger_generation)
    stabilizer_threshold: bpy.props.FloatProperty(name="Inner Zone", default=1.5, update=trigger_generation)
    inner_strictness: bpy.props.FloatProperty(name="Strictness", default=0.2, update=trigger_generation)
    use_cyclic: bpy.props.BoolProperty(name="Close Loops", default=True, update=trigger_generation)

    c8_real: bpy.props.FloatProperty(name="C8 Real", default=-81.7, update=trigger_generation)
    c8_imag: bpy.props.FloatProperty(name="C8 Imag", default=16.9, update=trigger_generation)
    c5_real: bpy.props.FloatProperty(name="C5 Real", default=47.3, update=trigger_generation)
    c5_imag: bpy.props.FloatProperty(name="C5 Imag", default=74.4, update=trigger_generation)

# --- 2. MATERIAL HELPER ---
def ensure_rainbow_materials(obj, n):
    obj.data.materials.clear()
    for i in range(n):
        mat_name = f"PolyRainbow_{i}"
        mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes; nodes.clear()
        out = nodes.new(type='ShaderNodeOutputMaterial')
        em = nodes.new(type='ShaderNodeEmission')
        rgb = colorsys.hsv_to_rgb(i/n, 0.8, 1.0) 
        em.inputs[0].default_value = (*rgb, 1.0)
        em.inputs[1].default_value = 5.0 
        mat.node_tree.links.new(em.outputs[0], out.inputs[0])
        obj.data.materials.append(mat)

# --- 3. GENERATOR ---
class OBJECT_OT_GeneratePolynomial(bpy.types.Operator):
    bl_idname = "object.generate_polynomial"
    bl_label = "Manual Generate"

    def execute(self, context):
        props = context.scene.poly_gen_props
        nv = props.n_roots
        obj_name = "Poly_Generator_Live"
        curve_obj = bpy.data.objects.get(obj_name) or bpy.data.objects.new(obj_name, bpy.data.curves.new(obj_name, 'CURVE'))
        if curve_obj.name not in context.collection.objects: context.collection.objects.link(curve_obj)
        curve_obj.data.dimensions = '3D'; curve_obj.data.bevel_depth = props.thickness; curve_obj.data.splines.clear()
        
        ensure_rainbow_materials(curve_obj, nv)
        theta1 = np.linspace(0, 2*np.pi, props.steps_t1); theta2 = np.linspace(0, 2*np.pi, props.steps_t2)

        for l_idx, t2_v in enumerate(theta2):
            z_val = l_idx * props.z_spread
            
            def get_coeffs(t1_val, t2_val, p):
                # Standard unit circle mapping (default for most formulas)
                t1 = np.exp(1j * t1_val) 
                t2 = np.exp(1j * t2_val)
                c = [0j] * (nv + 1)
                
                c8_custom = p.c8_real + 1j * p.c8_imag
                c5_custom = p.c5_real + 1j * p.c5_imag

                # --- NEW FORMULAS ---
                if p.formula_type == 'NEW_F1': # Requires Degree = 9
                    c[0] = 1.0
                    c[nv-5 if nv>=5 else 0] = -50j*(t2**3) - 50*(t2**2) + 50*t2 - 50
                    c[nv-1 if nv>=1 else 0] = 50j*(t1**3) + 50*(t1**2) + 50j*t1 + 50
                
                elif p.formula_type == 'NEW_F2': # Requires Degree = 10
                    # OPTION A: The Hardcoded Way (Uncomment to use, but will draw straight lines!)
                    # t1 = -4.0
                    # t2 = 4.0
                    
                    # OPTION B: The Sweep Way (Maps the 0-to-2pi loop into a -5 to +5 linear range)
                    t1 = (t1_val / (2 * np.pi)) * 10.0 - 5.0
                    t2 = (t2_val / (2 * np.pi)) * 10.0 - 5.0
                    
                    c[0] = 16.0
                    c[1 if nv>=1 else 0] = -100j*t2 - 100j
                    c[2 if nv>=2 else 0] = 6.4
                    c[3 if nv>=3 else 0] = 6.72
                    c[4 if nv>=4 else 0] = -20.47
                    c[5 if nv>=5 else 0] = 10.43
                    c[6 if nv>=6 else 0] = -1.16
                    c[7 if nv>=7 else 0] = -100*(t1**9) + 100*(t1**8) - 100*(t1**7) + 100*(t1**6) - 100j*(t1**5) - 100*(t1**4) - 100*(t1**3) + 100*(t1**2) + 100*t1 + 100
                    c[8 if nv>=8 else 0] = 2.352
                    c[9 if nv>=9 else 0] = -0.3641

                # --- OLD FORMULAS ---
                elif p.formula_type == 'S2_R1_1': c[0]=4.0; c[nv-2]=t1**2+t2; c[nv]=t1
                elif p.formula_type == 'S2_R1_2': c[0]=4.0; c[nv-2]=t1**2+t2; c[nv-1]=t1; c[nv]=t2**2
                elif p.formula_type == 'S2_R1_3': c[0]=4.0; c[nv-2]=t1**2-t2; c[nv-1]=t2**2; c[nv]=1.0
                elif p.formula_type == 'S2_R2_1': c[0]=1.0; c[1]=(t2**2+t1-1j); c[2]=(-t2**3-t1**2+1j*t2-1.0)
                elif p.formula_type == 'S2_R2_2': c[0]=4.0; c[1]=(-t1**2-1j*t1-1j); c[nv-1]=-3.0; c[nv]=-t2**2-1j*t2
                elif p.formula_type == 'S2_R2_3': c[0]=4.0; c[nv-1]=-(-1j*t2**2+t2-1j); c[nv]=1j*t2**2-1j*t1-1.0
                elif p.formula_type == 'S2_R3_1': c[0]=4.0; c[1]=(-t1**2+t1+1j); c[2]=(-1j*t2**2-t2**2-1.0)
                elif p.formula_type == 'S2_R3_2': c[0]=4.0; c[nv-2]=(t2**2-1j*t2-t2); c[nv-1]=-3.0; c[nv]=t1**2-1j*t1-1.0
                elif p.formula_type == 'S2_R3_3': c[0]=4.0; c[nv-2]=(t1**2+t1); c[nv-1]=-3.0; c[nv]=1j*t2**2-1j*t2-1j
                elif p.formula_type == 'F4':
                    c[nv-6 if nv>=6 else 0] = t1 * (c8_custom) + (35.6 + 79.7j)
                    c[nv] = t2 * (87.8 + 115j) + (7.94 + 122j)
                elif p.formula_type == 'F1':
                    c[0] = t2**2 * (c8_custom) + t2*(40-69.6j) + (60.5+7.09j)
                    c[3 if nv>=3 else 0] = t1**2 * (c5_custom) + t1*(-24+44.4j) + (-5.78+8.66j)
                
                if c[0] == 0j: c[0] = 1.0
                return c

            prev_roots = sorted(np.roots(get_coeffs(theta1[0], t2_v, props)), key=np.angle)
            threads = [[] for _ in range(len(prev_roots))]
            for t1_v in theta1:
                raw = list(np.roots(get_coeffs(t1_v, t2_v, props)))
                matched = []
                for pr in prev_roots:
                    if not raw: break
                    best = min(raw, key=lambda x: abs(x - pr))
                    dyn_limit = props.jump_limit
                    if props.use_stabilizer and abs(pr) < props.stabilizer_threshold: dyn_limit *= props.inner_strictness
                    if abs(best - pr) > dyn_limit: matched.append(pr)
                    else: matched.append(best); raw.remove(best)
                for i, r in enumerate(matched):
                    if i < len(threads): threads[i].append((r.real, r.imag, z_val))
                prev_roots = matched

            for i, pts in enumerate(threads):
                if len(pts) < 2: continue
                s = curve_obj.data.splines.new(type=props.spline_type)
                if props.spline_type == 'BEZIER':
                    s.bezier_points.add(len(pts)-1)
                    for p_idx, p in enumerate(pts):
                        s.bezier_points[p_idx].co = p
                        s.bezier_points[p_idx].handle_left_type = 'AUTO'; s.bezier_points[p_idx].handle_right_type = 'AUTO'
                else:
                    s.points.add(len(pts)-1)
                    for p_idx, p in enumerate(pts): s.points[p_idx].co = (p[0], p[1], p[2], 1.0)
                if props.spline_type != 'POLY':
                    s.resolution_u = props.smoothness
                    if props.spline_type == 'NURBS': s.use_endpoint_u = True
                s.use_cyclic_u = props.use_cyclic; s.material_index = i % nv
        return {'FINISHED'}

# --- 4. UI ---
class VIEW3D_PT_PolynomialPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'; bl_region_type = 'UI'; bl_category = 'Polynomial Art'; bl_label = "Poly Studio V6.0 Custom"
    def draw(self, context):
        props = context.scene.poly_gen_props; layout = self.layout
        
        layout.prop(props, "auto_update", icon='PLAY' if props.auto_update else 'PAUSE')
        layout.separator()
        
        layout.prop(props, "formula_type", text="")
        box = layout.box(); box.prop(props, "spline_type"); box.prop(props, "use_stabilizer")
        if props.use_stabilizer: box.prop(props, "stabilizer_threshold", text="Zone"); box.prop(props, "inner_strictness", text="Strict")
        
        col = layout.column(align=True); col.prop(props, "n_roots", text="Degree"); col.prop(props, "steps_t1"); col.prop(props, "steps_t2")
        row = layout.row(align=True); row.prop(props, "z_spread"); row.prop(props, "thickness")
        layout.prop(props, "jump_limit")
        
        layout.label(text="Coefficients (F1/F4):")
        row = layout.row(align=True); row.prop(props, "c8_real", text="C8 R"); row.prop(props, "c8_imag", text="C8 I")
        row = layout.row(align=True); row.prop(props, "c5_real", text="C5 R"); row.prop(props, "c5_imag", text="C5 I")
        
        if not props.auto_update:
            layout.operator("object.generate_polynomial", icon='FILE_REFRESH')

def register():
    bpy.utils.register_class(PolyGenProperties); bpy.utils.register_class(OBJECT_OT_GeneratePolynomial); bpy.utils.register_class(VIEW3D_PT_PolynomialPanel)
    bpy.types.Scene.poly_gen_props = bpy.props.PointerProperty(type=PolyGenProperties)
if __name__ == "__main__": register()