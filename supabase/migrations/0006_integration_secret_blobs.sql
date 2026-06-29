-- 0006_integration_secret_blobs.sql
-- Purpose : Durable, per-user ENVELOPE-ENCRYPTED secret storage (P2). Postgres
--           twin of the SQLite `integration_secret_blobs` table in
--           app/database/schema.sql, used by EnvelopeSecretStore
--           (app/services/secret_store.py). Railway's filesystem is ephemeral
--           (wiped on every redeploy), so the local Fernet vault file would be
--           LOST; this table persists secrets in Postgres instead.
-- Status  : NOT APPLIED by the agent. The controller applies this via MCP.
-- Updated : 2026-06-29T19:26:17+09:00
-- No secrets, PII, keys, or real connection strings are present.
--
-- ENVELOPE SCHEME (why the DB host cannot read secrets)
--   ciphertext  = encrypt(plaintext_secret, DEK)   -- payload sealed under a per-user DEK
--   wrapped_dek = wrap(DEK, KEK)                    -- the DEK sealed under the master KEK
--   The master KEK (AUTOFOLIO_VAULT_KEY) lives ONLY in the app environment
--   (Railway) and is NEVER stored here. Only {wrapped_dek, ciphertext,
--   key_version} are persisted, so compromising this database WITHOUT the KEK
--   yields nothing: the DEK cannot be unwrapped, so the ciphertext cannot be
--   decrypted. Each user has a distinct random DEK (per-user isolation).
--   `key_version` records which KEK version wrapped the DEK, for future
--   KEK rotation (re-wrap the DEK; the ciphertext is never re-encrypted).
--
-- SECRET-BEARING COLUMNS: ONLY wrapped_dek + ciphertext (both encrypted). The
-- plaintext secret is NEVER written. The remaining columns are non-secret
-- metadata (enabled flag, masked hint like '****abcd', account label, scopes,
-- note, timestamps).
--
-- OWNERSHIP / RLS (server-only — copies the 0004_aux_tables.sql pattern):
-- This is a server/service-managed store. `user_id` is the server's text user
-- identifier (NOT an `auth.users` uuid FK): the EnvelopeSecretStore is keyed by
-- the same identifier the app passes, and the KEK that makes the row meaningful
-- lives only in the app, so clients must NEVER read this table directly.
-- Accordingly, RLS is ENABLED with NO member-facing policies: authenticated and
-- anon roles get no access; the server-runtime backend connection (the table
-- owner / service role, which is not subject to RLS unless FORCE RLS is set — it
-- is not) performs all reads and writes. This matches the 0003/0004 invariant
-- that server-only data is server-runtime only. Mirroring the client-facing
-- `integration_secret_metadata` RLS view (which carries an `auth.users` uuid FK)
-- is deferred to a later migration when real auth uuids are wired.

-- ---------------------------------------------------------------------------
-- integration_secret_blobs
-- UNIQUE (user_id, provider) is the arbiter for the store's
-- `ON CONFLICT (user_id, provider) DO UPDATE` upsert.
-- `enabled` is boolean: the store binds a Python bool (portable here).
-- `scopes` stays TEXT (json.dumps()/json.loads() round-trip; jsonb would change
-- the round-tripped type) with a '[]' default, matching the SQLite twin.
-- ---------------------------------------------------------------------------
create table if not exists public.integration_secret_blobs (
    id          bigserial   primary key,
    user_id     text        not null,
    provider    text        not null,
    wrapped_dek text        not null default '',
    ciphertext  text        not null default '',
    key_version integer     not null default 1,
    enabled     boolean     not null default true,
    masked_hint text,
    account_label text,
    scopes      text        not null default '[]',
    note        text,
    created_at  timestamptz not null default now(),
    updated_at  timestamptz not null default now(),
    unique (user_id, provider)
);

create index if not exists idx_integration_secret_blobs_user
    on public.integration_secret_blobs (user_id);

alter table public.integration_secret_blobs enable row level security;
