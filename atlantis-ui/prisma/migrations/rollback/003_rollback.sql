-- SPEK Platform v2 - Rollback for Audit Logs Migration
-- Rollback: 003_rollback.sql
-- Created: 2025-10-11
-- Description: Rolls back 003_add_audit_logs.sql migration

BEGIN;

-- ============================================
-- DROP TRIGGERS (in reverse order of creation)
-- ============================================

DROP TRIGGER IF EXISTS update_audit_run_scores_trigger ON audit_runs;

-- ============================================
-- DROP FUNCTIONS
-- ============================================

DROP FUNCTION IF EXISTS update_audit_run_scores() CASCADE;
DROP FUNCTION IF EXISTS calculate_audit_score(INTEGER, INTEGER, INTEGER, INTEGER) CASCADE;

-- ============================================
-- DROP TABLES (in reverse order of creation, respecting foreign keys)
-- ============================================

DROP TABLE IF EXISTS export_logs CASCADE;
DROP TABLE IF EXISTS nasa_compliance_checks CASCADE;
DROP TABLE IF EXISTS audit_findings CASCADE;
DROP TABLE IF EXISTS audit_runs CASCADE;

COMMIT;

-- ============================================
-- VALIDATION
-- ============================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'audit_runs') THEN
        RAISE EXCEPTION 'Rollback failed: audit_runs table still exists';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'audit_findings') THEN
        RAISE EXCEPTION 'Rollback failed: audit_findings table still exists';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'nasa_compliance_checks') THEN
        RAISE EXCEPTION 'Rollback failed: nasa_compliance_checks table still exists';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'export_logs') THEN
        RAISE EXCEPTION 'Rollback failed: export_logs table still exists';
    END IF;

    RAISE NOTICE 'Rollback 003_rollback.sql completed successfully';
END $$;
