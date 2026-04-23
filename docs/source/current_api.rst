Current Amplitude API Coverage
==============================

The rewrite follows the current public Amplitude documentation and separates
authentication style by API family.

Dashboard REST API
------------------

Dashboard endpoints use Basic Auth and live under ``/api/2`` for chart data.
``DashboardClient`` implements the high-use endpoints from the original project:

* active and new users
* session length distribution
* average session length
* average sessions per user
* user composition
* event segmentation
* event list
* user activity
* user search
* realtime active users
* retention
* funnels
* chart CSV download
* generic ``query()`` for unsupported Dashboard endpoints

Official reference:
https://www.docs.developers.amplitude.com/analytics/apis/dashboard-rest-api/

Export API
----------

``ExportClient`` downloads zipped JSON event exports for ``YYYYMMDDTHH`` ranges
and can parse the archive into Python dictionaries.

Official reference:
https://amplitude.com/docs/apis/analytics/export

Behavioral Cohorts API
----------------------

``CohortsClient`` supports the current list, asynchronous request/status/download,
upload and membership update flows.

Official reference:
https://amplitude.com/docs/apis/analytics/behavioral-cohorts

HTTP V2 API
-----------

``HTTPV2Client`` uploads one or more event payloads with ``api_key`` in the JSON
body. The ``identify()`` helper sends an ``$identify`` event. Request payloads
are built from ``AmplitudeEvent`` and optional ``UploadOptions`` objects.

Official reference:
https://amplitude.com/docs/apis/analytics/http-v2

Batch Event Upload API
----------------------

``BatchClient`` uses the Batch endpoint and the same event model as HTTP V2. It
is intended for higher-volume server-side ingestion and accepts the same
``UploadOptions`` structure.

Official reference:
https://amplitude.com/docs/apis/analytics/batch-event-upload

Regions
-------

The clients support ``region="US"`` and ``region="EU"``. EU endpoints use
Amplitude's EU domains for ingestion and analytics APIs.

Compatibility Surface
---------------------

The following legacy imports remain available as wrappers:

* ``pyamplitude.amplituderestapi.AmplitudeRestApi``
* ``pyamplitude.behavioralcohortsapi.BehavioralCohortsApi``
* ``pyamplitude.exportapi.AmplitudeExportApi``
* ``pyamplitude.projectshandler.ProjectsHandler``
* ``pyamplitude.apiresources.Segment``
* ``pyamplitude.apiresources.Event``

New code should prefer the newer client names, because they map directly to API
families and expose the offline-testable transport hook.
