# Inbox Model
**Status:** Accepted (Bronze)
**Date:** 2025-09-07

## Context
- Mild inbox tampering observed
- Need basic resilience

## Decision
- Accept baseline detection + logging only
- No auto-remediation in Bronze

## Consequences
- Manual operator action if anomalies
- Silver will add policies

## Notes
- [Logging & Audit](./ADR-0004%20Logging%20&%20Audit.md)
