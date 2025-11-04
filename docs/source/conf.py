# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = 'LOLA OS'
copyright = '2025, Levi Chinecherem Chidi'
author = 'Levi Chinecherem Chidi'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
import os
import sys
sys.path.insert(0, os.path.abspath('../../python'))  # Point to lola package

extensions = [
    'myst_parser',              # Markdown support
    'sphinx.ext.autodoc',       # API documentation
    'sphinx.ext.napoleon',      # Google-style docstrings
    'sphinx.ext.viewcode',      # Source code links
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
myst_enable_extensions = ["colon_fence"]  # Support for code blocks

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = 'sphinx_rtd_theme'  # Better readability than alabaster
html_static_path = ['_static']
html_theme_options = {
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
}