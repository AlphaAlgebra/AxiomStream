#ifndef SPATIAL_TRANSFORM_H
#define SPATIAL_TRANSFORM_H

#include <Eigen/Dense>

namespace SpatialEngine {

class SpatialTransform {
public:
    static Eigen::Matrix4d create_translation(double tx, double ty, double tz);
    static Eigen::Matrix4d create_rotation_x(double angle_rad);
};

} // namespace SpatialEngine

#endif // SPATIAL_TRANSFORM_H
