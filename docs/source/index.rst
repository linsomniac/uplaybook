.. uPlaybook documentation master file, created by
   sphinx-quickstart on Thu Oct 26 08:21:23 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to uPlaybook's documentation!
=====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   fs


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

============
Introduction
============

uPlaybook is a Python-like declarative IT automation tool. It allows you to declare the desired state of a system via a Python playbook and associated templates/data.

This guide covers:

- The uPlaybook format
- How uPlaybook differs from Python
- Item loops in uPlaybook
- How uPlaybook differs from Ansible, Fabric, Shell, and Cookiecutter
- Installing uPlaybook
- Developing with uPlaybook

==================
The Playbook Format
==================

uPlaybook playbooks are written in Python but follow some specific conventions:

- Declare desired state rather than imperatively defining steps
- Tasks communicate if they changed something
- Changed tasks can trigger handlers
- Jinja2 templating with ``core.template()``
- Status output

Here is an example playbook:

.. code-block:: python

   import uplaybook

   def restart_service():
      uplaybook.core.service(name="nginx", state="restarted")

   uplaybook.fs.template(path="/etc/nginx/nginx.conf",
                         src="nginx.conf.j2").notify(restart_service)
