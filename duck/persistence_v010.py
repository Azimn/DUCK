"""Transactional multi-file snapshot persistence for MicroPsiDUCK v0.10.

The current organism spans several separately versioned state stores. Atomic
replacement of each JSON file is not enough because a crash between replacements can
leave a mixture of generations. ``SnapshotStore`` stages one complete generation,
validates it with hashes, atomically renames the generation directory, and finally
atomically moves one manifest pointer to make that generation authoritative.

Root-level JSON files may still be maintained by the host as compatibility mirrors,
but once a snapshot manifest exists they are not persistence authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import uuid
from typing import Mapping

SNAPSHOT_SCHEMA = "micropsi-duck.snapshot.v1"
SNAPSHOT_META_SCHEMA = "micropsi-duck.snapshot-generation.v1"
SNAPSHOT_DIRNAME = ".snapshots_v010"
SNAPSHOT_MANIFEST = "snapshot_manifest_v010.json"
GENERATION_META = "generation.json"
DEFAULT_RETAIN_GENERATIONS = 3


def _json_text(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SnapshotGeneration:
    generation: int
    tick: int
    payloads: dict[str, object]


class SnapshotStore:
    """Commit and recover all-or-nothing organism generations.

    ``_checkpoint`` is intentionally a no-op hook. Adversarial crash tests may
    monkey-patch it to raise after any staging/commit boundary without adding a
    production-only fault API to the host.
    """

    def __init__(self, root: str | Path, *, retain_generations: int = DEFAULT_RETAIN_GENERATIONS) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.snapshot_root = self.root / SNAPSHOT_DIRNAME
        self.manifest_path = self.root / SNAPSHOT_MANIFEST
        self.retain_generations = max(2, int(retain_generations))

    def _checkpoint(self, label: str) -> None:
        del label

    @staticmethod
    def _generation_name(generation: int) -> str:
        return f"gen-{max(0, int(generation)):08d}"

    @staticmethod
    def _parse_generation(path: Path) -> int | None:
        name = path.name
        if not name.startswith("gen-"):
            return None
        try:
            return int(name[4:])
        except ValueError:
            return None

    @staticmethod
    def _write_text(path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    @staticmethod
    def _atomic_write(path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            delete=False,
            dir=path.parent,
            prefix=path.stem + ".",
            suffix=".tmp",
        ) as handle:
            handle.write(text)
            temp_name = handle.name
        Path(temp_name).replace(path)

    def _committed_generation_hint(self) -> int:
        if not self.manifest_path.exists():
            return 0
        try:
            payload = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            if str(payload.get("schema_version", "")) != SNAPSHOT_SCHEMA:
                return 0
            return max(0, int(payload.get("generation", 0)))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return 0

    def _existing_generations(self) -> list[int]:
        if not self.snapshot_root.exists():
            return []
        rows: list[int] = []
        for path in self.snapshot_root.iterdir():
            if not path.is_dir():
                continue
            generation = self._parse_generation(path)
            if generation is not None:
                rows.append(generation)
        return sorted(set(rows))

    def _next_generation(self) -> int:
        return max([self._committed_generation_hint(), *self._existing_generations()], default=0) + 1

    def commit(self, payloads: Mapping[str, object], *, tick: int) -> int:
        """Stage and atomically publish one complete generation.

        The authoritative commit point is replacement of ``snapshot_manifest_v010.json``.
        If a process dies before that replacement, the previous manifest still points
        to the previous complete generation.
        """

        normalized: dict[str, object] = {
            str(name): payload
            for name, payload in payloads.items()
            if str(name).strip()
        }
        if "subject.json" not in normalized:
            raise ValueError("transactional snapshot requires subject.json")

        generation = self._next_generation()
        self.snapshot_root.mkdir(parents=True, exist_ok=True)
        temp_dir = self.snapshot_root / f".stage-{generation:08d}-{uuid.uuid4().hex}"
        final_dir = self.snapshot_root / self._generation_name(generation)
        temp_dir.mkdir(parents=True, exist_ok=False)

        hashes: dict[str, str] = {}
        try:
            for name in sorted(normalized):
                text = _json_text(normalized[name])
                self._write_text(temp_dir / name, text)
                hashes[name] = _sha256_text(text)
                self._checkpoint(f"component:{name}")

            generation_meta = {
                "schema_version": SNAPSHOT_META_SCHEMA,
                "generation": generation,
                "tick": max(0, int(tick)),
                "components": hashes,
            }
            meta_text = _json_text(generation_meta)
            self._write_text(temp_dir / GENERATION_META, meta_text)
            self._checkpoint("generation_metadata")

            if final_dir.exists():
                raise RuntimeError(f"snapshot generation already exists: {generation}")
            temp_dir.replace(final_dir)
            self._checkpoint("generation_renamed")

            manifest = {
                "schema_version": SNAPSHOT_SCHEMA,
                "generation": generation,
                "tick": max(0, int(tick)),
            }
            self._atomic_write(self.manifest_path, _json_text(manifest))
            self._checkpoint("manifest_committed")
        except Exception:
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
            raise

        self._cleanup_old_generations()
        return generation

    def _read_generation(self, generation: int) -> SnapshotGeneration | None:
        path = self.snapshot_root / self._generation_name(generation)
        meta_path = path / GENERATION_META
        if not path.is_dir() or not meta_path.exists():
            return None
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if str(meta.get("schema_version", "")) != SNAPSHOT_META_SCHEMA:
                return None
            if int(meta.get("generation", -1)) != int(generation):
                return None
            components = meta.get("components", {})
            if not isinstance(components, dict) or "subject.json" not in components:
                return None
            payloads: dict[str, object] = {}
            for raw_name, raw_hash in components.items():
                name = str(raw_name)
                expected_hash = str(raw_hash)
                component_path = path / name
                if not component_path.is_file():
                    return None
                text = component_path.read_text(encoding="utf-8")
                if _sha256_text(text) != expected_hash:
                    return None
                payloads[name] = json.loads(text)
            return SnapshotGeneration(
                generation=int(generation),
                tick=max(0, int(meta.get("tick", 0))),
                payloads=payloads,
            )
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return None

    def load(self) -> SnapshotGeneration | None:
        """Load the latest valid committed generation.

        If no manifest has ever committed, return ``None`` so callers may use the
        legacy root-file migration path. Once a manifest exists, root mirrors must
        never be used to recover a corrupt/mixed transactional generation.
        """

        if not self.manifest_path.exists():
            return None
        try:
            manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            raise RuntimeError("transactional snapshot manifest is unreadable") from exc
        if str(manifest.get("schema_version", "")) != SNAPSHOT_SCHEMA:
            raise RuntimeError("unsupported transactional snapshot manifest schema")
        committed = max(0, int(manifest.get("generation", 0)))
        if committed <= 0:
            raise RuntimeError("transactional snapshot manifest has no committed generation")

        candidates = [
            generation
            for generation in self._existing_generations()
            if generation <= committed
        ]
        candidates.sort(reverse=True)
        for generation in candidates:
            row = self._read_generation(generation)
            if row is not None:
                return row
        raise RuntimeError("no valid committed transactional snapshot generation is recoverable")

    def _cleanup_old_generations(self) -> None:
        generations = self._existing_generations()
        if len(generations) <= self.retain_generations:
            return
        keep = set(generations[-self.retain_generations :])
        for generation in generations:
            if generation in keep:
                continue
            path = self.snapshot_root / self._generation_name(generation)
            shutil.rmtree(path, ignore_errors=True)


__all__ = [
    "DEFAULT_RETAIN_GENERATIONS",
    "GENERATION_META",
    "SNAPSHOT_DIRNAME",
    "SNAPSHOT_MANIFEST",
    "SNAPSHOT_META_SCHEMA",
    "SNAPSHOT_SCHEMA",
    "SnapshotGeneration",
    "SnapshotStore",
]
