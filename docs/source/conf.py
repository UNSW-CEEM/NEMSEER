# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("../../src/"))


# -- Project information -----------------------------------------------------

project = "NEMSEER"
copyright = "2022, Abhijith (Abi) Prakash"
author = "Abhijith (Abi) Prakash"

# The full version, including alpha/beta/rc tags
release = "1.0.1"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

# autodoc allows docstrings to be pulled straight from your code
# napoleon supports Google/NumPy style docstrings
# intersphinx can link to other docs, e.g. standard library docs for try:
# doctest enables doctesting
# todo is self explanatory
# viewcode adds links to highlighted source code
# MyST is a CommonMark parser that plugs into Sphinx. Enables you to write docs in md.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.doctest",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "myst_nb",
]


# Prefix document path to section labels, to use:
# `path/to/file:heading` instead of just `heading`
autosectionlabel_prefix_document = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Formats for MyST --------------------------------------------------------
source_suffix = [".rst", ".md"]

# --  Napoleon options--------------------------------------------------------
# use the :param directive
napoleon_use_param = True

# -- Autodoc options ---------------------------------------------------------

# Automatically extract typehints when specified and place them in
# descriptions of the relevant function/method.
autodoc_typehints = "both"

# Only insert class docstring
autoclass_content = "class"

# --  Intersphinx options-----------------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "xarray": ("https://docs.xarray.dev/en/stable/", None),
}

# --  MyST options------------------------------------------------------------

myst_enable_extensions = [
    "colon_fence",
    "deflist",
]

myst_heading_anchors = 3

# --  Todo options------------------------------------------------------------

todo_include_todos = True

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Myst-NB config
nb_execution_mode = "cache"
nb_execution_timeout = 600
