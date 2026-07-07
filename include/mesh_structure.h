#ifndef SPATIAL_MESH_STRUCTURE_H
#define SPATIAL_MESH_STRUCTURE_H

#include <vector>
#include <string>
#include <Eigen/Dense>

namespace SpatialEngine {

class MeshStructure {
public:
    MeshStructure() = default;
    ~MeshStructure() = default;

    bool load_from_file(const std::string& filepath);
    bool validate_mesh_quality() const;
    
    std::vector<Eigen::Vector3d> vertices;
    std::vector<Eigen::Vector4i> tetrahedra;
};

} // namespace SpatialEngine

#endif // SPATIAL_MESH_STRUCTURE_H

