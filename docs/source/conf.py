import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

project = "PyAmplitude"
author = "Marcos Manuel Muraro"
release = "2.0.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = []
html_theme = "alabaster"
autodoc_typehints = "description"
napoleon_google_docstring = True
napoleon_numpy_docstring = True
