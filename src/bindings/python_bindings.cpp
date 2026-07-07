#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/eigen.h> // Enables automatic conversion of Eigen types to/from NumPy arrays
#include "stress_solver.h"

namespace py = pybind11;
using namespace SpatialEngine;

PYBIND11_MODULE(spatial_math_py, m) {
    m.doc() = "Enterprise spatial mathematics and stress mesh manipulation kernel";

    // ---- Bind MeshNode Struct ----
    py::class_<MeshNode>(m, "MeshNode")
        .def(py::init<>())
        .def_readwrite("id", &MeshNode::id)
        .def_readwrite("position", &MeshNode::position, "Current 3D coordinates (Eigen::Vector3d)")
        .def_readwrite("rest_position", &MeshNode::rest_position, "Original baseline shape coordinates")
        .def_readwrite("force", &MeshNode::force, "Accumulated vector forces acting on the node");

    // ---- Bind TetrahedronElement Struct ----
    py::class_<TetrahedronElement>(m, "TetrahedronElement")
        .def(py::init<>())
        .def_readwrite("id", &TetrahedronElement::id)
        // Binds the fixed C-style array to Python via a property or copy approach
        .def_property("node_indices", 
            [](const TetrahedronElement& self) {
                return std::vector<int>{self.node_indices[0], self.node_indices[1], self.node_indices[2], self.node_indices[3]};
            },
            [](TetrahedronElement& self, const std::vector<int>& indices) {
                if (indices.size() != 4) {
                    throw std::runtime_error("Tetrahedron element must have exactly 4 node indices.");
                }
                for (size_t i = 0; i < 4; ++i) {
                    self.node_indices[i] = indices[i];
                }
            }
        )
        .def_readwrite("material_poisson", &TetrahedronElement::material_poisson)
        .def_readwrite("material_youngs", &TetrahedronElement::material_youngs);

    // ---- Bind StressSolver Class ----
    py::class_<StressSolver>(m, "StressSolver")
        .def(py::init<>())
        .def("apply_external_stretch", &StressSolver::apply_external_stretch,
             py::arg("node_id"), py::arg("displacement"), py::arg("nodes"),
             "Displace a specific node's current spatial coordinates to simulate stretching.")
        
        .def("update_mesh_stress", &StressSolver::update_mesh_stress,
             py::arg("nodes"), py::arg("elements"),
             "Iterate through the volumetric elements using parallel threads to compute internal stress changes.");
}
