-- 2026-10-14: claim extras. details = JSON (new practice name/city/country/website, featured interest, note).
-- claims.status values: pending (email not confirmed) | email_confirmed (needs manual ownership check) |
-- verified (email confirmed + ownership signal) | approved | rejected.
ALTER TABLE claims ADD COLUMN details TEXT;
