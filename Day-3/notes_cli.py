import argparse

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

    subparsers.add_parser("delete")

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    if args.command == "add":
        notes = load_notes(args.file)
        notes.append({"title": args.title, "body": args.body})
        save_notes(args.file, notes)
        return

    if args.command == "list":
        for note in load_notes(args.file):
            print(f"{note['title']}: {note['body']}")
        return

    if args.command == "search":
        query = args.query.casefold()
        for note in load_notes(args.file):
            if query in note["title"].casefold() or query in note["body"].casefold():
                print(f"{note['title']}: {note['body']}")
        return

    print("not implemented")


if __name__ == "__main__":
    main()