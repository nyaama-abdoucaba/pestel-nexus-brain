from __future__ import annotations

import socket
import subprocess
import time
from pathlib import Path
from typing import Any, Callable

import yaml

_DEFAULT_SERVICES_PATH = Path(__file__).resolve().parent.parent / "infra" / "services.yaml"


def load_services(path: Path = _DEFAULT_SERVICES_PATH) -> list[dict[str, Any]]:
    with open(path) as fh:
        data = yaml.safe_load(fh)
    return data.get("services", [])


# ── Sondes bas niveau ────────────────────────────────────────────────────────

def probe_tcp(host: str, port: int, timeout: float = 2.0) -> tuple[str, float]:
    """Retourne ('up'|'down', latence_ms). Ne lève jamais."""
    t0 = time.monotonic()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            pass
        return "up", (time.monotonic() - t0) * 1000
    except OSError:
        return "down", (time.monotonic() - t0) * 1000


def probe_http(url: str, timeout: float = 2.0) -> tuple[str, float]:
    """Retourne ('up'|'down', latence_ms). Ne lève jamais."""
    import urllib.request
    import urllib.error

    t0 = time.monotonic()
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            _ = resp.read(64)
        return "up", (time.monotonic() - t0) * 1000
    except Exception:
        return "down", (time.monotonic() - t0) * 1000


def probe_docker(container: str, timeout: float = 2.0) -> tuple[str, float]:
    """Vérifie qu'un conteneur est en état 'running' via docker inspect."""
    t0 = time.monotonic()
    try:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Status}}", container],
            capture_output=True, text=True, timeout=timeout,
        )
        status = result.stdout.strip()
        elapsed = (time.monotonic() - t0) * 1000
        return ("up" if status == "running" else "down"), elapsed
    except Exception:
        return "down", (time.monotonic() - t0) * 1000


# ── Agrégateur ───────────────────────────────────────────────────────────────

def check_service(
    svc: dict[str, Any],
    tcp_fn: Callable = probe_tcp,
    http_fn: Callable = probe_http,
    docker_fn: Callable = probe_docker,
) -> dict[str, Any]:
    """
    Retourne dict avec keys : status ('up'|'down'|'unknown'), latency_ms, detail.
    Ne lève jamais.
    """
    health = svc.get("health") or {}
    htype = health.get("type", "none")
    target = health.get("target")

    try:
        if htype == "tcp" and target:
            host, _, port_str = target.rpartition(":")
            status, ms = tcp_fn(host, int(port_str))
            return {"status": status, "latency_ms": round(ms), "detail": target}

        if htype == "http" and target:
            status, ms = http_fn(target)
            return {"status": status, "latency_ms": round(ms), "detail": target}

        if htype == "docker" and target:
            status, ms = docker_fn(target)
            return {"status": status, "latency_ms": round(ms), "detail": f"container:{target}"}

    except Exception as exc:
        return {"status": "unknown", "latency_ms": None, "detail": str(exc)}

    return {"status": "unknown", "latency_ms": None, "detail": "no healthcheck"}


# ── Logs Docker ───────────────────────────────────────────────────────────────

def docker_logs(container: str, tail: int = 30, timeout: float = 4.0) -> str:
    """Retourne les N dernières lignes de logs. Jamais bloquant, jamais mutant."""
    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", str(tail), container],
            capture_output=True, text=True, timeout=timeout,
        )
        return (result.stdout + result.stderr).strip()
    except Exception as exc:
        return f"(erreur lecture logs : {exc})"
