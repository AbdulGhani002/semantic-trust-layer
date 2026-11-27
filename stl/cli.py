"""Command line for the Semantic Trust Layer."""
from __future__ import annotations

import argparse
import json


def serve(args: argparse.Namespace) -> None:
    import uvicorn

    from .api import create_app

    print(f"Dashboard: http://{args.host}:{args.port}")
    uvicorn.run(create_app(start_gateways=not args.no_gateways), host=args.host, port=args.port, log_level="warning")


def check(args: argparse.Namespace) -> None:
    from .api import Layer
    from .extract import find_urls
    from .schema import Item

    layer = Layer()
    item = Item(kind="message", text=args.text, urls=find_urls(args.text))
    verdict, _ = layer.coordinator.inspect(item)
    print(json.dumps(verdict.model_dump(mode="json"), indent=1, ensure_ascii=False))


def download(args: argparse.Namespace) -> None:
    from pathlib import Path

    from .releases import fetch

    fetch(Path(args.root) if args.root else Path(__file__).resolve().parent.parent, args.checkpoints)


def main() -> None:
    parser = argparse.ArgumentParser(prog="stl", description="Semantic Trust Layer")
    commands = parser.add_subparsers(dest="command", required=True)
    start = commands.add_parser("serve", help="start the dashboard and test gateways")
    start.add_argument("--host", default="127.0.0.1")
    start.add_argument("--port", type=int, default=8050)
    start.add_argument("--no-gateways", action="store_true", help="do not start the SMTP and HTTP test gateways")
    start.set_defaults(run=serve)
    one = commands.add_parser("check", help="check one message")
    one.add_argument("text")
    one.set_defaults(run=check)
    get = commands.add_parser("download", help="download the trained models from the GitHub release")
    get.add_argument("--checkpoints", action="store_true", help="also download the training checkpoints (707 MB)")
    get.add_argument("--root", help="folder that gets the models folder (default: the project folder)")
    get.set_defaults(run=download)
    args = parser.parse_args()
    args.run(args)


if __name__ == "__main__":
    main()
