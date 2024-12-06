import os

from conan import ConanFile
from conan.tools.files import get, copy
from conan.errors import ConanInvalidConfiguration


class ToolchainsConan(ConanFile):
    name = "tttapa-toolchains"
    package_type = "application"
    description = "GCC cross-compilers."
    homepage = "https://github.com/tttapa/toolchains"
    settings = "os", "arch"

    options = {
        "target": [
            "x86_64-bionic-linux-gnu",
            "aarch64-rpi3-linux-gnu",
            "armv8-rpi3-linux-gnueabihf",
            "armv7-neon-linux-gnueabihf",
            "armv6-rpi-linux-gnueabihf",
        ]
    }
    default_options = {"target": "x86_64-bionic-linux-gnu"}

    def validate(self):
        if self.settings.arch != "x86_64" or self.settings.os != "Linux":
            msg = "Binaries are only provided for Linux on x86_64"
            raise ConanInvalidConfiguration(msg)

    def package(self):
        os_name = str(self.settings.os)
        target = str(self.options.target)
        get(
            self,
            **self.conan_data["sources"][self.version][os_name][target],
            destination=self.package_folder,
            strip_root=True,
        )
        os.system(f"chmod -R +w {self.package_folder}")

    def package_info(self):
        target = str(self.options.target)
        bindir = os.path.join(self.package_folder, target, "bin")
        self.buildenv_info.prepend_path("PATH", bindir)
        libname = {
            "x86_64-bionic-linux-gnu": "lib64",
            "aarch64-rpi3-linux-gnu": "lib64",
            "armv8-rpi3-linux-gnueabihf": "lib",
            "armv7-neon-linux-gnueabihf": "lib",
            "armv6-rpi-linux-gnueabihf": "lib",
        }[target]
        libdir = os.path.join(self.package_folder, target, target, libname)
        processor = {
            "x86_64-bionic-linux-gnu": "x86_64",
            "aarch64-rpi3-linux-gnu": "aarch64",
            "armv8-rpi3-linux-gnueabihf": "armv7l",  # armv8l does not exist
            "armv7-neon-linux-gnueabihf": "armv7l",
            "armv6-rpi-linux-gnueabihf": "armv6l",
        }[target]
        self.runenv_info.prepend_path("LD_LIBRARY_PATH", libdir)
        self.conf_info.define("tools.cmake.cmaketoolchain:system_name", "Linux")
        self.conf_info.define("tools.cmake.cmaketoolchain:system_processor", processor)
        self.conf_info.define("tools.gnu:host_triplet", target)
        compilers = {
            "c": f"{target}-gcc",
            "cpp": f"{target}-g++",
            "fortran": f"{target}-gfortran",
        }
        self.conf_info.update("tools.build:compiler_executables", compilers)
        self.conf_info.define("tools.build.cross_building:cross_build", True)
