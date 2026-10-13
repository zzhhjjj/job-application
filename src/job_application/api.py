"""Loopback-only API for the local dashboard; Vite forwards /api/radar here."""

# ruff: noqa: RUF001 -- Chinese UI messages intentionally use Chinese punctuation.

from __future__ import annotations

import asyncio
import json
import threading
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from job_application.dashboard import DASHBOARD_SOURCES
from job_application.preferences import load_company_tiers
from job_application.tracking import RefreshBusy, RevisionConflict, Tracker

PREFIX = "/api/radar"
ALLOWED_ORIGINS = {"http://localhost:3000", "http://127.0.0.1:3000"}


class PersonalPatch(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    revision: int = Field(ge=0)
    favorite: bool | None = None
    stage: Literal["pending", "interested", "applied", "ignored"] | None = None
    notes: str | None = Field(default=None, max_length=10000)


class ReviewPatch(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    eventId: int = Field(ge=0)


class RadarServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(
        self,
        tracker: Tracker,
        output: Path,
        port: int = 8765,
        *,
        company_tiers_path: Path = Path(".local/company-tiers.json"),
    ) -> None:
        self.company_tiers_path = company_tiers_path.resolve()
        self.tracker = tracker
        self.output = output
        self.refresh_thread: threading.Thread | None = None
        self.refresh_guard = threading.Lock()
        self.refresh_error: str | None = None
        super().__init__(("127.0.0.1", port), RadarHandler)

    def start_refresh(self) -> None:
        with self.refresh_guard:
            if self.refresh_thread and self.refresh_thread.is_alive():
                raise RefreshBusy()
            if self.tracker.refresh_in_progress():
                raise RefreshBusy()
            self.refresh_error = None

            def run() -> None:
                try:
                    asyncio.run(self.tracker.refresh(self.output, date.today()))
                except Exception as exc:
                    self.refresh_error = f"{type(exc).__name__}: {exc}"
                    print(f"Dashboard refresh failed: {exc}", flush=True)

            self.refresh_thread = threading.Thread(target=run, daemon=True)
            self.refresh_thread.start()


class RadarHandler(BaseHTTPRequestHandler):
    server: RadarServer

    def reply(self, status: int, payload: Any) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def dispatch(self, mutate: bool = False) -> None:
        # No CORS; protect localhost writes from arbitrary websites and DNS rebinding.
        host = urlsplit("http://" + self.headers.get("Host", "")).hostname
        if host not in {"localhost", "127.0.0.1"}:
            self.reply(403, {"error": "Invalid local host"})
            return
        if mutate and (
            self.headers.get("Origin") not in ALLOWED_ORIGINS
            or self.headers.get_content_type() != "application/json"
        ):
            self.reply(403, {"error": "请从本地 dashboard 保存操作"})
            return
        path = urlsplit(self.path).path
        tracker = self.server.tracker
        try:
            if not mutate:
                if path == PREFIX:
                    refreshing = tracker.refresh_in_progress()
                    data = tracker.dashboard()
                    data["refreshing"] = refreshing or bool(
                        self.server.refresh_thread and self.server.refresh_thread.is_alive()
                    )
                    data["refreshError"] = self.server.refresh_error
                    data["companyTiers"] = load_company_tiers(
                        self.server.company_tiers_path,
                        {source.config.company_name for source in DASHBOARD_SOURCES},
                    )
                    self.reply(200, data)
                    return
                if path.startswith(PREFIX + "/jobs/") and path.endswith("/history"):
                    job_id = path.removeprefix(PREFIX + "/jobs/").removesuffix("/history")
                    self.reply(200, tracker.history(job_id))
                    return
            else:
                length = int(self.headers.get("Content-Length", "0"))
                if length < 1 or length > 100000:
                    self.reply(413, {"error": "请求大小无效"})
                    return
                body = json.loads(self.rfile.read(length))
                if path == PREFIX + "/refresh":
                    self.server.start_refresh()
                    self.reply(202, {"refreshing": True})
                    return
                if path == PREFIX + "/reviewed":
                    review = ReviewPatch.model_validate(body)
                    tracker.mark_reviewed(review.eventId)
                    self.reply(200, {"ok": True})
                    return
                if path.startswith(PREFIX + "/jobs/"):
                    patch = PersonalPatch.model_validate(body)
                    values = patch.model_dump(
                        exclude={"revision"}, exclude_unset=True, exclude_none=True
                    )
                    if not values:
                        raise ValueError("至少修改一个个人状态字段")
                    job_id = path.removeprefix(PREFIX + "/jobs/")
                    self.reply(200, tracker.save_personal(job_id, patch.revision, values))
                    return
            self.reply(404, {"error": "Not found"})
        except KeyError:
            self.reply(404, {"error": "岗位不存在"})
        except RevisionConflict:
            self.reply(
                409,
                {"error": "此岗位已在另一页面更新。已重新载入状态，请核对后重试；备注草稿保留。"},
            )
        except RefreshBusy:
            self.reply(409, {"error": "已有刷新正在运行"})
        except (ValidationError, ValueError):
            self.reply(400, {"error": "请求字段无效，请检查状态、版本或备注长度"})
        except Exception as exc:
            print(f"Dashboard API error: {exc}", flush=True)
            self.reply(500, {"error": "本地存储操作失败，尚未确认保存，请重试"})

    def do_GET(self) -> None:
        self.dispatch()

    def do_POST(self) -> None:
        self.dispatch(mutate=True)


def serve(output: Path, port: int) -> None:
    tracker = Tracker()
    tracker.bootstrap(output)
    tracker.refresh_in_progress()
    server = RadarServer(tracker, output, port)
    print(f"Role Radar API: http://127.0.0.1:{server.server_port}{PREFIX}", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()
        tracker.engine.dispose()
