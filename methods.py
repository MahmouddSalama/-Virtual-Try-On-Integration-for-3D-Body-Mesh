import trimesh
from scipy.spatial.transform import Rotation as R
import trimesh
import pyrender
import numpy as np

def get_model_orientation_and_extents(mesh_or_scene):
    if isinstance(mesh_or_scene, trimesh.Scene):
        mesh = trimesh.util.concatenate(list(mesh_or_scene.geometry.values()))
    else:
        mesh = mesh_or_scene
    bbox_extents = mesh.bounding_box.extents
    principal_transform = mesh.principal_inertia_transform

    rotation_matrix = principal_transform[:3, :3].copy()
    euler_angles = R.from_matrix(rotation_matrix).as_euler('xyz', degrees=True)
    return {
        'extents': bbox_extents,
        'rotation_matrix': rotation_matrix,
        'euler_angles_deg': euler_angles
    }
    
def load_and_standardize_model2(filepath, target_dims=(0.5, 0.3, 1.8),angle=0.0):

    if isinstance(filepath, trimesh.Scene):
        combined = trimesh.util.concatenate(list(filepath.geometry.values()))
    else:
        combined = filepath

    rot_x = trimesh.transformations.rotation_matrix(
        angle=np.radians(angle),
        direction=[1, 0, 0],
        point=[0, 0, 0]
    )
    combined.apply_transform(rot_x)
    combined.apply_translation(-combined.centroid)


    bounds = combined.bounds
    current_dims = bounds[1] - bounds[0]  # (X, Y, Z)

    current_dims[current_dims == 0] = 1e-8

    scale_factors = np.array(target_dims) / current_dims
    scale_matrix = np.eye(4)
    np.fill_diagonal(scale_matrix, list(scale_factors) + [1])
    
    combined.apply_transform(scale_matrix)

    return combined

def estimate_shoulder_distance(mesh, z_threshold_ratio=0.85):
  
    vertices = mesh.vertices

    z_min, z_max = mesh.bounds[:, 2]
    threshold = z_min + (z_max - z_min) * z_threshold_ratio

    upper_vertices = vertices[vertices[:, 2] >= threshold]

    if len(upper_vertices) == 0:
        raise ValueError("No upper body vertices found at the given threshold.")

    x_min = upper_vertices[:, 0].min()
    x_max = upper_vertices[:, 0].max()

    shoulder_width = x_max - x_min
    return shoulder_width

def get_standerd_mesh(body):
    try:
        combined = trimesh.util.concatenate(list(body.geometry.values()))
    except:
        combined = body

    flag = get_model_orientation_and_extents(combined)['euler_angles_deg'][1]
    if (flag < 0):
        human =  load_and_standardize_model2(combined,(0.8, 0.28, 1.8),angle=90.0)
    else:
        human = load_and_standardize_model2(combined,(1.5, 0.28, 1.8),angle=0.0)
    return human
    