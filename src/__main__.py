"""CLI for lablog."""
import sys, json, argparse
from .core import Lablog

def main():
    parser = argparse.ArgumentParser(description="LabLog — AI Lab Notebook. Digital lab notebook with AI-powered experiment documentation and analysis.")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "run", "info"])
    parser.add_argument("--input", "-i", default="")
    args = parser.parse_args()
    instance = Lablog()
    if args.command == "status":
        print(json.dumps(instance.get_stats(), indent=2))
    elif args.command == "run":
        print(json.dumps(instance.process(input=args.input or "test"), indent=2, default=str))
    elif args.command == "info":
        print(f"lablog v0.1.0 — LabLog — AI Lab Notebook. Digital lab notebook with AI-powered experiment documentation and analysis.")

if __name__ == "__main__":
    main()
