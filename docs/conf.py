# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'fitfocus'
copyright = '2025, Gbenga'
author = 'Gbenga'
release = '2025'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'autoapi.extension',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

autoapi_type = 'python'
autoapi_dirs = ['../meal', '../onboarding', '../routines', '../utils']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']


import os
import sys
import django

sys.path.insert(0, os.path.abspath('../..'))  # path to project root
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project_name.settings")
django.setup()
