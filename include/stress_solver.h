#ifndef SPATIAL_STRESS_SOLVER_H
#define SPATIAL_STRESS_SOLVER_H

#include <Eigen/Dense>
#include <vector>

namespace SpatialEngine {

// Represents a node in the 3D stress mesh
struct MeshNode {
    int id;
    Eigen::Vector3d position;     // Current 3D coordinates
    Eigen::Vector3d rest_position;// Original shape coordinates
    Eigen::Vector3d force;         // Accumulated internal/external forces
};

// Represents a volumetric element (Tetrahedron) connecting 4 nodes
struct TetrahedronElement {
    int id;
    int node_indices[4];          // Indices pointing to the global node list
    double material_poisson;      // Poisson's ratio (lateral strain / axial strain)
    double material_youngs;       // Young's Modulus (material stiffness)
};

class StressSolver {
public:
    StressSolver() = default;
    ~StressSolver() = default;

    // Core simulation steps
    void compute_deformation_gradient(const TetrahedronElement& element, const std::vector<MeshNode>& nodes);
    void apply_external_stretch(int node_id, const Eigen::Vector3d& displacement, std::vector<MeshNode>& nodes);
    void update_mesh_stress(std::vector<MeshNode>& nodes, const std::vector<TetrahedronElement>& elements);

private:
    // Helper to calculate strain and stress tensors using Linear Elasticity / Hooke's Law
    std::pair<Eigen::Matrix3d, Eigen::Matrix3d> calculate_elastic_tensors(
        const Eigen::Matrix3d& deformation_gradient, 
        double youngs, 
        double poisson
    );
};

} // namespace SpatialEngine

#endif // SPATIAL_STRESS_SOLVER_H
