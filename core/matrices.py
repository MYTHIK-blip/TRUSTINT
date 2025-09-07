from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path

from utils.logger import get_logger
from utils.provenance import append_event, sha256_file

LOG = get_logger("matrices")
DB_PATH = Path("vault/trustint.db")
DIST = Path("dist")
DIST.mkdir(exist_ok=True, parents=True)


def _con() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def export_jsonl() -> Path:
    out = DIST / "trustint_export.jsonl"
    with _con() as con, open(out, "w", encoding="utf-8") as f:
        for row in con.execute(
            """
          SELECT t.slug,t.name,t.purpose,j.code AS jurisdiction
          FROM trusts t LEFT JOIN jurisdictions j ON t.jurisdiction_id=j.id
        """
        ):
            f.write(json.dumps(dict(row), ensure_ascii=False) + "\n")
    append_event({"type": "export", "format": "jsonl", "path": str(out)})
    return out


def export_csv() -> Path:
    out = DIST / "trustint_export.csv"
    with _con() as con, open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["trust", "entity", "field1", "field2", "field3"])
        for r in con.execute("SELECT slug,name,purpose FROM trusts"):
            w.writerow([r["slug"], "trust", r["name"], r["purpose"], ""])
        for r in con.execute(
            """SELECT t.slug, role_type, party FROM roles r
                                JOIN trusts t ON r.trust_id=t.id"""
        ):
            w.writerow([r["slug"], "role", r["role_type"], r["party"], ""])
        for r in con.execute(
            """SELECT t.slug, class, descriptor FROM assets a
                                JOIN trusts t ON a.trust_id=t.id"""
        ):
            w.writerow([r["slug"], "asset", r["class"], r["descriptor"], ""])
    append_event({"type": "export", "format": "csv", "path": str(out)})
    return out


def export_markdown() -> Path:
    out = DIST / "board_report.md"
    with _con() as con, open(out, "w", encoding="utf-8") as f:
        f.write("# TRUSTINT — Board Report\n\n")
        for t in con.execute(
            """SELECT t.id, t.slug, t.name, t.purpose, j.code AS jz
                                FROM trusts t LEFT JOIN jurisdictions j ON j.id=t.jurisdiction_id
                                ORDER BY slug"""
        ):
            f.write(f"## {t['name']} (`{t['slug']}`) — {t['jz'] or '—'}\n")
            if t["purpose"]:
                f.write(f"> {t['purpose']}\n\n")
            f.write("### Roles\n")
            for r in con.execute(
                "SELECT role_type,party,powers FROM roles WHERE trust_id=?", (t["id"],)
            ):
                f.write(f"- **{r['role_type']}** — {r['party']}\n")
            f.write("\n### Assets (LAW)\n")
            for a in con.execute(
                "SELECT class,descriptor FROM assets WHERE trust_id=?", (t["id"],)
            ):
                f.write(f"- **{a['class']}** — {a['descriptor']}\n")
            f.write("\n---\n\n")
    append_event({"type": "export", "format": "md", "path": str(out)})
    return out


def write_checksums(paths):
    sums = DIST / "SHA256SUMS"
    with open(sums, "w", encoding="utf-8") as f:
        for p in paths:
            f.write(f"{sha256_file(p)}  {p.name}\n")
    append_event(
        {"type": "checksums", "files": [p.name for p in paths], "path": str(sums)}
    )
    LOG.info("Wrote checksums to %s", sums)
    return sums
