import argparse


COMMANDS = ("add", "list", "search", "delete")


def build_parser():
    parser = argparse.ArgumentParser(description="Manage notes")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in COMMANDS:
        subparsers.add_parser(command)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    print("not implemented")


if __name__ == "__main__":
    main()
