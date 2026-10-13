"""Offline CLI, migration and snapshot smoke test using a disposable database."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from job_application.dashboard import DASHBOARD_SOURCES
from job_application.tracking import Tracker


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    with TemporaryDirectory(prefix="job-application-smoke-") as temporary:
        database_url = f"sqlite:///{Path(temporary) / 'smoke.db'}"
        environment = {**os.environ, "JOB_APPLICATION_DATABASE_URL": database_url}
        help_result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from job_application.cli import main; raise SystemExit(main())",
                "--help",
            ],
            cwd=root,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )
        if "usage: job-application" not in help_result.stdout:
            raise RuntimeError("CLI did not return its help text")
        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=root,
            env=environment,
            check=True,
        )
        tracker = Tracker(database_url, DASHBOARD_SOURCES)
        try:
            tracker.bootstrap(root / "frontend/app/jobs.ts")
            data = tracker.dashboard()
            if not isinstance(data["jobs"], list):
                raise RuntimeError("Dashboard did not return a jobs list")
            if any(job["personal"]["notes"] for job in data["jobs"]):
                raise RuntimeError("Public snapshot unexpectedly imported personal notes")
        finally:
            tracker.engine.dispose()
    print("Smoke test passed")


if __name__ == "__main__":
    main()
