from __future__ import annotations

import sys
from pathlib import Path

import pytest

UI_PATH = Path(__file__).resolve().parent.parent.parent / "ui"
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(UI_PATH) not in sys.path:
    sys.path.insert(0, str(UI_PATH))

from infra import check_service, load_services


# ── load_services ─────────────────────────────────────────────────────────────

def test_load_services_returns_list():
    services = load_services(REPO_ROOT / "infra" / "services.yaml")
    assert isinstance(services, list)
    assert len(services) > 0


def test_each_service_has_required_keys():
    services = load_services(REPO_ROOT / "infra" / "services.yaml")
    required = {"name", "role", "runtime", "health"}
    for svc in services:
        missing = required - svc.keys()
        assert not missing, f"Service {svc.get('name')} manque : {missing}"


def test_all_service_names_unique():
    services = load_services(REPO_ROOT / "infra" / "services.yaml")
    names = [s["name"] for s in services]
    assert len(names) == len(set(names)), "Noms de services dupliqués"


def test_health_type_is_known():
    services = load_services(REPO_ROOT / "infra" / "services.yaml")
    known = {"tcp", "http", "docker", "none"}
    for svc in services:
        htype = (svc.get("health") or {}).get("type", "none")
        assert htype in known, f"{svc['name']} : type healthcheck inconnu '{htype}'"


# ── classification statut ────────────────────────────────────────────────────

class TestCheckService:
    def _svc(self, htype, target):
        return {"name": "test", "health": {"type": htype, "target": target}}

    def test_tcp_up(self):
        result = check_service(
            self._svc("tcp", "localhost:9999"),
            tcp_fn=lambda h, p: ("up", 12.0),
        )
        assert result["status"] == "up"
        assert result["latency_ms"] == 12

    def test_tcp_down(self):
        result = check_service(
            self._svc("tcp", "localhost:9999"),
            tcp_fn=lambda h, p: ("down", 2001.0),
        )
        assert result["status"] == "down"

    def test_http_up(self):
        result = check_service(
            self._svc("http", "http://localhost:8000/health"),
            http_fn=lambda u: ("up", 55.0),
        )
        assert result["status"] == "up"
        assert result["latency_ms"] == 55

    def test_http_down(self):
        result = check_service(
            self._svc("http", "http://localhost:8000/health"),
            http_fn=lambda u: ("down", 2000.0),
        )
        assert result["status"] == "down"

    def test_docker_up(self):
        result = check_service(
            self._svc("docker", "my-container"),
            docker_fn=lambda c: ("up", 30.0),
        )
        assert result["status"] == "up"

    def test_docker_down(self):
        result = check_service(
            self._svc("docker", "my-container"),
            docker_fn=lambda c: ("down", 30.0),
        )
        assert result["status"] == "down"

    def test_no_healthcheck_returns_unknown(self):
        result = check_service({"name": "x", "health": {"type": "none", "target": None}})
        assert result["status"] == "unknown"

    def test_probe_exception_returns_unknown(self):
        def boom(h, p):
            raise RuntimeError("network error")

        result = check_service(
            self._svc("tcp", "localhost:9999"),
            tcp_fn=boom,
        )
        assert result["status"] == "unknown"

    def test_service_down_does_not_raise(self):
        result = check_service(
            self._svc("tcp", "localhost:1"),
            tcp_fn=lambda h, p: ("down", 2000.0),
        )
        assert result["status"] in {"up", "down", "unknown"}


# ── parsing services réels ────────────────────────────────────────────────────

def test_no_searxng_in_services():
    services = load_services(REPO_ROOT / "infra" / "services.yaml")
    names = [s["name"] for s in services]
    assert "searxng" not in names
    assert "searxng-local" not in names


def test_native_services_have_no_port_internal():
    services = load_services(REPO_ROOT / "infra" / "services.yaml")
    for svc in services:
        if svc.get("runtime") == "native":
            assert svc.get("port_internal") is None, (
                f"{svc['name']} (natif) ne doit pas avoir port_internal"
            )
