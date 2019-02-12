bl_info = {
    "name": "Aspect Ratio Calculator",
    "author": "Spencer Magnusson",
    "version": (1, 1),
    "blender": (2, 79, 0),
    "description": "Calculates and Generates Settings for Specific Aspect Ratio",
    "support": "COMMUNITY",
    "category": "Render"
}

import bpy
from statistics import median

class ARN_OT_aspect_ratio_node(bpy.types.Operator):
    bl_idname = "node.arn_ot_aspect_ratio_node"
    bl_label = "Create Aspect Ratio Node";
    bl_description = 'Creates Box Matte Node based on given aspect ratio';
    bl_options = {'REGISTER', 'UNDO'}
    
    ratio_float = bpy.props.FloatProperty(
        name = 'Custom Aspect Ratio',
        description = 'Sets the proportion of the width to the height',
        default = 2.33,
        min = 0.1,
        max = 3.0,
        precision = 2,
        step = 1
    )
    
    @classmethod
    def poll(cls, context):
        return context.area.spaces.active.tree_type == 'CompositorNodeTree'
    
    def execute(self, context):
        group_name = "Aspect Ratio"
        group_box_node_name = "Aspect Ratio Mask"
        
        context.scene.use_nodes = True
        
        scene = context.scene
        
        # Set render resolution
        if scene.ar_ratio_names == 'CS':
            self.ratio_float = scene.custom_ar_float
        elif scene.ar_ratio_names == 'SQ':
            self.ratio_float = 1
        elif scene.ar_ratio_names == 'FS':
            self.ratio_float = 4 / 3
        elif scene.ar_ratio_names == 'WS':
            self.ratio_float = 16 / 9
        elif scene.ar_ratio_names == 'WSC':
            self.ratio_float = 2.35

        # create a group
        ar_group = bpy.data.node_groups.get(group_name)
        
        if ar_group is None:
            ar_group = bpy.data.node_groups.new(type="CompositorNodeTree", name=group_name)
            # create group inputs
            ar_group.inputs.new("NodeSocketColor","Image")
            group_inputs = ar_group.nodes.new('NodeGroupInput')
            group_inputs.location = (-550,0)
            # create group outputs
            ar_group.outputs.new('NodeSocketColor','Image')
            group_outputs = ar_group.nodes.new('NodeGroupOutput')
            group_outputs.location = (600,0)
            #create box node
            box_node = ar_group.nodes.new(type='CompositorNodeBoxMask')
            box_node.name = group_box_node_name
            box_node.location = -500, 300    
            #add invert node
            invert_node = ar_group.nodes.new(type='CompositorNodeInvert')
            invert_node.location = -250, 70      
            #set up color balance node that uses mask
            color_node = ar_group.nodes.new(type='CompositorNodeColorBalance')
            color_node.correction_method = 'OFFSET_POWER_SLOPE'
            color_node.slope = (0.0, 0.0, 0.0)
            #put it all together
            ar_group.links.new(box_node.outputs[0], invert_node.inputs[1])
            ar_group.links.new(invert_node.outputs[0], color_node.inputs[0])
            ar_group.links.new(color_node.outputs[0], group_outputs.inputs['Image'])
            ar_group.links.new(invert_node.outputs[0], color_node.inputs[0])
            ar_group.links.new(group_inputs.outputs["Image"], color_node.inputs[1])
        
        #set up aspect ratio
        box_node = ar_group.nodes.get(group_box_node_name)
        scene = bpy.context.scene
        if scene.orientation == 'LS':
            if self.ratio_float < (scene.render.resolution_x / scene.render.resolution_y):
                box_node.height = scene.render.resolution_y / scene.render.resolution_x 
                box_node.width = box_node.height * self.ratio_float
            else:
                box_node.width = 1.1
                box_node.height = 1 / self.ratio_float
        elif scene.orientation == 'PT':
            if self.ratio_float > (scene.render.resolution_y / scene.render.resolution_x):
                box_node.height = scene.render.resolution_y / scene.render.resolution_x
                box_node.width = box_node.height / self.ratio_float
                box_node.height += 0.05
            else:
                box_node.width = 1.1
                box_node.height = 1 * self.ratio_float
                
        
        box_node.label = str(round(self.ratio_float, 3)) + ":1 aspect ratio"
        
        tree = bpy.context.scene.node_tree
        group_node = tree.nodes.get(group_name)
        
        if group_node is None:
            group_node = tree.nodes.new("CompositorNodeGroup")
            group_node.node_tree = ar_group
            group_node.name = group_name
        
        return {'FINISHED'}

