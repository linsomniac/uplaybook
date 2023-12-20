# Welcome to uPlaybook

## Introduction

uPlaybook is a Python-like declarative IT automation tool. It allows you to declare
the desired state of a project or system via a Python playbook and associated templates/data.

This guide covers:

- Installing uPlaybook
- Running uPlaybook
- Making your own playbooks
- Developing new tasks

## The Playbook Format

uPlaybook playbooks are written in Python but follow some specific conventions:

- Declare desired state rather than imperatively defining steps
- Tasks communicate if they changed something
- Changed tasks can trigger handlers
- Jinja2 templating of many argument values
- Status output

To get started, see the [Getting Started Guide](getting_started.md)

<!-- vim: set tw=90: -->
