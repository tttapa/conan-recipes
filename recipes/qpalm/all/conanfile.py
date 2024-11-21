import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import can_run
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get


class QPALMRecipe(ConanFile):
    name = "qpalm"
    package_type = "library"

    # Optional metadata
    license = "LGPLv3"
    author = "Pieter P <pieter.p.dev@outlook.com>"
    url = "https://github.com/kul-optec/QPALM"
    description = "Proximal Augmented Lagrangian method for Quadratic Programs"
    topics = ("optimization", "quadratic-program", "qp", "alm")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    bool_qpalm_options = {
        "with_cxx": True,
        "with_python": False,
        "with_julia": False,
        "with_fortran": False,
        "with_examples": False,
    }
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    } | {k: [True, False] for k in bool_qpalm_options}
    default_options = {
        "shared": False,
        "fPIC": True,
    } | bool_qpalm_options

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def validate(self):
        if self.options.with_python and not self.options.with_cxx:
            msg = "Python interface requires C++. Set 'with_cxx=True'."
            raise ConanInvalidConfiguration(msg)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            destination=self.source_folder,
            strip_root=True
        )
        apply_conandata_patches(self)

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires("ladel/tttapa.20241118", transitive_headers=True)
        self.test_requires("gtest/1.15.0")
        if self.options.with_cxx:
            self.requires("eigen/tttapa.20240516", transitive_headers=True)
        if self.options.with_python:
            self.requires("pybind11/2.13.6")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        for k in self.bool_qpalm_options:
            value = getattr(self.options, k, None)
            if value is not None and value.value is not None:
                tc.variables["QPALM_" + k.upper()] = bool(value)
        if self.options.with_python:
            tc.variables["USE_GLOBAL_PYBIND11"] = True
        if can_run(self):
            tc.variables["QPALM_FORCE_TEST_DISCOVERY"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.test()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.set_property("cmake_file_name", "QPALM")
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake", "QPALM"))
        if self.options.with_cxx:
            self.cpp_info.builddirs.append(os.path.join("lib", "cmake", "QPALM_cxx"))
        if self.options.with_fortran:
            self.cpp_info.builddirs.append(os.path.join("lib", "cmake", "QPALM_fortran"))
