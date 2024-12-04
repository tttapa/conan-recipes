from io import StringIO
from conan import ConanFile
import re


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        tokens = re.split("[@#]", self.tested_reference_str)
        toolchains, required_version = tokens[0].split("/", 1)
        variant = self.dependencies.direct_build[toolchains].options.target
        self.run(f"{variant}-g++ --version", output := StringIO())
        print(out := output.getvalue(), end="")
        assert required_version in out
