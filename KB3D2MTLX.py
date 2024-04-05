# https://github.com/insanerob/kitbashToMTLX
# Searches for principled shader nodes in a path and tries to recreate them as 
# 3Delight Substance and Glass materials
# Add a primitive wrangle to alter the material paths 
# @shop_materialpath = replace(s@shop_materialpath , '/obj/KB3D_HOK/matnet' , '/obj/MTLXmatnet') ;
        
import hou

ior_default = 1.52 #Glass IOR

def get_kb3d_materials(shader_path):
    # Returns all the principled shader nodes in the path

    in_materials = []
    root = hou.node(shader_path)
    node_type = "principledshader"
    
    for child in root.allSubChildren():
        if node_type in child.type().name():
            print(child.parent().name())
            in_materials.append(child)

    print(str(len(in_materials)) + " Shaders Found") 
    
    return in_materials
    
    
def split_substance_glass(in_materials):
    # Returns the materials split by type substance or glass (has transparency_texture param)
    out_materials = []
    substance_materials = []
    glass_materials = []
    print(str(len(in_materials)) + " materials to convert")
    
    for material in in_materials:
        parent_material = material.parent().name()
        parm_transparency_tex = material.parm('transparency_texture').eval()
        if len(parm_transparency_tex) > 0:
            glass_materials.append(material)
            out_materials.append({'mat_node': material, 'type': "glass", 'parent_name': material.parent().name()})
            print("Glass: " + parent_material + " " + parm_transparency_tex)
        else:
            substance_materials.append(material)
            out_materials.append({'mat_node': material, 'type': "substance", 'parent_name': material.parent().name()})
            print("Substance: " + parent_material)
            
    print("Substance materials = " + str(len(substance_materials)))
    print("Glass materials = " + str(len(glass_materials))) 
    print("Total materials in dict list: " + str(len(out_materials)))
    
    return out_materials
        
        
def parse_kb3d_substance(material):
    # Populates the paramaters in the kb3d principled shader specific to the 3dl Substance shader
    material_dict = {}
    
    mat_node = material["mat_node"]
    material_dict["name"] = material["parent_name"]
    material_dict["base"] = mat_node.parm('basecolor_texture').eval()
    material_dict["rough"] = mat_node.parm('rough_texture').eval()
    material_dict["metallic"] = mat_node.parm('metallic_texture').eval()
    material_dict["emission"] = mat_node.parm('emitcolor_texture').eval()
    material_dict["opacity"] = mat_node.parm('opaccolor_texture').eval()
    material_dict["transparency"] = mat_node.parm('transparency_texture').eval()
    material_dict["normal"] = mat_node.parm('baseNormal_texture').eval()
    material_dict["displacement"] = mat_node.parm('dispTex_texture').eval()
    
    return material_dict
    
    
def parse_kb3d_glass(material):
    # Populates the paramaters in the kb3d principled shader specific to the 3dl Glass shader
    material_dict = {}
    
    mat_node = material["mat_node"]
    material_dict["name"] = material["parent_name"]
    material_dict["base"] = mat_node.parm('basecolor_texture').eval()
    material_dict["rough"] = mat_node.parm('rough_texture').eval()
    material_dict["metallic"] = mat_node.parm('metallic_texture').eval()
    material_dict["refract"] = mat_node.parm('transparency_texture').eval()
    material_dict["normal"] = mat_node.parm('baseNormal_texture').eval()
    material_dict["displacement"] = mat_node.parm('dispTex_texture').eval()
    
    return material_dict
    
    
def create_matnet(matnet_name):
# Check if the Material Network already exists
    matnet_path = "/obj/" + matnet_name
    if not hou.node(matnet_path):
        # If it doesn't exist, create it
        obj = hou.node("/obj")
        matnet = obj.createNode("matnet", matnet_name)
        matnet.cook()
        print("matnet created " + matnet_name)


