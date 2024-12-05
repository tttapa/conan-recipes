import os

from conan import ConanFile
from conan.tools.gnu import (
    Autotools,
    AutotoolsToolchain,
    PkgConfigDeps,
    AutotoolsDeps,
)
from conan.tools.files import get


class CPythonRecipe(ConanFile):
    name = "tttapa-python-dev-build"
    package_type = "application"

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            destination=self.source_folder,
            strip_root=True
        )

    def requirements(self):
        self.requires("zlib/1.3.1")

    def generate(self):
        pc = PkgConfigDeps(self)
        pc.generate()
        tc = AutotoolsDeps(self)
        tc.generate()
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--enable-ipv6")
        tc.configure_args.append("--disable-test-modules")
        tc.configure_args.append("--with-ensurepip=no")
        tc.extra_ldflags.append("-Wl,-rpath,\\\\$\\$ORIGIN/../lib")
        tc.generate()

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install(target="altinstall")

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.buildenv_info.prepend_path("PATH", bindir)
        libdir = os.path.join(self.package_folder, "lib")
        self.runenv_info.prepend_path("LD_LIBRARY_PATH", libdir)
