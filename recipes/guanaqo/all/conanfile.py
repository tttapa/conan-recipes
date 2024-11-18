import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get


class guanaqoRecipe(ConanFile):
    name = "guanaqo"
    package_type = "library"

    # Optional metadata
    author = "Pieter P <pieter.p.dev@outlook.com>"
    url = "https://github.com/tttapa/guanaqo"
    description = "Utilities for scientific software."
    topics = "scientific software"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    bool_guanaqo_options = {
        "with_quad_precision": False,
    }
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    } | {k: [True, False] for k in bool_guanaqo_options}
    default_options = {
        "shared": False,
        "fPIC": True,
    } | bool_guanaqo_options

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

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
        self.test_requires("gtest/1.14.0")
        self.test_requires("eigen/3.4.0")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        for k in self.bool_guanaqo_options:
            value = getattr(self.options, k, None)
            if value is not None and value.value is not None:
                tc.variables["GUANAQO_" + k.upper()] = bool(value)
        if can_run(self):
            tc.variables["GUANAQO_FORCE_TEST_DISCOVERY"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake", "guanaqo"))
