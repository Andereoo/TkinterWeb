# Configuration file for the Sphinx documentation builder.

# -- Project information

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname((os.path.realpath(__file__))))))

project = 'TkinterWeb'
copyright = '2025, Andereoo'
author = 'Andereoo'

release = '4.0'
version = '4.0.3'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}

templates_path = ['_templates']

# -- Options for HTML output

autodoc_member_order = 'bysource'

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'
