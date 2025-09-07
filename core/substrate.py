from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List

import yaml

from utils.logger import get_logger
from utils.provenance import append_event

LOG = get_logger("substrate")

SCHEMA_SQL = Path(__file__).resolve().parents[1] / "schema.sql"

if not SCHEMA_SQL.exists():
    raise FileNotFoundError(f"schema.sql not found at {SCHEMA_SQL}")
CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL;")  # Set WAL mode immediately on connection
    return con


def init_db(db_path: Path) -> None:
    LOG.info("Initializing database at %s", db_path)
    schema_file_path = SCHEMA_SQL.resolve()
    LOG.info("Opening schema file: %s", schema_file_path)
    with connect(db_path) as con:
        with open(schema_file_path, "r", encoding="utf-8") as f:
            con.executescript(f.read())
        con.execute("PRAGMA foreign_keys=ON;")  # Set foreign keys after schema
    LOG.info(
        "DB_WAL_ENABLED: Database initialized with WAL mode and foreign keys enabled."
    )


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def _load_yaml(p: Path) -> Any:
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else None


def ingest_from_config(db_path: Path) -> Dict[str, int]:
    """
    Ingests YAMLs from config/: jurisdictions (from laws.yaml), trusts, roles, assets, obligations.
    Populates FTS index.
    """
    trusts = _load_yaml(CONFIG_DIR / "trusts.yaml") or []
    roles = _load_yaml(CONFIG_DIR / "roles.yaml") or []
    assets = _load_yaml(CONFIG_DIR / "assets.yaml") or []
    laws = _load_yaml(CONFIG_DIR / "laws.yaml") or {}

    inserted = {
        "jurisdictions": 0,
        "trusts": 0,
        "roles": 0,
        "assets": 0,
        "obligations": 0,
    }

    with connect(db_path) as con:
        cur = con.cursor()

        # Jurisdictions from laws.yaml: {jurisdictions: [{code,name},...]}
        jzs: List[Dict[str, str]] = (laws or {}).get("jurisdictions", [])
        for j in jzs:
            cur.execute(
                "INSERT OR IGNORE INTO jurisdictions(code,name) VALUES(?,?)",
                (j["code"], j["name"]),
            )
            if cur.rowcount == 0:
                LOG.info(
                    "DB_INGEST_CONFLICT_IGNORED: Jurisdiction '%s' already exists, skipped.",
                    j["code"],
                )
        inserted["jurisdictions"] = cur.execute(
            "SELECT count(*) c FROM jurisdictions"
        ).fetchone()["c"]

        # Trusts
        for t in trusts:
            cur.execute(
                """
                INSERT OR IGNORE INTO trusts(slug,name,purpose,jurisdiction_id,created_at,updated_at)
                VALUES (?, ?, ?, (SELECT id FROM jurisdictions WHERE code=?), ?, ?)
            """,
                (
                    t["slug"],
                    t["name"],
                    t.get("purpose", ""),
                    t.get("jurisdiction", "NZ"),
                    _now_iso(),
                    _now_iso(),
                ),
            )
            if cur.rowcount == 0:
                LOG.info(
                    "DB_INGEST_CONFLICT_IGNORED: Trust '%s' already exists, skipped.",
                    t["slug"],
                )
        inserted["trusts"] = cur.execute("SELECT count(*) c FROM trusts").fetchone()[
            "c"
        ]

        # Roles
        for r in roles:
            cur.execute(
                """
              INSERT OR IGNORE INTO roles(trust_id,role_type,party,powers)
              SELECT id, ?, ?, ?
              FROM trusts WHERE slug=?
            """,
                (
                    r["role"],
                    r["party"],
                    json.dumps(r.get("powers", {}), separators=("", ":")),
                    r["trust"],
                ),
            )
            if cur.rowcount == 0:
                LOG.info(
                    "DB_INGEST_CONFLICT_IGNORED: Role for trust '%s' and party '%s' already exists, skipped.",
                    r["trust"],
                    r["party"],
                )
        inserted["roles"] = cur.execute("SELECT count(*) c FROM roles").fetchone()["c"]

        # Assets
        for a in assets:
            cur.execute(
                """
              INSERT OR IGNORE INTO assets(trust_id,class,descriptor,jurisdiction_id,metadata)
              SELECT id, ?, ?, (SELECT id FROM jurisdictions WHERE code=?), ?
              FROM trusts WHERE slug=?
            """,
                (
                    a["class"],
                    a["descriptor"],
                    a.get("jurisdiction", "NZ"),
                    json.dumps(a.get("metadata", {}), separators=("", ":")),
                    a["trust"],
                ),
            )
            if cur.rowcount == 0:
                LOG.info(
                    "DB_INGEST_CONFLICT_IGNORED: Asset '%s' for trust '%s' already exists, skipped.",
                    a["descriptor"],
                    a["trust"],
                )
        inserted["assets"] = cur.execute("SELECT count(*) c FROM assets").fetchone()[
            "c"
        ]

        # Obligations: in laws.yaml: {obligations:[{trust, name, kind, schedule, authority, details},...]}
        for o in (laws or {}).get("obligations", []):
            cur.execute(
                """
              INSERT OR IGNORE INTO obligations(trust_id,name,kind,schedule,authority,details)
              SELECT id, ?, ?, ?, ?, ?
              FROM trusts WHERE slug=?
            """,
                (
                    o["name"],
                    o["kind"],
                    o.get("schedule", ""),
                    o.get("authority", ""),
                    json.dumps(o.get("details", {}), separators=("", ":")),
                    o["trust"],
                ),
            )
            if cur.rowcount == 0:
                LOG.info(
                    "DB_INGEST_CONFLICT_IGNORED: Obligation '%s' for trust '%s' already exists, skipped.",
                    o["name"],
                    o["trust"],
                )
        inserted["obligations"] = cur.execute(
            "SELECT count(*) c FROM obligations"
        ).fetchone()["c"]

        # Rebuild FTS
        cur.execute("DELETE FROM search_idx")
        # trusts
        for row in cur.execute("SELECT slug,name,purpose FROM trusts"):
            cur.execute(
                "INSERT INTO search_idx(scope,key,content) VALUES(?,?,?)",
                ("trusts", row["slug"], f'{row["name"]} {row["purpose"]}'),
            )
        # roles
        for row in cur.execute(
            "SELECT r.id,t.slug,role_type,party FROM roles r JOIN trusts t ON r.trust_id=t.id"
        ):
            cur.execute(
                "INSERT INTO search_idx(scope,key,content) VALUES(?,?,?)",
                ("roles", row["slug"], f'{row["role_type"]} {row["party"]}'),
            )
        # assets
        rows = cur.execute(
            "SELECT a.id,t.slug,class,descriptor FROM assets a JOIN trusts t ON a.trust_id=t.id"
        ).fetchall()
        for row in rows:
            cur.execute(
                "INSERT INTO search_idx(scope,key,content) VALUES(?,?,?)",
                ("assets", row["slug"], f'{row["class"]} {row["descriptor"]}'),
            )
        # obligations
        for row in cur.execute(
            "SELECT o.id,t.slug,o.name,o.kind,o.authority FROM obligations o JOIN trusts t ON o.trust_id=t.id"
        ):
            cur.execute(
                "INSERT INTO search_idx(scope,key,content) VALUES(?,?,?)",
                (
                    "obligations",
                    row["slug"],
                    f'{row["name"]} {row["kind"]} {row["authority"]}',
                ),
            )

        con.commit()

    append_event({"type": "ingest", "source": "config/", "counters": inserted})
    LOG.info("Ingest complete: %s", inserted)
    return inserted


def search_fts(db_path: Path, query: str, scope: str = "all") -> List[Dict[str, Any]]:
    """Search the FTS index."""
    with connect(db_path) as con:
        sql = "SELECT scope, key, content FROM search_idx WHERE content MATCH ?"
        params = [query]
        if scope != "all":
            sql += " AND scope = ?"
            params.append(scope)
        return [dict(row) for row in con.execute(sql, tuple(params))]
