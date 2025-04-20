import trimesh
import pyrender
import pyrender
import methods as m

scene = pyrender.Scene()

female_body1 = trimesh.load(r"files\Female\female_body_base.glb")
female_body2 = trimesh.load(r"files\Female\female_body.glb")
male_body1 = trimesh.load(r"files\Male\male_body-1.glb")
male_body2 = trimesh.load(r"files\Male\male_body-2.glb")
male_body3=trimesh.load(r"files\Male\Local-Generated-1.obj")
male_body4=trimesh.load(r"files\Male\Local-Generated-2.obj")



def cloth_mesh(mesh):
    tshirt = trimesh.load(r"files\T-shirt Sample\static_tshirt.glb")

    tshirt_meshes = list(tshirt.geometry.values())
    tshirt = trimesh.util.concatenate(tshirt_meshes)
    human = m.get_standerd_mesh(mesh)
    d=m.estimate_shoulder_distance(human)
    if d>.4:
        d=d*2.7
    else:
        d*=3.6
    print(d)

    tshirt=m.load_and_standardize_model2(tshirt,(d, 0.45, 0.85),angle=90.0)
    body_scale = human.bounding_box.extents / tshirt.bounding_box.extents
    body_center = human.bounding_box.centroid
    shirt_center = tshirt.bounding_box.centroid

    tshirt.apply_translation([0.0, 0, .240])

    scene = pyrender.Scene()
    scene.add(pyrender.Mesh.from_trimesh(human))
    scene.add(pyrender.Mesh.from_trimesh(tshirt))

    pyrender.Viewer(scene, use_raymond_lighting=True)
    
    
l=[male_body2,female_body2,male_body1,]
for i in l:
    cloth_mesh(i)