class ARP_PT_aspect_ratio_node(bpy.types.Panel):
    bl_idname = "node.arp_pt_aspect_ratio"
    bl_space_type = 'NODE_EDITOR'
    bl_label = "Aspect Ratio Node"
    bl_category = "Aspect Ratio"
    bl_region_type = 'UI'
    
    @classmethod
    def poll(cls, context):
        return context.area.spaces.active.tree_type == 'CompositorNodeTree'
    
    def draw(self, context):
        layout = self.layout
        layout.label(text = 'Aspect Ratio Node')
        layout.prop(context.scene, "ar_ratio_names", expand=True)
        layout.prop(context.scene, "orientation", expand=True)
        if context.scene.ar_ratio_names == 'CS':
            layout.prop(context.scene, 'custom_ar_float')
        layout.operator(ARN_OT_aspect_ratio_node.bl_idname, text = 'Apply', icon = "CAMERA_DATA")
        
        
class ARRC_OT_aspect_ratio_resolution_calc(bpy.types.Operator):
    bl_idname = "render.arrc_ot_aspect_ratio_resolution_calc"
    bl_label = "Calculates Aspect Ratio Resolution";
    bl_description = 'Calculates the aspect ratio for the render';
    bl_options = {'REGISTER', 'UNDO'}
    
    ratio_float = bpy.props.FloatProperty(
        name = 'Custom Aspect Ratio',
        description = 'Sets the proportion of the width to the height',
        default = 2.33,
        min = 0.1,
        max = 3.0,
        precision = 4,
        step = 1
    )
    
    def execute(self, context):
        # Get the scene
        scene = bpy.context.scene

        # Set render resolution
        if scene.ar_ratio_names == 'CS':
            self.ratio_float = scene.custom_ar_float
        elif scene.ar_ratio_names == 'SQ':
            self.ratio_float = 1
        elif scene.ar_ratio_names == 'FS':
            self.ratio_float = 4 / 3
        elif scene.ar_ratio_names == 'WS':
            self.ratio_float = 16 / 9
        elif scene.ar_ratio_names == 'WSC':
            self.ratio_float = 2.35
        
        if scene.orientation == 'LS':
            scene.render.resolution_y = round(scene.render.resolution_x / self.ratio_float)
        elif scene.orientation == 'PT':
            scene.render.resolution_x = round(scene.render.resolution_y / self.ratio_float)
        return {'FINISHED'}

class ARRP_PT_aspect_ratio_resolution_panel(bpy.types.Panel):
    bl_idname = "render.arrp_pt_aspect_ratio_resolution_panel"
    bl_label = "Aspect Ratio Calculator"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'output'
    
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "ar_ratio_names", expand=True)
        layout.prop(context.scene, "orientation", expand=True)
        if context.scene.ar_ratio_names == 'CS':
            layout.prop(context.scene, 'custom_ar_float')
        layout.operator(ARRC_OT_aspect_ratio_resolution_calc.bl_idname, text = 'Apply', icon = "CAMERA_DATA")      



classes = (ARN_OT_aspect_ratio_node, ARP_PT_aspect_ratio_node, ARRC_OT_aspect_ratio_resolution_calc, ARRP_PT_aspect_ratio_resolution_panel)

def register():
    # To show the input in the left tool shelf, store 'bpy.props.~'.
    #   In draw() in the subclass of Panel, access the input value by 'context.scene'.
    #   In execute() in the class, access the input value by 'context.scene.float_input'.
    bpy.types.Scene.custom_ar_float = bpy.props.FloatProperty(
        name = 'Custom Aspect Ratio',
        description = 'Sets the proportion of the width to the height',
        default = 2.33,
        min = 0.1,
        max = 3.0,
        precision = 4,
        step = 1
    )
    
    bpy.types.Scene.ar_ratio_names = bpy.props.EnumProperty(
        items=[
            ('CS', 'Custom', '15', 0),
            ('SQ', '1:1', 'Square', 1),
            ('FS', '4:3', 'Fullscreen', 2),
            ('WS', '16:9', 'Widescreen', 3),
            ('WSC', '2.35', 'Widescreen Cinema', 4)
        ],
        default='WS')
        
    bpy.types.Scene.orientation = bpy.props.EnumProperty(
        items=[
            ('PT', 'Portrait', 'Portrait orientation', 0),
            ('LS', 'Landscape', 'Landscape orientation', 1)
        ],
        default='LS')
    
    for cls in classes:
        bpy.utils.register_class(cls)
    
 
def unregister():
    del bpy.types.Scene.custom_ar_float
    del bpy.types.Scene.ar_ratio_names
    del bpy.types.Scene.orientation
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
if __name__ == "__main__":
    register()
