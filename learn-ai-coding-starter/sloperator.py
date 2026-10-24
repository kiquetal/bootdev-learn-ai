import sys
from pathlib import Path

from sloperator.runner import check_program, run_program

USAGE = "usage: uv run sloperator.py [--check] <file.slop>"


def main(argv: list[str]) -> int:
    check = False
    paths: list[str] = []
    for arg in argv[1:]:
        if arg == "--check":
            check = True
        elif arg in ("-h", "--help"):
            print(USAGE)
            return 0
        elif arg.startswith("-"):
            print(f"unknown option '{arg}'", file=sys.stderr)
            print(USAGE, file=sys.stderr)
            return 2
        else:
            paths.append(arg)

    if len(paths) != 1:
        print(USAGE, file=sys.stderr)
        return 2

    path = Path(paths[0])
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as error:
        print(f"could not read '{path}': {error.strerror}", file=sys.stderr)
        return 2

    error = check_program(source) if check else run_program(source, sys.stdout)
    if error is not None:
        sys.stdout.flush()
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
