from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from duck.continuity_campaign import CharacterOrigin, ExternalJsonlCondition


FIXTURE = Path(__file__).resolve().parents[1] / "evaluation" / "fixtures" / "pretorius_origin_v1.json"
ROOT = Path(__file__).resolve().parents[1]


def test_external_jsonl_condition_handshake_and_response(tmp_path):
    script = tmp_path / "fake_external.py"
    script.write_text(
        """
import json, sys

def send(value):
    print(json.dumps(value), flush=True)

hello = json.loads(sys.stdin.readline())
send({
    'ok': True,
    'protocol': hello['protocol'],
    'origin_digest': hello['origin_digest'],
    'model_id': hello['model_id'],
})
for line in sys.stdin:
    request = json.loads(line)
    if request['op'] == 'respond':
        send({'ok': True, 'response_text': 'external:' + request['text'], 'public_trace': {'seen': True}})
    elif request['op'] == 'close':
        send({'ok': True})
        break
""".strip()
        + "\n",
        encoding="utf-8",
    )
    origin = CharacterOrigin.load(FIXTURE)
    condition = ExternalJsonlCondition(
        [sys.executable, str(script)],
        origin,
        condition_id="wayfarer",
        model_id="shared-model",
        root=tmp_path / "state",
    )
    result = condition.respond("Hello.", speaker="Jay")
    condition.close()
    assert result.response_text == "external:Hello."
    assert result.public_trace == {"seen": True}


def test_wayfarer_bridge_cli_accepts_positional_source_argument():
    completed = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "wayfarer_duckhunter_bridge.py"), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0
    assert "source" in completed.stdout
    assert "--source" not in completed.stdout
