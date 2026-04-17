from sqlalchemy import inspect, text

from database import engine


def ensure_database_schema() -> None:
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    if "users" not in tables:
        return

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    statements: list[str] = []

    if "password_hash" not in user_columns:
        statements.append(
            "ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) DEFAULT ''"
        )

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
