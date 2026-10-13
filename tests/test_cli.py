from pathlib import Path

from sqlalchemy import create_engine, inspect

from job_application.cli import main


def test_init_db_command(tmp_path: Path, capsys: object) -> None:
    del capsys
    database_path = tmp_path / "cli.db"
    database_url = f"sqlite:///{database_path}"

    assert main(["init-db", "--database-url", database_url]) == 0

    engine = create_engine(database_url)
    try:
        assert "jobs" in inspect(engine).get_table_names()
    finally:
        engine.dispose()
