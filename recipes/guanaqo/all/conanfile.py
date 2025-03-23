import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get
from conan.tools.scm import Version


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
        "with_itt": False,
        "with_tracing": False,
        "with_openmp": False,
        "with_blas": False,
        "with_mkl": False,
    }
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "blas_index_type": ["int", "long", "long long"],
    } | {k: [True, False] for k in bool_guanaqo_options}
    default_options = {
        "shared": False,
        "fPIC": True,
        "blas_index_type": "long long",
    } | bool_guanaqo_options

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
        if Version(self.version).in_range("<1.0.0-alpha.8", resolve_prerelease=True):
            self.options.rm_safe("with_itt")
            self.options.rm_safe("with_tracing")
        if Version(self.version).in_range("<1.0.0-alpha.9", resolve_prerelease=True):
            self.options.rm_safe("with_blas")
            self.options.rm_safe("with_mkl")
            self.options.rm_safe("blas_index_type")
        if Version(self.version).in_range("<1.0.0-alpha.10", resolve_prerelease=True):
            self.options.rm_safe("with_openmp")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.get_safe("with_blas"):
            if not self.options.with_mkl:
                # OpenBLAS does not allow configuring the index type
                self.options.rm_safe("blas_index_type")
        else:
            self.options.rm_safe("with_mkl")

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
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("with_itt"):
            self.requires("ittapi/3.24.4", transitive_headers=True)
        if self.options.get_safe("with_blas") and not self.options.get_safe("with_mkl"):
            self.requires("openblas/0.3.27", transitive_headers=True)
        self.test_requires("gtest/1.15.0")
        self.test_requires("eigen/tttapa.20240516")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        for k in self.bool_guanaqo_options:
            value = self.options.get_safe(k)
            if value is not None and value.value is not None:
                tc.variables["GUANAQO_" + k.upper()] = bool(value)
        if self.options.get_safe("with_blas") and not self.options.get_safe("with_mkl"):
            tc.variables["GUANAQO_WITH_OPENBLAS"] = True
            tc.variables["GUANAQO_BLAS_INDEX_TYPE"] = self.options.get_safe(
                "blas_index_type", default="int"
            )
        if can_run(self):
            tc.variables["GUANAQO_FORCE_TEST_DISCOVERY"] = True
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
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake", "guanaqo"))
