#include "spatial_transform.h"
#include <cmath>

namespace SpatialEngine {

Eigen::Matrix4d SpatialTransform::create_translation(double tx, double ty, double tz) {
    Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
    m(0,3) = tx; m(1,3) = ty; m(2,3) = tz;
    return m;
}

Eigen::Matrix4d SpatialTransform::create_rotation_x(double angle_rad) {
    Eigen::Matrix4d m = Eigen::Matrix4d::Identity();
    double c = std::cos(angle_rad);
    double s = std::sin(angle_rad);
    m(1,1) = c;  m(1,2) = -s;
    m(2,1) = s;  m(2,2) = c;
    return m;
}

} // namespace SpatialEngine
