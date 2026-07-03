cmake_minimum_required(VERSION 3.20 FATAL_ERROR)
project(SpatialStressEngine VERSION 1.0.0 LANGUAGES CXX)

# ---- Compile Options & Standards ----
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Force optimization for high-performance physics tracking
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -ffast-math")

# ---- Dependency Management ----
# Find Eigen3 for spatial tensors, matrices, and linear algebra solvers
find_package(Eigen3 3.4 REQUIRED)

# Find OpenMP to enable multi-threaded stress loop iterations
find_package(OpenMP REQUIRED)

# ---- Target 1: Core Spatial Math & FEM Library ----
add_library(spatial_math_core STATIC)

target_sources(spatial_math_core
    PRIVATE
        src/core/mesh_structure.cpp
        src/core/stress_solver.cpp
        src/core/spatial_transform.cpp
)

target_include_directories(spatial_math_core
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        Eigen3::Eigen
)

target_link_libraries(spatial_math_core
    PUBLIC
        Eigen3::Eigen
        OpenMP::OpenMP_CXX
)

# ---- Target 2: Standalone Engine Executable (Testing/CLI) ----
add_executable(stress_engine_cli src/main.cpp)
target_link_libraries(stress_engine_cli PRIVATE spatial_math_core)

# ---- Target 3: Python Bindings (Optional, requires pybind11) ----
# Enable this block by installing pybind11 via system package manager or git submodule
find_package(pybind11 CONFIG QUIET)
if(pybind11_FOUND)
    message(STATUS "Found pybind11. Building Python bindings...")
    pybind11_add_module(spatial_math_py src/bindings/python_bindings.cpp)
    target_link_libraries(spatial_math_py PRIVATE spatial_math_core)
else()
    message(STATUS "pybind11 not found. Skipping Python module build.")
endif()

