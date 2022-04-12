#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import platform
import re
import subprocess
import sys
from datetime import datetime
from distutils.version import LooseVersion
from glob import glob

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext

this_directory = os.path.abspath(os.path.dirname(__file__))
version_file = os.path.join(this_directory, 'dl_on_flink_tensorflow/version.py')

in_dl_on_flink_source = os.path.isfile(
    "../../dl-on-flink-framework/python/dl_on_flink_framework/include/spscqueue.h")

try:
    exec(open(version_file).read())
except IOError:
    print("Failed to load dl_on_flink_tensorflow version file for packaging. " +
          "'%s' not found!" % version_file,
          file=sys.stderr)
    sys.exit(-1)
VERSION = __version__  # noqa
PACKAGE_NAME = "dl-on-flink-tensorflow"
DL_ON_FLINK_FRAMEWORK_PACKAGE_NAME = "dl-on-flink-framework"

if os.getenv("NIGHTLY_WHEEL") == "true":
    if 'dev' not in VERSION:
        raise RuntimeError("Nightly wheel is not supported for non dev version")
    VERSION = VERSION[:str.find(VERSION, 'dev') + 3] + \
        datetime.now().strftime('%Y%m%d')


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError(
                "CMake must be installed to build the following extensions: " +
                ", ".join(e.name for e in self.extensions))

        if platform.system() == "Windows":
            cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)',
                                                   out.decode()).group(1))
            if cmake_version < '3.1.0':
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        import tensorflow as tf
        extdir = os.path.abspath(
            os.path.dirname(self.get_ext_fullpath(ext.name)))
        tf_lib = tf.sysconfig.get_lib()
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DPYTHON_EXECUTABLE=' + sys.executable,
                      f'-DTensorFlow_INCLUDE_DIR={tf.sysconfig.get_include()}',
                      f'-DTensorFlow_C_LIBRARY={self.get_tf_lib(tf_lib)}',
                      f'-DDL_ON_FLINK_FRAMEWORK_INCLUDE_DIR={self._get_dl_on_flink_include()}']

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(
                cfg.upper(),
                extdir)]
            if sys.maxsize > 2 ** 32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j2']
            if platform.system() == "Linux":
                build_args += ['-lpthread']

        env = os.environ.copy()
        env['CXXFLAGS'] = \
            '{} -D_GLIBCXX_USE_CXX11_ABI=0 -DVERSION_INFO=\\"{}\\"'.format(
                env.get('CXXFLAGS', ''),
                self.distribution.get_version())
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args,
                              cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.'] + build_args,
                              cwd=self.build_temp)

    def _get_dl_on_flink_include(self):
        if not in_dl_on_flink_source:
            import dl_on_flink_framework.sysconfig
            return dl_on_flink_framework.sysconfig.get_include()
        include_path = os.path.join(os.path.dirname(os.path.dirname(this_directory)),
                                    "dl-on-flink-framework", "python",
                                    "dl_on_flink_framework", "include")
        return include_path

    @staticmethod
    def get_tf_lib(tf_lib):
        print(os.path.join(tf_lib, "tensorflow_framework"))
        return glob(os.path.join(tf_lib, "*tensorflow_framework*"))[0]


setup_requires = ['tensorflow>=1.15.0, <2.0.0']
if not in_dl_on_flink_source:
    setup_requires.append(f'{DL_ON_FLINK_FRAMEWORK_PACKAGE_NAME}=={VERSION}')

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    python_requires=">=3.6,<3.8",
    include_package_data=True,
    packages=find_packages(),
    ext_modules=[CMakeExtension('dl_on_flink_tensorflow/dl_on_flink_tensorflow')],
    cmdclass={'build_ext': CMakeBuild},
    zip_safe=False,
    install_requires=['tensorflow>=1.15.0, <2.0.0',
                      'tensorboard>=1.15.0, <2.0.0',
                      f'{DL_ON_FLINK_FRAMEWORK_PACKAGE_NAME}=={VERSION}',
                      'apache-flink>=1.14.0, <1.15.0',
                      'apache-flink-ml==2.0.0'],
    setup_requires=setup_requires,
    url='https://github.com/flink-extended/dl-on-flink',
    license='https://www.apache.org/licenses/LICENSE-2.0'
)
