#!/usr/bin/env python3
"""JSONL bridge that lets Duckhunter evaluate a frozen Wayfarer checkout fairly.

The bridge does not modify Wayfarer. It installs Wayfarer's public external
expression renderer around the same OpenAI-compatible completion port used by
DUCK, verifies the frozen Pretorius cartridge, and rejects silent renderer
fallback before returning a scored response.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from duck.continuity_campaign import PROTOCOL_VERSION
from duck.language import OpenAICompatiblePort


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _emit(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
    sys.stdout.flush()


def _read() -> dict[str, Any] | None:
    line = sys.stdin.readline()
    if not line:
        return None
    return dict(json.loads(line))


def _load_wayfarer(source: Path):
    if not source.exists():
        raise FileNotFoundError(f"Wayfarer source root does not exist: {source}")
    sys.path.insert(0, str(source))
    from persona_engine.agent import CharacterAgent
    from persona_engine.core.external_renderer import ExternalChatRenderer

    return CharacterAgent, ExternalChatRenderer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Duckhunter bridge for a frozen Wayfarer checkout")
    parser.add_argument("--source", type=Path, required=True, help="Wayfarer repository source root containing persona_engine")
    parser.add_argument("--cartridge", type=Path, help="Pretorius cartridge path; defaults inside --source")
    parser.add_argument("--temperature", type=float, default=0.78)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source = args.source.expanduser().resolve()
    cartridge = (
        args.cartridge.expanduser().resolve()
        if args.cartridge is not None
        else source / "persona_engine" / "cartridges" / "pretorius.snp"
    )

    try:
        CharacterAgent, ExternalChatRenderer = _load_wayfarer(source)
    except Exception as exc:
        _emit({"ok": False, "error": f"wayfarer_import_failed:{type(exc).__name__}:{exc}"})
        return 2

    hello = _read()
    if hello is None:
        return 0
    if hello.get("op") != "hello" or hello.get("protocol") != PROTOCOL_VERSION:
        _emit({"ok": False, "error": "invalid_handshake"})
        return 2

    origin = hello.get("origin")
    if not isinstance(origin, dict):
        _emit({"ok": False, "error": "missing_origin"})
        return 2
    origin_digest = str(hello.get("origin_digest", ""))
    model_id = str(hello.get("model_id", "")).strip()
    if not model_id:
        _emit({"ok": False, "error": "missing_model_id"})
        return 2

    expected_cartridge_sha = str(origin.get("source", {}).get("wayfarer_cartridge_sha256", ""))
    if not cartridge.exists():
        _emit({"ok": False, "error": f"cartridge_missing:{cartridge}"})
        return 2
    actual_cartridge_sha = _sha256(cartridge)
    if not expected_cartridge_sha or actual_cartridge_sha != expected_cartridge_sha:
        _emit(
            {
                "ok": False,
                "error": "frozen_cartridge_mismatch",
                "expected_sha256": expected_cartridge_sha,
                "actual_sha256": actual_cartridge_sha,
            }
        )
        return 2

    state_root = Path(str(hello.get("root", "."))).expanduser().resolve()
    state_root.mkdir(parents=True, exist_ok=True)
    db_path = state_root / "wayfarer_state.sqlite3"

    port = OpenAICompatiblePort.from_env()
    if port.model != model_id:
        _emit({"ok": False, "error": "shared_model_mismatch", "port_model": port.model, "requested_model": model_id})
        return 2

    def shared_chat(messages):
        return port.complete(messages, temperature=float(args.temperature))

    renderer = ExternalChatRenderer(
        shared_chat,
        provider_name="duckhunter-shared-openai-compatible",
        model_name=model_id,
    )
    agent = CharacterAgent(
        cartridge_path=str(cartridge),
        user_id=f"duckhunter-{origin_digest[:12]}",
        db_path=str(db_path),
    )
    agent.set_renderer(renderer)

    _emit(
        {
            "ok": True,
            "protocol": PROTOCOL_VERSION,
            "origin_digest": origin_digest,
            "model_id": model_id,
            "cartridge_sha256": actual_cartridge_sha,
            "renderer_status": agent.engine.renderer_status(),
        }
    )

    while True:
        request = _read()
        if request is None:
            break
        op = request.get("op")
        if op == "close":
            try:
                agent.engine.persistence.close()
            finally:
                _emit({"ok": True})
            break
        if op != "respond":
            _emit({"ok": False, "error": f"unsupported_op:{op}"})
            continue

        speaker = str(request.get("speaker", "Jay"))
        if speaker != "Jay":
            _emit({"ok": False, "error": "wayfarer_bridge_supports_single_frozen_interlocutor:Jay"})
            continue
        text = str(request.get("text", "")).strip()
        if not text:
            _emit({"ok": False, "error": "empty_input"})
            continue

        result = agent.say(text)
        status = agent.engine.renderer_status()
        if status.get("actual_provider") != "duckhunter-shared-openai-compatible":
            raise RuntimeError(f"Wayfarer renderer fell back during scored response: {status}")
        if status.get("model_name") != model_id:
            raise RuntimeError(f"Wayfarer renderer model changed during scored response: {status}")
        response = str(result.get("response", "")).strip()
        if not response:
            raise RuntimeError("Wayfarer returned an empty response")

        _emit(
            {
                "ok": True,
                "response_text": response,
                "public_trace": {
                    "selected_intention": result.get("selected_intention"),
                    "bucket": result.get("bucket"),
                    "renderer_status": status,
                },
            }
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
