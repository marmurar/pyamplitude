import json

import pytest

from pyamplitude import AmplitudeCredentials


class FakeResponse:
    def __init__(self, status_code=200, json_data=None, text=None, content=None, headers=None):
        self.status_code = status_code
        self._json_data = json_data
        self.headers = headers or {}
        if content is not None:
            self.content = content
            self.text = text if text is not None else content.decode("utf-8", errors="replace")
        elif json_data is not None:
            self.text = text if text is not None else json.dumps(json_data)
            self.content = self.text.encode("utf-8")
        else:
            self.text = text or ""
            self.content = self.text.encode("utf-8")

    def json(self):
        if self._json_data is not None:
            return self._json_data
        return json.loads(self.text)


class RecordingTransport:
    def __init__(self, *responses):
        self.responses = list(responses or [FakeResponse(json_data={"ok": True})])
        self.requests = []

    def request(self, method, url, **kwargs):
        self.requests.append({"method": method, "url": url, **kwargs})
        if len(self.responses) > 1:
            return self.responses.pop(0)
        return self.responses[0]


@pytest.fixture
def credentials():
    return AmplitudeCredentials(api_key="api-key", secret_key="secret", project_name="demo", project_id=123)


@pytest.fixture
def transport():
    return RecordingTransport(FakeResponse(json_data={"data": {"ok": True}}))