def create_substance(texture_dict, matnet_name):
    # creates the 3dl material network with a substance shader
    matnet = hou.node(matnet_name)
    
    # create Collect node 
    collect = matnet.createNode("collect", texture_dict['name'])
    
    # create MTLX standard surface node
    standard = matnet.createNode("mtlxstandard_surface", "mtlx_standard_" + texture_dict['name'])
    collect.setInput(0, standard, 0)

    # create mtxl base texture
    if (texture_dict["base"] != ""):
        base_texture = matnet.createNode("mtlximage", "base_" + texture_dict['name'])
        base_texture_parm = base_texture.parm("file")
        base_texture_parm.set(texture_dict["base"])
        #base_texture_parm1 = base_texture.parm("signature")
        #base_texture_parm1.set("Color")
        base_texture_parm2 = base_texture.parm("filecolorspace")
        base_texture_parm2.set("srgb_texture")
        standard.setInput(1, base_texture, 0)
    
    
    
    # create mtlx rough texture
    if (texture_dict["rough"] != ""):
        rough_texture = matnet.createNode("mtlximage", "rough_" + texture_dict['name'])
        rough_texture_parm = rough_texture.parm("file")
        rough_texture_parm.set(texture_dict["rough"])
        rough_texture_parm1 = rough_texture.parm("signature")
        rough_texture_parm1.set("float")
        rough_texture_parm2 = rough_texture.parm("filecolorspace")
        rough_texture_parm2.set("lin_rec709")
        standard.setInput(6, rough_texture, 0)

    # create mtlx metallic texture
    if (texture_dict["metallic"] != ""):
        metallic_texture = matnet.createNode("mtlximage", "metallic_" + texture_dict['name'])
        metallic_texture_parm =  metallic_texture.parm("file")
        metallic_texture_parm.set(texture_dict["metallic"])
        metallic_texture_parm1 = metallic_texture.parm("signature")
        metallic_texture_parm1.set("float")
        metallic_texture_parm2 = metallic_texture.parm("filecolorspace")
        metallic_texture_parm2.set("lin_rec709")
        standard.setInput(3, metallic_texture, 0)
        
    # create mtlx emission texture
    if (texture_dict["emission"] != ""):
        emission_texture = matnet.createNode("mtlximage", "emission_" + texture_dict['name'])
        emission_texture_parm =  emission_texture.parm("file")
        emission_texture_parm.set(texture_dict["emission"])
        #emission_texture_parm1 = emission_texture.parm("signature")
        #emission_texture_parm1.set("Color")
        emission_texture_parm2 = emission_texture.parm("filecolorspace")
        emission_texture_parm2.set("lin_rec709")
        standard_parm_emission = standard.parm("emission")
        standard_parm_emission.set(emission_value)
        standard_parm_specular = standard.parm("specular")
        standard_parm_specular.set(specular_value)
        standard.setInput(37, emission_texture, 0)

    # create mtlx opactiy texture
    if (texture_dict["opacity"] != ""):
        opacity_texture = matnet.createNode("mtlximage", "opacity_" + texture_dict['name'])
        opacity_texture_parm =  opacity_texture.parm("file")
        opacity_texture_parm.set(texture_dict["opacity"])
        #opacity_texture_parm1 = opacity_texture.parm("signature")
        #opacity_texture_parm1.set("float")
        opacity_texture_parm2 = opacity_texture.parm("filecolorspace")
        opacity_texture_parm2.set("lin_rec709")
        standard.setInput(38, opacity_texture, 0)

    # create mtlx transparency texture
    if (texture_dict["transparency"] != ""):
        transparency_texture = matnet.createNode("mtlximage", "transparency_" + texture_dict['name'])
        transparency_texture_parm =  transparency_texture.parm("file")
        transparency_texture_parm.set(texture_dict["transparency"])
        transparency_texture_parm1 = transparency_texture.parm("signature")
        transparency_texture_parm1.set("float")
        transparency_texture_parm2 = transparency_texture.parm("filecolorspace")
        transparency_texture_parm2.set("lin_rec709")
        standard.setInput(10, transparency_texture, 0)

    # create mtlx normal texture
    if (texture_dict["normal"] != ""):
        mtlx_normal_map = matnet.createNode("mtlxnormalmap", "normalmap_" + texture_dict['name'])
    
        normal_texture = matnet.createNode("mtlximage", "normal_" + texture_dict['name'])
        normal_texture_parm =  normal_texture.parm("file")
        normal_texture_parm.set(texture_dict["normal"])
        #normal_texture_parm1 = normal_texture.parm("signature")
        #normal_texture_parm1.set("color")
        normal_texture_parm2 = normal_texture.parm("filecolorspace")
        normal_texture_parm2.set(norm_map_color_space)
        mtlx_normal_map.setInput(0, normal_texture, 0)
        standard.setInput(40, mtlx_normal_map, 0)
        
    # create mtlx displacement texture
    if (texture_dict["displacement"] != ""):
        mtlx_disp_remap = matnet.createNode("mtlxremap", "disp_remap_" + texture_dict['name'])
        remap_parm = mtlx_disp_remap.parm("signature") 
        remap_parm.set("1")
        remap_parm1 = mtlx_disp_remap.parm("inlow") 
        remap_parm1.set("0.0")
        remap_parm2 = mtlx_disp_remap.parm("inhigh") 
        remap_parm2.set("1.0")
        remap_parm3 = mtlx_disp_remap.parm("outlow") 
        remap_parm3.set("-0.5")
        remap_parm4 = mtlx_disp_remap.parm("outhigh") 
        remap_parm4.set("0.5")
        
        displacement_texture = matnet.createNode("mtlximage", "displacement_" + texture_dict['name'])
        displacement_texture_parm =  displacement_texture.parm("file")
        displacement_texture_parm.set(texture_dict["displacement"])
        #displacement_texture_parm1 = displacement_texture.parm("signature")
        #displacement_texture_parm1.set("color")
        displacement_texture_parm2 = displacement_texture.parm("filecolorspace")
        displacement_texture_parm2.set("lin_rec709")
        
        # create mtlx displacement node
        mtlx_disp = matnet.createNode("mtlxdisplacement", "disp_map_" + texture_dict['name'])
        disp_parm = mtlx_disp.parm("scale") 
        disp_parm.set("0.02")
        
        # connect displacement texture to remap
        mtlx_disp_remap.setInput(0, displacement_texture, 0)
        
        # connect remap to mtlx_disp
        mtlx_disp.setInput(0, mtlx_disp_remap, 0)
        
        # connect mtlx_disp to collect
        collect.setInput(1, mtlx_disp, 0)
    
    # Tidy up node layout
    matnet.layoutChildren()
    
    
