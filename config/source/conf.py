# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'mydoc'
copyright = '2025, UP2160428'
author = 'UP2160428'


extensions = [
    'autoapi.extension',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

html_theme = 'sphinx_rtd_theme'
autoapi_type = 'python'
autoapi_dirs = ['../../meal', '../../onboarding', '../../routines']

import os
import sys
import django

sys.path.insert(0, os.path.abspath('../..'))  # path to project root
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fitfocus.settings")
django.setup()

