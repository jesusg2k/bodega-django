# Configuration file for the Sphinx documentation builder.
#

import os
import sys
import datetime
sys.path.insert(0, os.path.abspath('../../'))
#import proyecto

# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'proyecto'
copyright = 'XXXXXXXXXXXXXXXXX'
author = 'XXXXXXXXXXXXXXXXXXx'
release = '1.0'

autodoc_mock_imports = ["tensorflow", "arcpy"]
# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.mathjax',
    'sphinx.ext.napoleon',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest'
]


templates_path = ['_templates']
exclude_patterns = []

language = 'es'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'classic'
#html_static_path = ['_static']
