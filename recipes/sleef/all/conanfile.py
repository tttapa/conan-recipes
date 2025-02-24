# Based on https://github.com/conan-io/conan-center-index/blob/5ead0ed936701285c4cae4d79f2878047ba19eb3/recipes/sleef/all/conanfile.py

import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir, apply_conandata_patches, export_conandata_patches
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class SleefConan(ConanFile):
    name = "sleef"
    description = "SLEEF is a library that implements vectorized versions of C standard math functions."
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sleef.org"
    topics = ("vectorization", "simd")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration(
                "shared sleef not supported on Windows, it produces runtime errors"
            )
        if self.settings.compiler == "apple-clang":
            if Version(self.version) < "3.6" and self.settings.arch == "armv8":
                # clang: error: the clang compiler does not support '-march=armv7-a'
                # clang: warning: argument unused during compilation: '-mfpu=vfpv4' [-Wunused-command-line-argument]
                # clang: warning: argument unused during compilation: '-arch arm64' [-Wunused-command-line-argument]
                # clang: warning: argument unused during compilation: '-mmacosx-version-min=11.0' [-Wunused-command-line-argument]
                raise ConanInvalidConfiguration(f"{self.ref} does not support Mac M1. Please, use {self.name} version >=3.6.")

    def requirements(self):
        if Version(self.version) >= "3.6":
            self.tool_requires("cmake/[>=3.18 <4]")
        print(self.conf.get("tools.build.cross_building:cross_build", check_type=bool))
        if self.context != "build":
            self.tool_requires("sleef/" + str(self.version))

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        VirtualBuildEnv(self).generate()

        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        if Version(self.version) >= "3.6":
            tc.cache_variables["SLEEF_BUILD_STATIC_TEST_BINS"] = False
            tc.cache_variables["SLEEF_BUILD_LIBM"] = True
            tc.cache_variables["SLEEF_BUILD_DFT"] = False
            tc.cache_variables["SLEEF_BUILD_QUAD"] = False
            tc.cache_variables["SLEEF_BUILD_GNUABI_LIBS"] = False
            tc.cache_variables["SLEEF_BUILD_SCALAR_LIB"] = False
            tc.cache_variables["SLEEF_BUILD_TESTS"] = False
            tc.cache_variables["SLEEF_BUILD_INLINE_HEADERS"] = False
            tc.cache_variables["SLEEF_SHOW_CONFIG"] = True
            tc.cache_variables["SLEEF_SHOW_ERROR_LOG"] = False
            tc.cache_variables["SLEEF_ENABLE_ALTDIV"] = False
            tc.cache_variables["SLEEF_ENABLE_ALTSQRT"] = False
            tc.cache_variables["SLEEF_DISABLE_FFTW"] = True
            tc.cache_variables["SLEEF_DISABLE_MPFR"] = True
            tc.cache_variables["SLEEF_DISABLE_SSL"] = True
            tc.cache_variables["SLEEF_ENABLE_CUDA"] = False
            tc.cache_variables["SLEEF_ENABLE_CXX"] = False
        else:
            tc.cache_variables["BUILD_DFT"] = False
            tc.cache_variables["BUILD_GNUABI_LIBS"] = False
            tc.cache_variables["BUILD_TESTS"] = False
            tc.cache_variables["DISABLE_FFTW"] = True
        if cross_building(self):
            native_sleef = self.dependencies.build["sleef"]
            tc.cache_variables["NATIVE_BUILD_DIR"] = native_sleef.package_folder
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "dummy"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "sleef")
        self.cpp_info.libs = ["sleef"]
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines = ["SLEEF_STATIC_LIBS"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
