import argparse
import sys


def main() -> None:
    # First pass: pull --upper from any position without consuming other args.
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--upper", action="store_true")
    pre_args, remaining = pre.parse_known_args()

    # Second pass: parse the subcommand and its positional.
    parser = argparse.ArgumentParser(prog="greet.py")
    subparsers = parser.add_subparsers(dest="command", metavar="<hello>")
    hello_parser = subparsers.add_parser("hello")
    hello_parser.add_argument("name")

    parsed = parser.parse_args(remaining)
    if parsed.command is None:
        parser.print_usage(sys.stderr)
        sys.exit(1)

    message = f"Hello, {parsed.name}!"
    if pre_args.upper:
        message = message.upper()
    print(message)


if __name__ == "__main__":
    main()
