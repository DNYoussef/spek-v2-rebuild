-- SPEK Platform v2 - Rollback for Initial Schema Migration
-- Rollback: 001_rollback.sql
-- Created: 2025-10-11
-- Description: Rolls back 001_initial_schema.sql migration

BEGIN;

-- ============================================
-- DROP TRIGGERS (in reverse order of creation)
-- ============================================

DROP TRIGGER IF EXISTS update_agents_updated_at ON agents;
DROP TRIGGER IF EXISTS update_projects_updated_at ON projects;

-- ============================================
-- DROP FUNCTIONS
-- ============================================

DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- ============================================
-- DROP TABLES (in reverse order of creation, respecting foreign keys)
-- ============================================

DROP TABLE IF EXISTS agent_logs CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS agents CASCADE;
DROP TABLE IF EXISTS projects CASCADE;

-- ============================================
-- DROP EXTENSIONS (optional - may be used by other migrations)
-- ============================================

-- Uncomment if you want to remove extensions completely
-- DROP EXTENSION IF EXISTS "pg_trgm";
-- DROP EXTENSION IF EXISTS "uuid-ossp";

COMMIT;

-- ============================================
-- VALIDATION
-- ============================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'projects') THEN
        RAISE EXCEPTION 'Rollback failed: projects table still exists';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'agents') THEN
        RAISE EXCEPTION 'Rollback failed: agents table still exists';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tasks') THEN
        RAISE EXCEPTION 'Rollback failed: tasks table still exists';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'agent_logs') THEN
        RAISE EXCEPTION 'Rollback failed: agent_logs table still exists';
    END IF;

    RAISE NOTICE 'Rollback 001_rollback.sql completed successfully';
END $$;
