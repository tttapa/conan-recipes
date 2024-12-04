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

    def build(self):
        os_name = str(self.settings.os)
        target = str(self.options.target)
        get(
            self,
            **self.conan_data["sources"][self.version][os_name][target],
            destination=self.source_folder,
            strip_root=True
        )

    def package(self):
        copy(self, "*", src=self.build_folder, dst=self.package_folder)

    def package_info(self):
        target = str(self.options.target)
        bindir = os.path.join(self.package_folder, target, "bin")
        self.buildenv_info.prepend_path("PATH", bindir)
