# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import os
import sys
import sphinx_rtd_theme
import subprocess

sys.path.insert(0, os.path.abspath('../ai_flow/api'))
sys.path.insert(0, os.path.abspath('../ai_flow/context'))
sys.path.insert(0, os.path.abspath('../ai_flow/ai_graph'))
sys.path.insert(0, os.path.abspath('../ai_flow/endpoint/server'))
sys.path.insert(0, os.path.abspath('../ai_flow/workflow'))
sys.path.insert(0, os.path.abspath('../ai_flow/client'))
sys.path.insert(0, os.path.abspath('../ai_flow/common'))
sys.path.insert(0, os.path.abspath('../ai_flow/meta'))
sys.path.insert(0, os.path.abspath('../ai_flow_plugins'))

# -- Project information -----------------------------------------------------

project = 'Flink AI Flow'
author = 'Alibaba'

# The full version, including alpha/beta/rc tags
release = '1.0'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosectionlabel',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# Following modules will be excluded as they are not public API
exclude_rst = [
    '**ai_flow.metadata_store.test.rst', 
    '**ai_flow.runtime.rst', 
    '**ai_flow.metric.service.rst', 
    '**ai_flow.exception.rst', 
    '**ai_flow.model_center.entity.rst', 
    '**ai_flow.metadata_store.test.sbin.rst', 
    '**ai_flow.translator.rst', 
    '**ai_flow.model_center.rst', 
    '**ai_flow.model_center.service.rst', 
    '**ai_flow.scheduler.rst', 
    '**ai_flow.endpoint.client.rst', 
    '**ai_flow.util.rst',
    '**ai_flow.metadata_store.rst',  
    '**ai_flow.store.rst', 
    '**ai_flow.log.rst', 
    '**ai_flow.protobuf.rst', 
    '**ai_flow.metadata_store.utils.rst', 
    '**ai_flow.util.model_util.rst', 
    '**ai_flow.metric.rst', 
    '**ai_flow.metadata_store.service.rst',  
    '**ai_flow.util.file_util.rst', 

    '**ai_flow_plugins.scheduler_plugins.airflow.rst', 
    '**ai_flow_plugins.job_plugins.utils.rst', 

    '**modules.rst', 
]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
# We will not show any documents for API in genrated API doc
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**test**'] + exclude_rst
# Look at the first line of the docstring for function and method signatures.
autodoc_docstring_signature = True

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

autodoc_mock_imports = ['bs4', 'requests']

autoclass_content = 'both'

# If false, no module index is generated.
html_domain_indices = False
# If false, no index is generated.
html_use_index = False

# Output file base name for HTML help builder.
htmlhelp_basename = 'flinkaiflowdoc'

def autodoc_skip_member(app, what, name, obj, skip, options):
    exclusions = ('__doc__', '__module__', '__dict__')
    exclude = name in exclusions
    # return True if (skip or exclude) else None  # Can interfere with subsequent skip functions.
    return True if exclude else None
 
def setup(app):
    app.connect('autodoc-skip-member', autodoc_skip_member)
    dir=os.path.dirname(os.path.abspath(__file__))
    subprocess.call(['bash', dir+'/docgen.sh'])