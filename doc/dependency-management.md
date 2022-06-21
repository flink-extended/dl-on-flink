# Dependency Management

To run the deep learning model training or inference, user typically have some
external Python dependencies. User can install the dependencies on every
TaskManager of the Flink cluster manually if it is commonly use by multiple
jobs.

For the environment where it is inconvenient to install dependencies on every
TaskManager or the dependencies that are not commonly used by multiple job. We
provide the following methods to submit the Python dependencies together with
the Flink job.

## Java API

For Java API, you can use specify the Python dependencies with the following
methods in `ClusterConfig.Builder`.

```java

public class ClusterConfig implements Serializable {
    ...

    public static class Builder<T extends Builder<T>> {
        ...

        /**
         * Add a list of python file to the PYTHON_PATH of the python process that runs in the node.
         *
         * @param pythonFilePaths A list of path of python files.
         */
        public T addPythonFile(String... pythonFilePaths) {
            ...
        }

        /**
         * Set a zipped python virtual environment under which the deep learning process will run.
         *
         * @param pythonVirtualEnvPath The path of the zipped python virtual environment.
         */
        public T setPythonVirtualEnvZip(String pythonVirtualEnvPath) {
            ...
        }
    }
}
```

If you just want to upload a few python files to the PYTHONPATH when running the
deep learning script, you can use the `addPythonFile` method. If you have some
third party dependencies to install, we recommend packaging a virtual
environment and use the `setPythonVirtualEnvZip` method to upload the Python
virtual environment with the Flink job to every TaskManager. You can refer to
the following script to prepare a Python virtual environment.

```shell
set -e
# download miniconda.sh
if [[ `uname -s` == "Darwin" ]]; then
    wget "https://repo.continuum.io/miniconda/Miniconda3-4.7.10-MacOSX-x86_64.sh" -O "miniconda.sh"
else
    wget "https://repo.continuum.io/miniconda/Miniconda3-4.7.10-Linux-x86_64.sh" -O "miniconda.sh"
fi

# add the execution permission
chmod +x miniconda.sh

# create python virtual environment
./miniconda.sh -b -p venv

# activate the conda python virtual environment
source venv/bin/activate ""

# install your dependencies
pip install scikit-learn

# deactivate the conda python virtual environment
conda deactivate

# remove the cached packages
rm -rf venv/pkgs

# package the prepared conda python virtual environment
zip -r venv.zip venv
```

## Python API

For Python API, it is seamlessly integrated with the dependency management of
PyFlink. Therefore, you can refer to
the [Dependency Management for PyFlink.](https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/dev/python/dependency_management)