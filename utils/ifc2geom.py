import os
import ifcopenshell
import ifcopenshell.geom
import trimesh
import numpy as np


def geometry_to_mesh(element:ifcopenshell.entity_instance):
    
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    guid = element.GlobalId
    mesh = None
    try:
        shape = ifcopenshell.geom.create_shape(settings, element)
        faces = shape.geometry.faces
        verts = shape.geometry.verts

        grouped_verts = [[verts[i], verts[i + 1], verts[i + 2]] for i in range(0, len(verts), 3)]
        grouped_faces = [[faces[i], faces[i + 1], faces[i + 2]] for i in range(0, len(faces), 3)]

        mesh = trimesh.Trimesh(vertices=grouped_verts, faces=grouped_faces)
    except:
        print(f"Error in generating geometry for {guid}")
    return mesh

    
def export_exact_geometry(guid:str, model:ifcopenshell.file, element:ifcopenshell.entity_instance, geom_dir:str=os. getcwd(), check_aggregate=False) -> str:
    
    if not os.path.exists(geom_dir):
        os.makedirs(geom_dir)
        print(f"New directory created ./{geom_dir}/")
        
    if not os.path.isfile(os.path.join(geom_dir, guid + '.ply')):
        if hasattr(element, 'Representation') and element.Representation is not None:
            mesh = geometry_to_mesh(element)
            if mesh is not None:
                mesh.export(geom_dir + '/' + guid + '.ply')
                print(f"Geometry exported for {guid}")
                return geom_dir + '/' + guid + '.ply'
        elif check_aggregate: 
            # test whether the element is an aggregated element. 
            # If yes, build geometery from its aggregating elements.
            mesh = trimesh.base.Trimesh()
            agg_mesh_list = []
            
            for inv_rel in model.get_inverse(element):
                if inv_rel.is_a() == 'IfcRelAggregates' and inv_rel.RelatingObject == element:
                    print(f"Aggregating geometries for {guid}...")
                    for agg_element in inv_rel.RelatedObjects:
                        agg_mesh = geometry_to_mesh(agg_element)
                        if agg_mesh is not None:
                            agg_mesh_list.append(agg_mesh)
                        mesh = trimesh.boolean.union(agg_mesh_list, engine='blender')
                else:
                    continue
            mesh.export(geom_dir + '/' + guid + '.ply')
            print(f"Geometry exported for {guid}")
            return geom_dir + '/' + guid + '.ply'
        else:
            print(f"No geometry found for {guid}, skipping")

    else:
        print(f"Geometry exist for {guid}")
        return geom_dir + '/' + guid + '.ply'

    
def bbox_to_string(guid:str, geom_dir:str) -> str:
    try:
        element_mesh = trimesh.load_mesh(geom_dir + '/' + guid + '.ply')
        element_bbox = element_mesh.bounding_box
        bbox_dimension = np.round(element_bbox.extents * 1000, 0)
        bbox_base = np.round(element_bbox.vertices.min(0) * 1000, 0)
        output_string = ""
        for num in np.concatenate((bbox_base, bbox_dimension)):
            output_string += str(num) + ', '

        return output_string[:-2]
    except:
        print(f"Geometry file not found when creating bounding box for {guid}")
    
    
