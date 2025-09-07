#!/usr/bin/env python3

from core.matrices import export_csv, export_jsonl, export_markdown, write_checksums


def main():
    out = [export_jsonl(), export_csv(), export_markdown()]
    write_checksums(out)
    print("OK :: exports:", [p.name for p in out])


if __name__ == "__main__":
    main()
