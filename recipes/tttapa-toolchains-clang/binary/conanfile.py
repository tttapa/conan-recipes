import os
import shlex

from conan import ConanFile
from conan.tools.files import get
from conan.errors import ConanInvalidConfiguration


class ToolchainsConan(ConanFile):
    name = "tttapa-toolchains-clang"
    package_type = "application"
    description = "Clang cross-compilers using GCC toolchains."
    homepage = "https://github.com/tttapa/toolchains"
    settings = "os", "arch"

    _arch_triplets = {
        "x86_64": "x86_64-bionic-linux-gnu",
        "armv8": "aarch64-rpi3-linux-gnu",
        # "armv8-rpi3-linux-gnueabihf",
        "armv7hf": "armv7-neon-linux-gnueabihf",
        "armv6": "armv6-rpi-linux-gnueabihf",
    }

    def _get_gcc_version(self):
        possible_versions = self.conan_data["supported-gcc-versions"][self.version]
        return possible_versions[0]

    @property
    def _target_triplet(self):
        return self._arch_triplets[str(self.settings_target.arch)]

    def validate(self):
        if self.settings.arch != "x86_64" or self.settings.os != "Linux":
            msg = f"This toolchain is not compatible with {self.settings.os}-{self.settings.arch}. "
            msg += "It can only run on Linux-x86_64."
            raise ConanInvalidConfiguration(msg)

        invalid_arch = str(self.settings_target.arch) not in self._arch_triplets
        if self.settings_target.os != "Linux" or invalid_arch:
            msg = f"This toolchain only supports building for Linux-{','.join(self._arch_triplets)}. "
            msg += f"{self.settings_target.os}-{self.settings_target.arch} is not supported."
            raise ConanInvalidConfiguration(msg)

        if self.settings_target.compiler != "clang":
            msg = f"The compiler is set to '{self.settings_target.compiler}', but this "
            msg += "toolchain only supports building with Clang."
            raise ConanInvalidConfiguration(msg)

    def package(self):
        ref = f"{self.settings.os}-{self.settings.arch}"
        gcc_v = self._get_gcc_version()
        tgt_ref = f"{self._target_triplet}-gcc{gcc_v}"
        get(
            self,
            **self.conan_data["sources"][self.version][ref][tgt_ref],
            destination=self.package_folder,
            strip_root=True,
        )
        self.run(f"chmod -R +w {shlex.quote(self.package_folder)}")

    def package_id(self):
        self.info.settings_target = self.settings_target
        self.info.settings_target.rm_safe("build_type")

    def package_info(self):
        target = self._target_triplet
        toolchain_dir = os.path.join(self.package_folder, target)
        processor = {
            "x86_64-bionic-linux-gnu": "x86_64",
            "aarch64-rpi3-linux-gnu": "aarch64",
            "armv8-rpi3-linux-gnueabihf": "armv7l",  # armv8l does not exist
            "armv7-neon-linux-gnueabihf": "armv7l",
            "armv6-rpi-linux-gnueabihf": "armv6l",
        }[target]
        self.conf_info.define("tools.cmake.cmaketoolchain:system_name", "Linux")
        self.conf_info.define("tools.cmake.cmaketoolchain:system_processor", processor)
        self.conf_info.define("tools.gnu:host_triplet", target)
        toolchain_flags = ["--gcc-toolchain=" + toolchain_dir, "--gcc-triple=" + target]
        self.conf_info.append("tools.build:cflags", toolchain_flags)
        self.conf_info.append("tools.build:cxxflags", toolchain_flags)
        self.conf_info.define("tools.build.cross_building:cross_build", True)
