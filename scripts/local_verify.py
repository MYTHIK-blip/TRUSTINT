#!/usr/bin/env python3
"""
Local end-to-end verifier for a TRUSTINT ledger file.
- Verifies prev chain and HMACs using vault/.hmac_key
- Reports first failure with line number; exits 0 on full pass
"""

import base64
import hashlib
import hmac
import io
import json
import os
import sys
from typing import Any, Dict

if len(sys.argv) != 2:
    print("usage: local_verify.py <ledger.jsonl>", file=sys.stderr)
    sys.exit(2)

LEDGER = sys.argv[1]
KEY_PATH = "vault/.hmac_key"

if not os.path.exists(LEDGER):
    print(f"ERR: ledger not found: {LEDGER}", file=sys.stderr)
    sys.exit(2)
if not os.path.exists(KEY_PATH):
    print(f"ERR: key not found: {KEY_PATH}", file=sys.stderr)
    sys.exit(2)


def canon(obj: Dict[str, Any]) -> bytes:
    # TRUSTINT canonical form: compact separators + sorted keys
    return json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")


# load key (base64url, 32 bytes when decoded)
k = open(KEY_PATH, "rb").read().strip()
k += b"=" * ((4 - (len(k) % 4)) % 4)
key = base64.urlsafe_b64decode(k)

prev_mac = None
count = 0

with io.open(LEDGER, "r", encoding="utf-8", newline="") as f:
    for idx, line in enumerate(f, start=1):
        line = line.rstrip("\n")
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception as e:
            print(f"FAIL line {idx}: JSON parse error: {e}")
            sys.exit(1)

        mac_stored = obj.get("mac")
        if mac_stored is None:
            print(f"FAIL line {idx}: missing 'mac'")
            sys.exit(1)

        # Check linkage (if not first record)
        if prev_mac is not None:
            if obj.get("prev") != prev_mac:
                print(
                    f"FAIL line {idx}: prev mismatch\n  expected: {prev_mac}\n  actual:   {obj.get('prev')}"
                )
                sys.exit(1)

        # Compute HMAC over all fields except 'mac'
        payload = {k: v for k, v in obj.items() if k != "mac"}
        mac_calc = hmac.new(key, canon(payload), hashlib.sha256).hexdigest()

        if mac_calc.lower() != mac_stored.lower():
            print(
                f"FAIL line {idx}: HMAC mismatch\n  mac_file: {mac_stored}\n  mac_calc: {mac_calc}"
            )
            sys.exit(1)

        prev_mac = mac_stored
        count += 1

print(f"PASS: verified {count} events; linkage & HMAC OK")
