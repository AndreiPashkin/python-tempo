============
Installation
============

Python
======
Just use PIP::

    pip install python-tempo

PostgreSQL
==========
1) Install PostgreSQL flavor of the library in the Python environment,
   that your PostgreSQL instance uses, so PL/Python stored procedures would be
   able to `import tempo`::

     pip install python-tempo[postgresql]

2) Ensure, that PL/Python language is available for you in your
   PostgreSQL instance (see details `here
   <http://www.postgresql.org/docs/9.4/static/plpython.html>`_).

3) After installing Python egg, you will be able to execute such commands:
   ``python -m tempo.postgresql.install`` and
   ``python -m tempo.postgresql.uninstall``.
   They will output to stdout installation and uninstallation SQL scripts
   respectively. Feed them to ``psql``, to perform needed operation. On Unix it
   can look like this::

       python -m tempo.postgresql.install | sudo -u postgres psql -d my_databse

Django
======
Perform steps for PostgreSQL.

Django-REST-Framework
=====================
Perform steps for Python or PostgreSQL.
