def test_legacy_import_paths():
    from pyamplitude.apiresources import Event, ProjectsHandler, Segment
    from pyamplitude.amplituderedshift import AmplitudeRedshift
    from pyamplitude.amplituderestapi import AmplitudeRestApi
    from pyamplitude.behavioralcohortsapi import BehavioralCohortsApi
    from pyamplitude.exportapi import AmplitudeExportApi
    from pyamplitude.projectshandler import AmplitudeCredentials

    assert ProjectsHandler
    assert Segment
    assert Event
    assert AmplitudeRestApi
    assert BehavioralCohortsApi
    assert AmplitudeExportApi
    assert AmplitudeRedshift
    assert AmplitudeCredentials
