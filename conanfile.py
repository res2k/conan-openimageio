from conans import ConanFile, tools, CMake
import os

class OpenImageIOConan(ConanFile):

    name = "openimageio"
    version = "2.1.10.0"
    description = "OpenImageIO is a library for reading and writing images, and a bunch of related classes, utilities, and applications."
    topics = ["graphics", "images", "vfx"]
    url = "https://github.com/p-podsiadly/conan-openimageio"
    homepage = "https://github.com/OpenImageIO/oiio"
    license = "BSD-3-Clause"

    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "with_webp": [True, False],
        "with_jpeg2000": [True, False]
    }

    default_options = {
        "shared": False,
        "with_webp": True,
        "with_jpeg2000": True
    }

    generators = "cmake", "cmake_find_package"

    requires = [
        "boost/1.71.0",
        "tsl-robin-map/0.6.1@tessil/stable",
        "openexr/2.4.0",
        "libtiff/4.0.9",
        "libpng/1.6.37",
        "libjpeg-turbo/2.0.2"
    ]

    _source_subfolder = "source_subfolder"

    exports = ["oiio.patch"]

    def requirements(self):

        if self.options.with_webp:
            self.requires("libwebp/1.0.3")

        if self.options.with_jpeg2000:
            self.requires("openjpeg/2.3.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "oiio-Release-{}".format(self.version)
        os.rename(extracted_dir, self._source_subfolder)

        tools.patch(base_path=self._source_subfolder, patch_file="oiio.patch", strip=1)

    def _configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["USE_OPENGL"] = False
        cmake.definitions["USE_QT"] = False
        cmake.definitions["LINKSTATIC"] = False
        cmake.definitions["OIIO_BUILD_TOOLS"] = False
        cmake.definitions["OIIO_BUILD_TESTS"] = False
        cmake.definitions["BUILD_DOCS"] = False
        cmake.definitions["INSTALL_FONTS"] = False
        cmake.definitions["USE_PYTHON"] = False

        # When set, OIIO's externalpackages.cmake will not call find_package for Boost.
        # Instead, we're patching the file to use conan-generated Find module.
        cmake.definitions["BOOST_CUSTOM"] = True

        cmake.configure(source_folder=self._source_subfolder)
        
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        self.copy("LICENSE-THIRD-PARTY.md", dst="licenses", src=self._source_subfolder)

    def package_info(self):

        self.cpp_info.libs = ["OpenImageIO", "OpenImageIO_Util"]
        
        if not self.options.shared:
            self.cpp_info.defines.append("OIIO_STATIC_DEFINE")