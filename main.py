import argparse
import sys

# the actual simulations live in the experiments folder
from experiments import part1, part2

# utility functions for parsing command line arguments
def csv(value: str):
    return [v.strip() for v in value.split(",") if v.strip()]

# Checking valid list of agent names
def canonical(names, allowed):
    """Match user input case-insensitively against the allowed agent names."""
    lookup = {a.lower(): a for a in allowed}
    out = []
    for n in names:
        if n.lower() not in lookup:
            sys.exit(f"Unknown agent '{n}'. Choose from: {', '.join(allowed)}")
        out.append(lookup[n.lower()])
    if sorted(out) != sorted(allowed):
        sys.exit(f"List every agent exactly once: {', '.join(allowed)}")
    return out

# Build the command line parser
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="6COM2012 Worksheet 1 - Co-existing agents")
    sub = p.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("part1", help="3x3 wrap-around world")
    p1.add_argument("--steps", type=int, default=50)
    p1.add_argument("--start-order", type=csv, default=list(part1.DEFAULT_ORDER),
                    help="who enters at t=0,2,4, e.g. Left,Clockwise,Diamond")
    p1.add_argument("--move-order", type=csv, default=list(part1.DEFAULT_ORDER),
                    help="who moves first in each round")
    p1.add_argument("--retry-blocked", action="store_true",
                    help="a blocked agent waits and retries the SAME move "
                         "(default: the cancelled move is lost, pattern continues)")
    p1.add_argument("--show", action="store_true", help="draw the grid every step")

    p2 = sub.add_parser("part2", help="5x5 Platform Royal")
    p2.add_argument("--steps", type=int, default=part2.STEPS)
    p2.add_argument("--hunter", action="store_true", help="add the challenge agent")
    p2.add_argument("--show", action="store_true", help="draw the grid every step")
    p2.add_argument("--quiet", action="store_true", help="hide push/removal log")

    sub.add_parser("all", help="run Part 1, Part 2 and Part 2 with the Hunter")
    return p

# Main entry point
def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    # the three agent names are always the same in Part 1
    names = list(part1.DEFAULT_ORDER)

    if args.cmd == "part1":
        part1.run(args.steps,
                  canonical(args.start_order, names),
                  canonical(args.move_order, names),
                  retry_blocked=args.retry_blocked,
                  show=args.show)
    elif args.cmd == "part2":
        part2.run(args.steps, with_hunter=args.hunter,
                  show=args.show, verbose=not args.quiet)
    else:
        part1.run()
        print()
        part2.run(verbose=False)
        print()
        part2.run(with_hunter=True, verbose=False)


if __name__ == "__main__":
    main()
