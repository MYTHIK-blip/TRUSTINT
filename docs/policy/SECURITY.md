# Security Policy

This document outlines the security policies and practices for the TRUSTINT system, focusing on the handling of sensitive information, particularly cryptographic keys and environment variables.

## No Secrets in Repository

**Crucially, no secrets, API keys, private keys, or sensitive credentials are ever to be committed directly into the TRUSTINT Git repository.** This policy is enforced to prevent accidental exposure of sensitive information.

## Cryptographic Keys (HMAC)

The TRUSTINT system uses HMAC-SHA256 for maintaining the integrity and immutability of its provenance ledger (`vault/events.jsonl`). The HMAC key is a critical secret.

-   **`TRUSTINT_HMAC_KEY` Environment Variable:** The primary method for providing the HMAC key to the application is via the `TRUSTINT_HMAC_KEY` environment variable. This ensures the key is not stored in the codebase or configuration files.
-   **`vault/.hmac_key` Fallback:** For operational convenience and disaster recovery, a copy of the `TRUSTINT_HMAC_KEY` may be stored in a file named `vault/.hmac_key`. This file **must be protected with appropriate file system permissions** and is typically excluded from version control via `.gitignore`.
-   **Key Management:** The generation, rotation, and secure storage of the `TRUSTINT_HMAC_KEY` are external operational concerns and must follow organizational security best practices.

## Environment Variables

Sensitive configuration parameters, such as database connection strings, API endpoints, or other operational secrets, should be managed through environment variables.

-   **`.env.example`:** The `.env.example` file provides a template for required environment variables without exposing their actual values. Users should create a `.env` file (which is `.gitignore`d) based on this example and populate it with their specific, sensitive values.

## Access Control

Access to the TRUSTINT system and its underlying infrastructure (e.g., servers, database) must be strictly controlled using the principle of least privilege. Role-Based Access Control (RBAC) mechanisms are being developed (see `docs/db/migrations.md` for `role_permissions` table) to manage user permissions within the application.

## Data Integrity

The provenance ledger and checksum manifests (generated during export) are core components for ensuring data integrity and tamper-evidence within the TRUSTINT system. Regular verification of the provenance chain using `trustint doctor` is recommended.
