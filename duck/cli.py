"""Command line interface for the integrated DUCK build."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .host import PersistentDuckHost
from .language import ModelExpression, ModelInnerVoice, OpenAICompatiblePort
from .living import BeliefStance, WorldEvent


def _host(args) -> PersistentDuckHost:
    cognition = None
    expression = None
    if getattr(args, "llm", False):
        port = OpenAICompatiblePort.from_env()
        cognition = ModelInnerVoice(port)
        expression = ModelExpression(port)
    return PersistentDuckHost.open(args.root, name=getattr(args, "name", "Duck"), cognition=cognition, expression=expression)


def cmd_status(args) -> int:
    host = _host(args)
    print(json.dumps(host.status(), indent=2))
    return 0


def cmd_chat(args) -> int:
    host = _host(args)
    print(f"{host.duck.state.name} is here. Type /quit to leave, /status for state summary, /tick to let time pass.")
    while True:
        try:
            text = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        if text in {"/quit", "/exit"}:
            break
        if text == "/status":
            print(json.dumps(host.status(), indent=2))
            continue
        if text.startswith("/tick"):
            parts = text.split()
            count = int(parts[1]) if len(parts) > 1 else 1
            steps = host.heartbeat(count)
            if steps:
                last = steps[-1]
                print(f"[{last.selected_action}] {last.inner_cognition.thought or ''}")
            continue
        result = host.interact(text)
        print(f"{host.duck.state.name}> {result.response_text}")
    host.save()
    return 0


def cmd_tick(args) -> int:
    host = _host(args)
    steps = host.heartbeat(args.count)
    for step in steps:
        print(json.dumps({"tick": step.tick, "action": step.selected_action, "thought": step.inner_cognition.thought}, ensure_ascii=False))
    return 0


def cmd_demo(args) -> int:
    host = PersistentDuckHost.open(args.root, name="Aster", subject_id="demo-subject")
    first = host.observe(WorldEvent("encounter", "Morgan", "Morgan threatens me.", ("social", "threat", "conflict"), -0.8, 0.9))
    host.resolve_outcome(first.action_id, success=0.8, valence=-0.7, description="Backing away kept me safe, but the encounter was frightening.", tags=("threat", "safety"))
    for _ in range(2):
        host.heartbeat()
    later = host.interact("Hey, it's Morgan. I'm back.", speaker="Morgan")
    print("subject:", host.duck.state.subject_id)
    print("response:", later.response_text)
    print("private thought:", later.private_thought)
    print("subjective state:")
    for line in later.subjective_state:
        print("  ", line)
    return 0


def cmd_commit(args) -> int:
    host = _host(args)
    item = host.duck.create_commitment(args.actor, args.text, due_in=args.due_in, importance=args.importance)
    host.save()
    print(item.commitment_id)
    return 0


def cmd_resolve_commitment(args) -> int:
    host = _host(args)
    item = host.duck.resolve_commitment(args.commitment_id, kept=args.kept, outcome=args.outcome)
    host.save()
    print(json.dumps({"commitment_id": item.commitment_id, "status": item.status}))
    return 0


def cmd_fact(args) -> int:
    host = _host(args)
    host.duck.set_world_fact(args.key, args.text, perceived=args.perceived)
    host.save()
    return 0


def cmd_belief(args) -> int:
    host = _host(args)
    host.duck.revise_belief(args.key, args.text, BeliefStance(args.stance), args.confidence, source="manual")
    host.save()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="duck", description="DUCK persistent subject simulator")
    parser.add_argument("--root", type=Path, default=Path("./duck_state"))
    parser.add_argument("--name", default="Duck")
    parser.add_argument("--llm", action="store_true", help="use DUCK_LLM_* environment variables for inner cognition and expression")
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status")
    status.set_defaults(func=cmd_status)
    chat = sub.add_parser("chat")
    chat.set_defaults(func=cmd_chat)
    tick = sub.add_parser("tick")
    tick.add_argument("count", type=int, nargs="?", default=1)
    tick.set_defaults(func=cmd_tick)
    demo = sub.add_parser("demo")
    demo.set_defaults(func=cmd_demo)

    commit = sub.add_parser("commit")
    commit.add_argument("actor")
    commit.add_argument("text")
    commit.add_argument("--due-in", type=int)
    commit.add_argument("--importance", type=float, default=0.6)
    commit.set_defaults(func=cmd_commit)

    resolved = sub.add_parser("resolve-commitment")
    resolved.add_argument("commitment_id")
    group = resolved.add_mutually_exclusive_group(required=True)
    group.add_argument("--kept", action="store_true")
    group.add_argument("--broken", dest="kept", action="store_false")
    resolved.add_argument("--outcome", default="")
    resolved.set_defaults(func=cmd_resolve_commitment)

    fact = sub.add_parser("fact")
    fact.add_argument("key")
    fact.add_argument("text")
    fact.add_argument("--perceived", action="store_true")
    fact.set_defaults(func=cmd_fact)

    belief = sub.add_parser("belief")
    belief.add_argument("key")
    belief.add_argument("text")
    belief.add_argument("--stance", choices=[item.value for item in BeliefStance], default="uncertain")
    belief.add_argument("--confidence", type=float, default=0.5)
    belief.set_defaults(func=cmd_belief)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
