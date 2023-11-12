# Installing

## Via PIP

Typically you are able to install uPlaybook by running: `python3 -m pip install uplaybook`

## Git clone / Developing

To directly use the version from github, either for trying it without installing or if
you are developing uPlaybook:

    git clone git@github.com:linsomniac/uplaybook.git
    cd uplaybook
    python3 -m pip install poetry
    poetry install
    poetry shell

That will place you in a sub-shell that is configured for running uPlaybook, run `up` to get
started.

If you are doing full development, you will probably also want to set up pre-commit:

    python3 -m pip install pre-commit
    pre-commit install
    pre-commit run

<!-- vim: set tw=90: -->
