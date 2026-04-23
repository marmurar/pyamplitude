import pytest
import sys
import types

from pyamplitude import AmplitudeRedshift, RedshiftClient
from pyamplitude.exceptions import ValidationError


class Cursor:
    def __init__(self, rows):
        self.rows = rows
        self.executed = []
        self.closed = False

    def execute(self, query, params):
        self.executed.append((query, params))

    def fetchall(self):
        return self.rows

    def close(self):
        self.closed = True


class Connection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.closed = False

    def cursor(self):
        return self._cursor

    def close(self):
        self.closed = True


def test_redshift_executes_queries_with_factory():
    cursor = Cursor([(3,)])
    connection = Connection(cursor)

    def connect_factory(**kwargs):
        assert kwargs["dbname"] == "db"
        return connection

    client = RedshiftClient(
        host="host",
        user="user",
        port=5439,
        password="pw",
        dbname="db",
        schema="app123",
        table="events",
        connect_factory=connect_factory,
    )

    assert client.execute_query("SELECT 1", [1]) == [(3,)]
    assert cursor.executed == [("SELECT 1", (1,))]
    assert cursor.closed is True
    assert connection.closed is True


def test_redshift_helpers_and_legacy_wrapper():
    cursor = Cursor([(7,), ("u1",), ("u2",)])
    connection = Connection(cursor)
    client = AmplitudeRedshift(
        host="host",
        user="user",
        password="pw",
        dbname="db",
        schema="app123",
        table="events",
        connect_factory=lambda **kwargs: connection,
    )

    assert client.count_redshift_active_users("2024-01-01") == 7
    assert client.count_specific_user_events(date="2024-01-01", event_type="Signup") == 7
    assert client.count_redshift_active_users("2024-01-01", schema="app123") == 7
    assert client.get_a_list_of_users("2024-01-01") == [7, "u1", "u2"]
    assert client.get_a_list_of_users("2024-01-01", schema="app456", table="events") == [7, "u1", "u2"]
    assert "app456.events" in cursor.executed[-1][0]


def test_redshift_validates_sql_inputs():
    with pytest.raises(ValidationError):
        RedshiftClient(
            host="h",
            user="u",
            port=5439,
            password="p",
            dbname="d",
            schema="bad-schema",
            table="events",
            connect_factory=lambda **kwargs: None,
        )

    client = RedshiftClient(
        host="h",
        user="u",
        port=5439,
        password="p",
        dbname="d",
        schema="public",
        table="events",
        connect_factory=lambda **kwargs: None,
    )

    with pytest.raises(ValidationError):
        client.execute_query("")


def test_redshift_imports_psycopg2_when_no_factory(monkeypatch):
    cursor = Cursor([(1,)])
    connection = Connection(cursor)
    module = types.SimpleNamespace(connect=lambda **kwargs: connection)
    monkeypatch.setitem(sys.modules, "psycopg2", module)
    client = RedshiftClient(
        host="h",
        user="u",
        port=5439,
        password="p",
        dbname="d",
        schema="public",
        table="events",
    )

    assert client.execute_query("SELECT 1") == [(1,)]
