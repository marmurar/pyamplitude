Quickstart
==========

Install the package:

.. code-block:: bash

   pip install pyamplitude

Create credentials for Basic Auth APIs:

.. code-block:: python

   from pyamplitude import AmplitudeCredentials

   credentials = AmplitudeCredentials(api_key="key", secret_key="secret")

Dashboard REST queries:

.. code-block:: python

   from pyamplitude import DashboardClient, Segment

   client = DashboardClient(credentials)
   segment = Segment.user_property("country", "is", ["Uruguay"])

   data = client.active_users(
       start="20240101",
       end="20240131",
       segments=[segment],
       group_by="country",
   )

HTTP V2 ingestion:

.. code-block:: python

   from pyamplitude import AmplitudeEvent, HTTPV2Client
   from pyamplitude.ingestion import make_ingestion_credentials

   client = HTTPV2Client(make_ingestion_credentials("key"))
   client.upload([AmplitudeEvent("Signup", user_id="user-123")])

Export API:

.. code-block:: python

   from pyamplitude import ExportClient

   events = ExportClient(credentials).export_events(
       start="20240101T00",
       end="20240101T23",
   )

Behavioral Cohorts:

.. code-block:: python

   from pyamplitude import CohortsClient

   client = CohortsClient(credentials)
   job = client.request_cohort("cohort-id", include_properties=True)
   status = client.request_status(job["request_id"])
   archive = client.download_cohort(job["request_id"])
