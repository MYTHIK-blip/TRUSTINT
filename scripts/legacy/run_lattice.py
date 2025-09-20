#!/usr/bin/env python3

import argparse

from core.lattice import validate_all
from core.substrate import ingest_from_config, init_db


def main():
    parser = argparse.ArgumentParser(description="Run TRUSTINT lattice operations.")
    parser.add_argument(
        "--only",
        choices=["validate", "ingest", "all"],
        default="all",
        help="Specify which operation to run (default: all)",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip validation when --only ingest is specified",
    )
    args = parser.parse_args()

    if args.only == "validate":
        counts = validate_all()
        print("OK :: validate ::", counts)
    elif args.only == "ingest":
        if not args.no_validate:
            validate_all()
        init_db()
        counters = ingest_from_config()
        print("OK :: ingest ::", counters)
    elif args.only == "all":
        counts = validate_all()
        init_db()
        counters = ingest_from_config()
        print("OK :: validate+ingest ::", counters)


if __name__ == "__main__":
    main()
