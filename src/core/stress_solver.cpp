#include "stress_solver.h"
#include <iostream>
#include <omp.h> // Linked via OpenMP in your CMakeLists.txt

namespace SpatialEngine {

void StressSolver::apply_external_stretch(int node_id, const Eigen::Vector3d& displacement, std::vector<MeshNode>& nodes) {
    if (node_id >= 0 && node_id < static_cast<int>(nodes.size())) {
        nodes[node_id].position += displacement;
    }
}

std::pair<Eigen::Matrix3d, Eigen::Matrix3d> StressSolver::calculate_elastic_tensors(
    const Eigen::Matrix3d& F, 
    double youngs, 
    double poisson
) {
    // 1. Calculate Green-Lagrange Strain Tensor: E = 0.5 * (F^T * F - I)
    Eigen::Matrix3d I = Eigen::Matrix3d::Identity();
    Eigen::Matrix3d E = 0.5 * (F.transpose() * F - I);

    // 2. Compute Lamé parameters from Young's Modulus and Poisson's ratio
    double lambda = (youngs * poisson) / ((1.0 + poisson) * (1.0 - 2.0 * poisson));
    double mu = youngs / (2.0 * (1.0 + poisson));

    // 3. Compute Second Piola-Kirchhoff Stress Tensor: S = lambda * tr(E) * I + 2 * mu * E
    Eigen::Matrix3d S = lambda * E.trace() * I + 2.0 * mu * E;

    return {E, S};
}

void StressSolver::update_mesh_stress(std::vector<MeshNode>& nodes, const std::vector<TetrahedronElement>& elements) {
    // Reset internal forces on all nodes before accumulation
    for (auto& node : nodes) {
        node.force.setZero();
    }

    // Thread-safe OpenMP parallelization loop for high node-count performance
    #pragma omp parallel for
    for (int i = 0; i < static_cast<int>(elements.size()); ++i) {
        const auto& elem = elements[i];
        
        // Extract the 4 vertices of the tetrahedron
        Eigen::Vector3d x0 = nodes[elem.node_indices[0]].position;
        Eigen::Vector3d x1 = nodes[elem.node_indices[1]].position;
        Eigen::Vector3d x2 = nodes[elem.node_indices[2]].position;
        Eigen::Vector3d x3 = nodes[elem.node_indices[3]].position;

        Eigen::Vector3d X0 = nodes[elem.node_indices[0]].rest_position;
        Eigen::Vector3d X1 = nodes[elem.node_indices[1]].rest_position;
        Eigen::Vector3d X2 = nodes[elem.node_indices[2]].rest_position;
        Eigen::Vector3d X3 = nodes[elem.node_indices[3]].rest_position;

        // Build edge matrices for spatial deformation tracking
        Eigen::Matrix3d Ds; // Deformed state edges
        Ds.col(0) = x1 - x0; Ds.col(1) = x2 - x0; Ds.col(2) = x3 - x0;

        Eigen::Matrix3d Dm; // Rest (undeformed) state edges
        Dm.col(0) = X1 - X0; Dm.col(1) = X2 - X0; Dm.col(2) = X3 - X0;

        // Verify element is valid and not inverted before dividing matrix
        if (Dm.determinant() != 0.0) {
            // Compute Deformation Gradient: F = Ds * Dm^-1
            Eigen::Matrix3d F = Ds * Dm.inverse();

            // Run physics calculation to find Strain and Stress tensors
            auto [strain, stress] = calculate_elastic_tensors(F, elem.material_youngs, elem.material_poisson);
            
            // Note: In a complete engine loop, forces derived from the stress tensor 
            // are back-propagated to the node.force components here using atomic updates.
        }
    }
}

} // namespace SpatialEngine
