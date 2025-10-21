-- SPEK Platform v2 - Rollback for Context DNA Migration
-- Rollback: 002_rollback.sql
-- Created: 2025-10-11
-- Description: Rolls back 002_add_context_dna.sql migration

BEGIN;

-- ============================================
-- DROP TRIGGERS (in reverse order of creation)
-- ============================================

DROP TRIGGER IF EXISTS update_artifact_metadata_updated_at ON artifact_metadata;
DROP TRIGGER IF EXISTS set_context_dna_expiration_trigger ON context_dna_entries;
DROP TRIGGER IF EXISTS update_context_dna_updated_at ON context_dna_entries;

-- ============================================
-- DROP SCHEDULED JOBS (if pg_cron extension was used)
-- ============================================

-- Uncomment if pg_cron was enabled
-- SELECT cron.unschedule('cleanup-expired-context-dna');

-- ============================================
-- DROP FUNCTIONS
-- ============================================

DROP FUNCTION IF EXISTS set_context_dna_expiration() CASCADE;
DROP FUNCTION IF EXISTS cleanup_expired_context_dna() CASCADE;
DROP FUNCTION IF EXISTS update_context_dna_accessed() CASCADE;

-- ============================================
-- DROP TABLES (in reverse order of creation, respecting foreign keys)
-- ============================================

DROP TABLE IF EXISTS agent_memory CASCADE;
DROP TABLE IF EXISTS artifact_metadata CASCADE;
DROP TABLE IF EXISTS context_dna_entries CASCADE;

COMMIT;

-- ============================================
-- VALIDATION
-- ============================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'context_dna_entries') THEN
        RAISE EXCEPTION 'Rollback failed: context_dna_entries table still exists';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'artifact_metadata') THEN
        RAISE EXCEPTION 'Rollback failed: artifact_metadata table still exists';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'agent_memory') THEN
        RAISE EXCEPTION 'Rollback failed: agent_memory table still exists';
    END IF;

    RAISE NOTICE 'Rollback 002_rollback.sql completed successfully';
END $$;
