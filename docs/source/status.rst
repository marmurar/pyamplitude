Project Status
==============

Badges
------

.. list-table::
   :header-rows: 1

   * - Badge
     - Purpose
     - Source
   * - CI
     - Runs unit tests, coverage and Sphinx builds on supported Python versions.
     - https://github.com/marmurar/pyamplitude/actions/workflows/ci.yml
   * - Codecov
     - Publishes coverage from ``coverage.xml`` and enforces project/patch targets.
     - https://codecov.io/gh/marmurar/pyamplitude
   * - Git tag
     - Shows the latest repository tag, even when there is no GitHub Release object.
     - https://github.com/marmurar/pyamplitude/tags
   * - PyPI version
     - Shows the latest published package version.
     - https://pypi.org/project/pyamplitude/
   * - Python versions
     - Shows supported Python versions from package metadata.
     - https://pypi.org/project/pyamplitude/
   * - MIT license
     - Links to the repository license.
     - https://github.com/marmurar/pyamplitude/blob/develop/LICENSE.txt

Branches
--------

The active development branch is ``develop``. The ``master`` branch should only
be updated intentionally when changes are ready to promote.

Release tags use the ``vX.Y.Z`` format, for example ``v2.0.0``.

Codecov
-------

Codecov is configured in ``codecov.yml``:

* project target: 95%
* patch target: 90%
* coverage upload: GitHub Actions ``CI`` workflow

The local test command also enforces 95% total coverage:

.. code-block:: bash

   python -m pytest

CI Workflow
-----------

The workflow runs on pushes to ``develop``, ``master``, ``main`` and ``v*`` tags,
and on pull requests. It tests Python 3.9 through 3.12 and builds the Sphinx
documentation.

Publishing
----------

The ``Publish`` workflow builds distributions and uploads them to PyPI through
Trusted Publishing when a GitHub Release is published. Manual Twine publishing is
also supported; in both cases ``twine check dist/*`` should pass before upload.
