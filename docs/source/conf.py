project = "uPlaybook"
copyright = "2023, Sean Reifschneider"
author = "Sean Reifschneider"

extensions = [
    "m2r2",
    # "myst_parser",
    "sphinx.ext.autodoc",
]
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

templates_path = ["_templates"]
html_theme = "alabaster"  # or another theme of your choice
html_static_path = ["_static"]
exclude_patterns = []


def remove_taskdoc_tag(app, what, name, obj, options, lines):
    # Filter out lines that contain #taskdoc
    lines[:] = [line.replace("#taskdoc", "").strip() for line in lines]


def skip(app, what, name, obj, would_skip, options):
    if "#taskdoc" not in obj.__doc__:
        return True
    return would_skip


def setup(app):
    # app.connect("autodoc-skip-member", skip)
    app.connect("autodoc-process-docstring", remove_taskdoc_tag)
