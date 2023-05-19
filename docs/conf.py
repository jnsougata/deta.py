import os
import re
import sys

sys.path.insert(0, os.path.abspath('..'))

project = 'deta'
copyright = '2022-present, Sougata Jana'
author = 'Sougata Jana'

version = ''
with open('../deta/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)  # type: ignore

release = version


templates_path = ['_templates']
exclude_patterns = []

html_theme = 'furo'
html_static_path = ['_static']

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode', 'sphinx.ext.napoleon']
