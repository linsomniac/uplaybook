html_theme = "alabaster"  # or another theme of your choice
extensions = [
    "m2r2",
    "sphinx.ext.autodoc",
]
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}


def skip(app, what, name, obj, would_skip, options):
    if "#taskdoc" not in obj.__doc__:
        return True
    return would_skip


def setup(app):
    app.connect("autodoc-skip-member", skip)
