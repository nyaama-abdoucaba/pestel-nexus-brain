import os
from pathlib import Path


TEST_DATA_HOME = Path("/tmp/pestel-nexus-brain-test-data")
TEST_DATA_HOME.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("XDG_DATA_HOME", str(TEST_DATA_HOME))
os.environ.setdefault("OTEL_SDK_DISABLED", "true")
