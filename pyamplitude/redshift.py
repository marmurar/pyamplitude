"""Optional Redshift helpers for historical Amplitude exports."""

import re
from typing import Any, Callable, Optional, Sequence

from .exceptions import ValidationError

ConnectFactory = Callable[..., Any]
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def validate_identifier(value: str, name: str) -> None:
    if not IDENTIFIER_RE.match(value):
        raise ValidationError(f"{name} must be a safe SQL identifier.")


class RedshiftClient:
    """Small optional Redshift client.

    ``psycopg2`` is imported only when a real connection is needed, so the base
    package remains usable without Redshift dependencies.
    """

    def __init__(
        self,
        *,
        host: str,
        user: str,
        port: int,
        password: str,
        dbname: str,
        schema: str,
        table: str = "events",
        connect_factory: Optional[ConnectFactory] = None,
    ) -> None:
        validate_identifier(schema, "schema")
        validate_identifier(table, "table")
        self.host = host
        self.user = user
        self.port = port
        self.password = password
        self.dbname = dbname
        self.schema = schema
        self.table = table
        self.connect_factory = connect_factory

    def _connect(self) -> Any:
        if self.connect_factory is not None:
            return self.connect_factory(
                host=self.host,
                user=self.user,
                port=self.port,
                password=self.password,
                dbname=self.dbname,
            )
        import psycopg2  # type: ignore

        return psycopg2.connect(
            host=self.host,
            user=self.user,
            port=self.port,
            password=self.password,
            dbname=self.dbname,
        )

    def execute_query(self, query: str, params: Optional[Sequence[Any]] = None) -> list:
        if not query:
            raise ValidationError("query is required.")
        connection = self._connect()
        cursor = connection.cursor()
        try:
            cursor.execute(query, tuple(params or ()))
            return list(cursor.fetchall())
        finally:
            cursor.close()
            close = getattr(connection, "close", None)
            if close is not None:
                close()

    def count_active_users(self, date: str) -> int:
        query = f"SELECT COUNT(DISTINCT amplitude_id) FROM {self.schema}.{self.table} WHERE DATE(event_time) = %s;"
        return int(self.execute_query(query, [date])[0][0])

    def count_specific_user_events(self, *, date: str, event_type: str) -> int:
        query = f"""
            SELECT COUNT(DISTINCT amplitude_id)
            FROM {self.schema}.{self.table}
            WHERE event_type = %s AND DATE(event_time) = %s;
        """
        return int(self.execute_query(query, [event_type, date])[0][0])

    def list_users(self, *, date: str) -> list:
        query = f"SELECT DISTINCT user_id FROM {self.schema}.{self.table} WHERE DATE(event_time) = %s;"
        return [row[0] for row in self.execute_query(query, [date])]


class AmplitudeRedshift(RedshiftClient):
    """Backward-compatible Redshift class."""

    def __init__(
        self,
        host: str = "",
        user: str = "",
        port: int = 5439,
        password: str = "",
        dbname: str = "",
        schema: str = "public",
        table: str = "events",
        show_logs: bool = True,
        connect_factory: Optional[ConnectFactory] = None,
    ) -> None:
        super().__init__(
            host=host,
            user=user,
            port=port,
            password=password,
            dbname=dbname,
            schema=schema,
            table=table,
            connect_factory=connect_factory,
        )

    def count_redshift_active_users(self, date: str, schema: str = "", table: str = "") -> int:
        if schema:
            validate_identifier(schema, "schema")
            self.schema = schema
        if table:
            validate_identifier(table, "table")
            self.table = table
        return self.count_active_users(date)

    def get_a_list_of_users(self, date: str, schema: str = "", table: str = "") -> list:
        if schema:
            validate_identifier(schema, "schema")
            self.schema = schema
        if table:
            validate_identifier(table, "table")
            self.table = table
        return self.list_users(date=date)
