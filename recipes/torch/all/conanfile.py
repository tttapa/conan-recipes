import os
from pathlib import Path
import sys

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get


class TorchRecipe(ConanFile):
    name = "torch"
    package_type = "library"

    # Optional metadata
    author = "Pieter P <pieter.p.dev@outlook.com>"
    url = "https://github.com/pytorch/pytorch"
    description = "Tensors and Dynamic neural networks in Python with strong GPU acceleration"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_cuda": [True, False],
        "with_numa": [False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "with_cuda": True,
        "with_numa": False,  # Currently broken because of versioned symbols in a static library
    }

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
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openblas/0.3.27")
        self.requires("eigen/3.4.0")
        self.requires("sleef/tttapa.3.6")
        self.requires("cpuinfo/cci.20231129")
        self.requires("fp16/cci.20210320")
        self.requires("pybind11/2.13.6")
        self.requires("pthreadpool/cci.20231129")
        self.requires("psimd/cci.20200517")
        self.requires("fxdiv/cci.20200417")
        self.requires("onnx/1.17.0")
        self.requires("xnnpack/cci.20240229")
        self.requires("ittapi/3.24.4")
        self.requires("openmpi/4.1.6")
        self.requires("nvtx/tttapa.3.1.1", transitive_headers=True)
        if self.options.with_numa:
            self.requires("libnuma/2.0.19")
        if self.options.with_cuda:
            self.tool_requires("nvcc/12.4.1")
        self.test_requires("benchmark/1.9.1")
        self.test_requires("gtest/1.15.0")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["USE_SYSTEM_LIBS"] = True  # Don't use pytorch's bundled depedencies
        tc.variables["USE_GLOO"] = False  # Unavailable in CCI
        tc.variables["USE_NCCL"] = False  # Large dependency
        tc.variables["USE_CUDA"] = self.options.with_cuda
        tc.variables["USE_NUMA"] = self.options.with_numa
        tc.variables["USE_XPU"] = False
        tc.variables["USE_NNPACK"] = False
        tc.variables["USE_XNNPACK"] = False
        tc.variables["USE_MAGMA"] = False
        tc.variables["USE_MPI"] = True
        tc.variables["USE_NUMPY"] = False
        tc.variables["BUILD_PYTHON"] = False
        tc.variables["PYTHON_EXECUTABLE"] = Path(sys.executable).as_posix()
        if self.settings.compiler.get_safe("libcxx") == "libstdc++11":
            tc.variables["GLIBCXX_USE_CXX11_ABI"] = "1"
        # TORCH_CUDA_ARCH_LIST needs to be a cache variable
        extra_vars = self.conf.get("tools.cmake.cmaketoolchain:extra_variables")
        cuda_arch_list = extra_vars.get("TORCH_CUDA_ARCH_LIST")
        if cuda_arch_list:
            tc.variables["TORCH_CUDA_ARCH_LIST"] = cuda_arch_list
        tc.generate()

    def build(self):
        print(self.conf.get("tools.cmake.cmaketoolchain:extra_variables"))
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.test()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.builddirs.append(os.path.join("share", "cmake", "Torch"))
        self.cpp_info.builddirs.append(os.path.join("share", "cmake", "Tensorpipe"))
        self.cpp_info.builddirs.append(os.path.join("share", "cmake", "Caffe2"))
        self.cpp_info.builddirs.append(os.path.join("share", "cmake", "ATen"))
