Release Process
===============

Versioning
----------

Releases use semantic versioning and annotated Git tags:

.. code-block:: bash

   git switch develop
   git status -sb
   git tag -a v2.0.0 -m "Release v2.0.0"
   git push origin develop
   git push origin v2.0.0

The package version is defined in ``pyproject.toml``. The public package version
and ``pyamplitude.__version__`` should match the release tag without the leading
``v``.

Build Validation
----------------

Before publishing, run the same checks as CI:

.. code-block:: bash

   python -m pytest
   python -m sphinx -b html docs/source docs/_build/html
   python -m build --no-isolation
   python -m twine check dist/*

PyPI Description
----------------

PyPI renders the project description from ``README.md`` through the
``readme = "README.md"`` setting in ``pyproject.toml``. ``twine check`` must pass
before upload; otherwise PyPI may show an empty or ``UNKNOWN`` description.

Publishing
----------

Manual publishing with a PyPI API token:

.. code-block:: bash

   TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-... python -m twine upload dist/*

The repository also includes a ``Publish`` GitHub Actions workflow for PyPI
Trusted Publishing. To use it, configure the PyPI project as a trusted publisher
for ``marmurar/pyamplitude`` and publish a GitHub Release from the tag.
