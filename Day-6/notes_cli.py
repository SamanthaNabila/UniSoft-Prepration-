import argparse
import json
import sys

from app.storage import load_notes, save_notes


COMMANDS = ("add", "list", "search", "delete")
DEFAULT_NOTES_FILE = "notes.json"


def build_parser():
    parser = argparse.ArgumentParser(description="Manage notes")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("title")
    add_parser.add_argument("body")
    add_parser.add_argument("--file", default=DEFAULT_NOTES_FILE)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--file", default=DEFAULT_NOTES_FILE)

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("query")
    search_parser.add_argument("--file", default=DEFAULT_NOTES_FILE)

    delete_parser = subparsers.add_parser("delete")
    delete_parser.add_argument("title")
    delete_parser.add_argument("--file", default=DEFAULT_NOTES_FILE)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    if args.command == "add":
        if not args.body:
            raise ValueError("body cannot be empty")

        notes = load_notes(args.file)
        notes.append({"title": args.title, "body": args.body})
        save_notes(args.file, notes)
        return

    if args.command == "list":
        try:
            notes = load_notes(args.file)
        except json.JSONDecodeError:
            print(f"Invalid notes file: {args.file}", file=sys.stderr)
            raise SystemExit(1)

        for note in notes:
            print(f"{note['title']}: {note['body']}")
        return

    if args.command == "search":
        query = args.query.casefold()
        for note in load_notes(args.file):
            if query in note["title"].casefold() or query in note["body"].casefold():
                print(f"{note['title']}: {note['body']}")
        return

    if args.command == "delete":
        notes = load_notes(args.file)
        for note_index, note in enumerate(notes):
            if note["title"] == args.title:
                confirmation = input(f"Delete '{args.title}'? [y/N] ")
                if confirmation.casefold() in ("y", "yes"):
                    save_notes(args.file, notes[:note_index] + notes[note_index + 1 :])
                return
        return

    print("not implemented")


if __name__ == "__main__":
    main()