def topology_rel(subj:str, obj:str, delta=1e-3) -> (dict, dict):
    bbox1, bbox2 = list(map(float, subj.split(', '))), list(map(float, obj.split(', ')))
    bbox1_base, bbox1_dimension = bbox1[:3], bbox1[3:]
    bbox2_base, bbox2_dimension = bbox2[:3], bbox2[3:]
    topo_res = {}
    topo_offset = {}
    
    for idx, (p1, l1, p2, l2) in enumerate(zip(bbox1_base, bbox1_dimension, bbox2_base, bbox2_dimension)):
        if idx == 0: # in x-axis
            if p1 < p2:
                if p1+l1 < p2:
                    topo_res['x'] = 'RIGHT'
                    topo_offset['x'] = p2-p1-l1
                elif p1+l1 == p2:
                    topo_res['x'] = 'RIGHT_CONTACT'
                    topo_offset['x'] = 0
                else: # p1+l1 > p2
                    if p1+l1 < p2+l2:
                        topo_res['x'] = 'RIGHT_OVERLAP'
                    else:
                        topo_res['x'] = 'CONTAINED_IN'
                    topo_offset['x'] = 0
            elif p1 == p2:
                if p1+l1 < p2+l2:
                    topo_res['x'] = 'CONTAIN'
                elif p1+l1 == p2+l2:
                    topo_res['x'] = 'EXACT_OVERLAP'
                else: # p1+l1 > p2+l2
                    topo_res['x'] = 'CONTAINED_IN'
                topo_offset['x'] = 0
            else: # p1 > p2
                if p1 < p2+l2:
                    if p1+l1 <= p2+l2:
                        topo_res['x'] = 'CONTAIN'
                    else: # p1+l1 > p2+l2
                        topo_res['x'] = 'LEFT_OVERLAP'
                    topo_offset['x'] = 0
                elif p1 == p2+l2:
                    topo_res['x'] = 'LEFT_CONTACT'
                    topo_offset['x'] = 0
                else: # p1 > p2+l2
                    topo_res['x'] = 'LEFT'
                    topo_offset['x'] = p2+l2-p1
            
        elif idx == 1: # in y-axis
            if p1 < p2:
                if p1+l1 < p2:
                    topo_res['y'] = 'FRONT'
                    topo_offset['y'] = p2-p1-l1
                elif p1+l1 == p2:
                    topo_res['y'] = 'FRONT_CONTACT'
                    topo_offset['y'] = 0
                else: # p1+l1 > p2
                    if p1+l1 < p2+l2:
                        topo_res['y'] = 'FRONT_OVERLAP'
                    else:
                        topo_res['y'] = 'CONTAINED_IN'
                    topo_offset['y'] = 0
            elif p1 == p2:
                if p1+l1 < p2+l2:
                    topo_res['y'] = 'CONTAIN'
                elif p1+l1 == p2+l2:
                    topo_res['y'] = 'EXACT_OVERLAP'
                else: # p1+l1 > p2+l2
                    topo_res['y'] = 'CONTAINED_IN'
                topo_offset['y'] = 0
            else: # p1 > p2
                if p1 < p2+l2:
                    if p1+l1 <= p2+l2:
                        topo_res['y'] = 'CONTAIN'
                    else: # p1+l1 > p2+l2
                        topo_res['y'] = 'BACK_OVERLAP'
                    topo_offset['y'] = 0
                elif p1 == p2+l2:
                    topo_res['y'] = 'BACK_CONTACT'
                    topo_offset['y'] = 0
                else: # p1 > p2+l2
                    topo_res['y'] = 'BACK'
                    topo_offset['y'] = p2+l2-p1
                    
        else: # idx == 2, in z-axis
            if p1 < p2:
                if p1+l1 < p2:
                    topo_res['z'] = 'ABOVE'
                    topo_offset['z'] = p2-p1-l1
                elif p1+l1 == p2:
                    topo_res['z'] = 'ABOVE_CONTACT'
                    topo_offset['z'] = 0
                else: # p1+l1 > p2
                    if p1+l1 < p2+l2:
                        topo_res['z'] = 'ABOVE_OVERLAP'
                    else:
                        topo_res['z'] = 'CONTAINED_IN'
                    topo_offset['z'] = 0
            elif p1 == p2:
                if p1+l1 < p2+l2:
                    topo_res['z'] = 'CONTAIN'
                elif p1+l1 == p2+l2:
                    topo_res['z'] = 'EXACT_OVERLAP'
                else: # p1+l1 > p2+l2
                    topo_res['z'] = 'CONTAINED_IN'
                topo_offset['z'] = 0
            else: # p1 > p2
                if p1 < p2+l2:
                    if p1+l1 <= p2+l2:
                        topo_res['z'] = 'CONTAIN'
                    else: # p1+l1 > p2+l2
                        topo_res['z'] = 'BELOW_OVERLAP'
                    topo_offset['z'] = 0
                elif p1 == p2+l2:
                    topo_res['z'] = 'BELOW_CONTACT'
                    topo_offset['z'] = 0
                else: # p1 > p2+l2
                    topo_res['z'] = 'BELOW'
                    topo_offset['z'] = p2+l2-p1
            
    
    return topo_res, topo_offset


def test_for_contact(subj_path:str, obj_path:str, delta=1e-2) -> (bool, dict):
    
    subj_mesh = trimesh.load_mesh(subj_path)
    obj_mesh = trimesh.load_mesh(obj_path)
    intersection_mesh = trimesh.boolean.intersection([subj_mesh, obj_mesh], 'blender')
    
    contact_res = {'subject_volume': subj_mesh.volume, 'object_volume': obj_mesh.volume, 'intersection_volume': 0.0}
    
    if isinstance(intersection_mesh, trimesh.scene.scene.Scene) \
        or (intersection_mesh.volume/subj_mesh.volume < delta \
        and intersection_mesh.volume/obj_mesh.volume < delta):
        is_contact = False
    else:
        is_contact = True
        contact_res['intersection_volume'] = intersection_mesh.volume
    
    return is_contact, contact_res