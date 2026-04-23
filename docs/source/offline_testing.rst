Offline Testing
===============

Real API keys are not required to develop or test the package.

Every client accepts a custom transport object:

.. code-block:: python

   class Transport:
       def request(self, method, url, **kwargs):
           ...

Tests can assert the exact request without touching the network:

.. code-block:: python

   from pyamplitude import AmplitudeCredentials, DashboardClient

   credentials = AmplitudeCredentials(api_key="key", secret_key="secret")
   client = DashboardClient(credentials, transport=fake_transport)

   client.active_users(start="20240101", end="20240101")

The standard test suite uses this pattern for request construction, response
parsing, validation and error handling.

Run tests with coverage:

.. code-block:: bash

   python -m pytest

The local coverage gate is configured in ``pyproject.toml`` and currently
requires at least 95% total coverage. The generated ``coverage.xml`` file is what
the GitHub Actions workflow uploads to Codecov.

Run only the Sphinx documentation build:

.. code-block:: bash

   python -m sphinx -b html docs/source docs/_build/html

Run a package build locally:

.. code-block:: bash

   python -m build --no-isolation

Integration tests should be marked explicitly:

.. code-block:: python

   import os
   import pytest

   pytestmark = pytest.mark.integration

   @pytest.mark.skipif(
       not os.getenv("AMPLITUDE_API_KEY"),
       reason="Amplitude credentials are not configured",
   )
   def test_real_api():
       ...

Expected optional variables:

* ``AMPLITUDE_API_KEY``
* ``AMPLITUDE_SECRET_KEY``
* ``AMPLITUDE_PROJECT_ID``

CI and Codecov
--------------

The CI workflow runs tests on Python 3.9, 3.10, 3.11 and 3.12. The Python 3.12
job uploads coverage to Codecov. Sphinx is built in a separate docs job so API
reference generation fails fast when public objects or imports break.
