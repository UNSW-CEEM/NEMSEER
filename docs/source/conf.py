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
copyright = "2023, Abhijith (Abi) Prakash"
author = "Abhijith (Abi) Prakash"

# The full version, including alpha/beta/rc tags
release = "1.0.6"


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

html_theme_options = {
    "footer_icons": [
        {
            "name": "CC",
            "url": "https://creativecommons.org/licenses/by/4.0/",
            "html": """
            <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 24 24" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
            <path d="M20.354 6.479a10.021 10.021 0 0 0-7.421-4.429c-3.108-.294-6.031.771-8.123 2.963C3.533 6.35 2.699 7.839 2.21 9.66c-.217.805-.247 1.104-.244 2.396.002 1.293.034 1.599.255 2.432a10.232 10.232 0 0 0 7.451 7.332c.315.078.702.16.859.182.696.097 2.381.056 3.131-.075 3.088-.538 5.832-2.531 7.24-5.258 1.644-3.181 1.426-7.222-.548-10.19zm-.41 7.688c-.808 2.99-3.263 5.272-6.361 5.912-4.831.997-9.538-2.658-9.839-7.641-.194-3.217 1.755-6.446 4.745-7.863 1.133-.536 2.045-.733 3.425-.738 1.327-.004 2.064.132 3.223.596 2.324.931 4.146 3.04 4.816 5.573.281 1.06.276 3.103-.009 4.161z"></path><path d="M8.042 14.955c-.915-.324-1.616-1.275-1.74-2.36-.183-1.607.422-2.856 1.654-3.415.669-.303 1.882-.296 2.603.016.438.19 1.261.933 1.261 1.139 0 .033-.284.201-.631.372l-.632.312-.337-.337c-.187-.188-.475-.363-.649-.396-.433-.082-.952.111-1.187.44-.389.546-.415 1.972-.048 2.533.191.291.512.494.813.518.635.05.796-.006 1.172-.401l.379-.398.488.269c.269.148.527.305.575.347.164.148-.592.92-1.199 1.224-.517.259-.679.293-1.358.286-.425-.006-.949-.074-1.164-.149zm5.816 0c-.901-.32-1.591-1.241-1.739-2.325-.215-1.569.419-2.888 1.654-3.45.717-.324 1.934-.3 2.661.056.45.221 1.201.911 1.201 1.104 0 .034-.295.203-.654.377l-.654.317-.341-.37c-.304-.332-.385-.369-.802-.369-.576 0-.945.225-1.145.698-.18.423-.201 1.461-.043 1.934.324.961 1.505 1.188 2.175.419l.304-.346.58.294c.32.161.582.319.582.352 0 .219-.75.918-1.256 1.17-.517.259-.679.293-1.358.287-.425-.005-.949-.073-1.165-.148z"></path>
            </svg>
            """,
            "class": "",
        },
        {
            "name": "BY",
            "url": "https://creativecommons.org/licenses/by/4.0/",
            "html": """
            <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 496 512" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
            <path d="M314.9 194.4v101.4h-28.3v120.5h-77.1V295.9h-28.3V194.4c0-4.4 1.6-8.2 4.6-11.3 3.1-3.1 6.9-4.7 11.3-4.7H299c4.1 0 7.8 1.6 11.1 4.7 3.1 3.2 4.8 6.9 4.8 11.3zm-101.5-63.7c0-23.3 11.5-35 34.5-35s34.5 11.7 34.5 35c0 23-11.5 34.5-34.5 34.5s-34.5-11.5-34.5-34.5zM247.6 8C389.4 8 496 118.1 496 256c0 147.1-118.5 248-248.4 248C113.6 504 0 394.5 0 256 0 123.1 104.7 8 247.6 8zm.8 44.7C130.2 52.7 44.7 150.6 44.7 256c0 109.8 91.2 202.8 203.7 202.8 103.2 0 202.8-81.1 202.8-202.8.1-113.8-90.2-203.3-202.8-203.3z"></path>
            </svg>
            """,
            "class": "",
        },
        {
            "name": "GitHub",
            "url": "https://github.com/UNSW-CEEM/NEMSEER",
            "html": """
            <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
            </svg>
            """,
            "class": "",
        },
    ],
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Myst-NB config
nb_execution_mode = "cache"
nb_execution_timeout = 600
