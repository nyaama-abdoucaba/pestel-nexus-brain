import json
import logging
import sys


def log_json(logger: logging.Logger, level: str, event: str, **payload) -> None:
    message = json.dumps(
        {"event": event, **payload},
        ensure_ascii=False,
        default=str,
    )
    getattr(logger, level)(message)


def configure_application_logging(level_name: str = "INFO") -> None:
    level = getattr(logging, str(level_name or "INFO").upper(), logging.INFO)
    root = logging.getLogger()

    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        root.addHandler(handler)

    root.setLevel(level)
