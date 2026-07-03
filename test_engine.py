import sys
import os
import numpy as np

# Dynamically link the location paths
sys.path.append(os.path.abspath("."))
sys.path.append(os.path.abspath("./build"))

try:
    import spatial_math_py as engine
    print("[SUCCESS] Found spatial_math_py module.")
except ImportError as e:
    print(f"[FAIL] Could not import engine core module: {e}")
    print("Hint: Run ./setup.sh again to make sure compilation completed.")
    sys.exit(1)

print("--- Initializing Volumetric Stress Test Loop ---")
nodes = []
# Create four nodes forming a solid 3D tetrahedron structure
coords = [[0.,0.,0.], [1.,0.,0.], [0.,1.,0.], [0.,0.,1.]]
for i, coord in enumerate(coords):
    n = engine.MeshNode()
    n.id = i
    n.position = np.array(coord, dtype=np.float64)
    n.rest_position = np.array(coord, dtype=np.float64)
    n.force = np.zeros(3, dtype=np.float64)
    n.von_mises_stress = 0.0
    nodes.append(n)
    
element = engine.TetrahedronElement()
element.id = 0
element.node_indices = [0, 1, 2, 3] # Fixed broken line assignment
element.material_youngs = 2.1e11
element.material_poisson = 0.3

solver = engine.StressSolver()
print("Applying structural stretch manipulation to Node 1...")
solver.apply_external_stretch(1, np.array([0.05, 0.0, 0.0]), nodes)
solver.update_mesh_stress(nodes, [element])

print("\n--- Simulation Results Matrix ---")
for node in nodes:
    print(f"Node ID {node.id} | Stress Scalar: {node.von_mises_stress:.4e} Pa")
