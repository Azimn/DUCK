from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_documentation_contract() -> None:
    root = Path(__file__).resolve().parents[1]
    subprocess.run(
        [sys.executable, str(root / "tools" / "check_docs.py")],
        cwd=root,
        check=True,
    )