def create_glass(texture_dict, matnet_name):
    print("no separate glass shader needed")
    
def process_substance(material, matnet_name):
    # handles converting substance materials
    print("Substance processing: " + material["parent_name"] + " " + material["type"])
    texture_dict = parse_kb3d_substance(material)
    create_substance(texture_dict, matnet_name)
    
    
def process_glass(material, matnet_name):
    # handles converting glass materials
    print("Glass processing: " + material["parent_name"] + " " + material["type"])
    texture_dict = parse_kb3d_glass(material)
    create_glass(texture_dict, matnet_name)
        
        
def process_materials(materials_list, matnet_name):
    # takes each material and calls is processor by type
    
    # create material network if it doesn't exist
    create_matnet(matnet_name)
    matnet_name = "/obj/" + matnet_name
    # itterate through materials
    for material in materials_list:
        #if material["type"] == "substance":
        #    process_substance(material, matnet_name)
        #if material["type"] == "glass":
        #    process_glass(material, matnet_name)
        process_substance(material, matnet_name)

def main():
    input_material_path = hou.selectedNodes()[0].path()
    matnet_name="MTLXmatnet"
    in_materials = get_kb3d_materials(input_material_path)
    materials_list = split_substance_glass(in_materials)
    process_materials(materials_list, matnet_name)
    print("Finished Processing")

specular_value = float(hou.ui.readInput("Enter a default specular value (default is 0.00 i.e. dielectric):", buttons=("OK", "Cancel"), initial_contents="0.004")[1])
emission_value = float(hou.ui.readInput("Enter a default emission value:", buttons=("OK", "Cancel"), initial_contents="2.0")[1])
norm_map_color_space = hou.ui.readInput("Normal map colour space (ACEScg, lin_rec709, srgb_tx, Raw):", buttons=("OK", "Cancel"), initial_contents="")[1]
main()

