from __future__ import annotations

from pathlib import Path
from typing import Dict

import jsonschema
import yaml

from utils.logger import get_logger

LOG = get_logger("lattice")
CONFIG = Path(__file__).resolve().parents[1] / "config"

# Minimal JSON Schemas (deterministic, explicit)
TRUST_SCHEMA = {
    "type": "object",
    "required": ["slug", "name", "jurisdiction"],
    "properties": {
        "slug": {"type": "string", "pattern": "^[a-z0-9-]{3,}$"},
        "name": {"type": "string", "minLength": 3},
        "purpose": {"type": "string"},
        "jurisdiction": {"type": "string", "minLength": 2},
    },
}
ROLE_SCHEMA = {
    "type": "object",
    "required": ["trust", "role", "party"],
    "properties": {
        "trust": {"type": "string"},
        "role": {
            "type": "string",
            "enum": ["trustee", "protector", "beneficiary", "advisor"],
        },
        "party": {"type": "string", "minLength": 2},
        "powers": {"type": "object"},
    },
}
ASSET_SCHEMA = {
    "type": "object",
    "required": ["trust", "class", "descriptor"],
    "properties": {
        "trust": {"type": "string"},
        "class": {"type": "string", "enum": ["land", "water", "air"]},
        "descriptor": {"type": "string", "minLength": 2},
        "jurisdiction": {"type": "string"},
        "metadata": {"type": "object"},
    },
}
LAWS_SCHEMA = {
    "type": "object",
    "properties": {
        "jurisdictions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["code", "name"],
                "properties": {"code": {"type": "string"}, "name": {"type": "string"}},
            },
        },
        "obligations": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["trust", "name", "kind"],
                "properties": {
                    "trust": {"type": "string"},
                    "name": {"type": "string"},
                    "kind": {"type": "string", "enum": ["compliance", "covenant"]},
                    "schedule": {"type": "string"},
                    "authority": {"type": "string"},
                    "details": {"type": "object"},
                },
            },
        },
    },
}


def _load(name: str, config_path: Path):
    p = config_path / name
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else None


def validate_all(config_path: Path = CONFIG) -> Dict[str, int]:
    trusts = _load("trusts.yaml", config_path) or []
    roles = _load("roles.yaml", config_path) or []
    assets = _load("assets.yaml", config_path) or []
    laws = _load("laws.yaml", config_path) or {}

    for t in trusts:
        jsonschema.validate(t, TRUST_SCHEMA)
    for r in roles:
        jsonschema.validate(r, ROLE_SCHEMA)
    for a in assets:
        jsonschema.validate(a, ASSET_SCHEMA)
    jsonschema.validate(laws or {}, LAWS_SCHEMA)

    # Simple rule checks:
    # 1) Each trust must have at least one trustee.
    slugs = {t["slug"] for t in trusts}
    trustees = {r["trust"] for r in roles if r["role"] == "trustee"}
    missing = [s for s in slugs if s not in trustees]
    if missing:
        raise ValueError(f"Rule violation: trusts without a trustee: {missing}")

    # 2) If asset class = air, ensure there is a jurisdiction and descriptor mentions AGL/ceiling or corridor
    for a in assets:
        if a["class"] == "air":
            if "jurisdiction" not in a:
                raise ValueError(f"Air asset must specify jurisdiction: {a}")
            desc = a["descriptor"].lower()
            if not any(k in desc for k in ["agl", "ceiling", "corridor", "altitude"]):
                raise ValueError(
                    f"Air asset descriptor should indicate bounds/altitude: {a['descriptor']}"
                )

    LOG.info(
        "Validation passed: %d trusts, %d roles, %d assets, %d obligations",
        len(trusts),
        len(roles),
        len(assets),
        len((laws or {}).get("obligations", [])),
    )
    return {
        "trusts": len(trusts),
        "roles": len(roles),
        "assets": len(assets),
        "obligations": len((laws or {}).get("obligations", [])),
    }
