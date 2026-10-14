-- ScannerFinder claim flow. Plan: research/claim-flow-plan.md (2026-10-14).
-- Usage tracking (views, clicks, searches) lives in Matomo, not here.

-- Claims, sessions, profiles, payments.
CREATE TABLE claims (
  id TEXT PRIMARY KEY,
  listing_slug TEXT,              -- NULL = new practice, not yet in the directory
  status TEXT NOT NULL DEFAULT 'pending', -- pending | verified | approved | rejected
  email TEXT NOT NULL,
  name TEXT NOT NULL,
  role TEXT,
  verify_method TEXT,             -- invite_token | domain_email | known_email | manual
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX claims_slug ON claims (listing_slug);
CREATE INDEX claims_status ON claims (status);

CREATE TABLE sessions (
  token_hash TEXT PRIMARY KEY,
  claim_id TEXT NOT NULL REFERENCES claims(id),
  purpose TEXT NOT NULL,          -- magic_link | session
  expires_at TEXT NOT NULL
);

CREATE TABLE profile_public (
  claim_id TEXT NOT NULL REFERENCES claims(id),
  version INTEGER NOT NULL,
  data TEXT NOT NULL,             -- JSON
  consents TEXT NOT NULL,         -- JSON: wellness, accuracy, terms, marketing
  submitted_at TEXT NOT NULL,
  reviewed_at TEXT,
  PRIMARY KEY (claim_id, version)
);

CREATE TABLE profile_private (
  claim_id TEXT NOT NULL REFERENCES claims(id),
  block TEXT NOT NULL,            -- device | economics | clients | certification
  data TEXT NOT NULL,             -- JSON
  aggregate_consent INTEGER NOT NULL,
  submitted_at TEXT NOT NULL,
  PRIMARY KEY (claim_id, block)
);

CREATE TABLE payments (
  claim_id TEXT NOT NULL REFERENCES claims(id),
  stripe_customer TEXT,
  subscription_id TEXT PRIMARY KEY,
  tier TEXT NOT NULL,
  status TEXT NOT NULL,
  period_end TEXT
);
