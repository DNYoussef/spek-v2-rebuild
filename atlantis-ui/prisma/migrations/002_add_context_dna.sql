-- SPEK Platform v2 - Context DNA Migration
-- Migration: 002_add_context_dna.sql
-- Created: 2025-10-11
-- Description: Adds Context DNA storage for cross-agent memory and artifact references

BEGIN;

-- ============================================
-- TABLE: context_dna_entries
-- ============================================

CREATE TABLE IF NOT EXISTS context_dna_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

    -- Context identification
    context_key VARCHAR(500) NOT NULL,
    context_type VARCHAR(100) NOT NULL,

    -- Content
    content TEXT NOT NULL,
    summary TEXT,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    accessed_at TIMESTAMP,
    access_count INTEGER DEFAULT 0,

    -- Artifact references (S3 paths, not full files)
    artifact_references JSONB DEFAULT '[]'::jsonb,

    -- Vector embedding ID (reference to Pinecone/vector DB)
    embedding_id VARCHAR(255),

    -- Tags for filtering
    tags TEXT[] DEFAULT '{}',

    -- Retention policy
    expires_at TIMESTAMP,
    retention_days INTEGER DEFAULT 30,

    -- Constraints
    CONSTRAINT context_dna_entries_project_key_unique UNIQUE (project_id, context_key)
);

-- Indexes
CREATE INDEX idx_context_dna_project_id ON context_dna_entries(project_id);
CREATE INDEX idx_context_dna_context_type ON context_dna_entries(context_type);
CREATE INDEX idx_context_dna_created_at ON context_dna_entries(created_at DESC);
CREATE INDEX idx_context_dna_accessed_at ON context_dna_entries(accessed_at DESC);
CREATE INDEX idx_context_dna_expires_at ON context_dna_entries(expires_at);
CREATE INDEX idx_context_dna_tags_gin ON context_dna_entries USING gin(tags);
CREATE INDEX idx_context_dna_artifact_refs_gin ON context_dna_entries USING gin(artifact_references);
CREATE INDEX idx_context_dna_summary_trgm ON context_dna_entries USING gin(summary gin_trgm_ops);

-- ============================================
-- TABLE: artifact_metadata
-- ============================================

CREATE TABLE IF NOT EXISTS artifact_metadata (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    context_dna_id UUID REFERENCES context_dna_entries(id) ON DELETE CASCADE,

    -- Artifact identification
    artifact_path VARCHAR(1024) NOT NULL,
    artifact_type VARCHAR(100) NOT NULL,

    -- Storage information
    storage_backend VARCHAR(50) NOT NULL DEFAULT 's3',
    storage_path VARCHAR(1024),

    -- File metadata
    file_size_bytes BIGINT,
    content_hash VARCHAR(128),
    mime_type VARCHAR(255),

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Constraints
    CONSTRAINT artifact_metadata_storage_backend_check
        CHECK (storage_backend IN ('s3', 'local', 'redis', 'pinecone'))
);

-- Indexes
CREATE INDEX idx_artifact_metadata_project_id ON artifact_metadata(project_id);
CREATE INDEX idx_artifact_metadata_context_dna_id ON artifact_metadata(context_dna_id);
CREATE INDEX idx_artifact_metadata_artifact_path ON artifact_metadata(artifact_path);
CREATE INDEX idx_artifact_metadata_artifact_type ON artifact_metadata(artifact_type);
CREATE INDEX idx_artifact_metadata_content_hash ON artifact_metadata(content_hash);
CREATE INDEX idx_artifact_metadata_created_at ON artifact_metadata(created_at DESC);

-- ============================================
-- TABLE: agent_memory
-- ============================================

CREATE TABLE IF NOT EXISTS agent_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,

    -- Memory details
    memory_key VARCHAR(500) NOT NULL,
    memory_type VARCHAR(100) NOT NULL,
    memory_value JSONB NOT NULL,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    accessed_at TIMESTAMP,
    access_count INTEGER DEFAULT 0,

    -- Expiration
    expires_at TIMESTAMP,

    -- Constraints
    CONSTRAINT agent_memory_project_agent_key_unique
        UNIQUE (project_id, agent_id, memory_key)
);

-- Indexes
CREATE INDEX idx_agent_memory_project_id ON agent_memory(project_id);
CREATE INDEX idx_agent_memory_agent_id ON agent_memory(agent_id);
CREATE INDEX idx_agent_memory_memory_type ON agent_memory(memory_type);
CREATE INDEX idx_agent_memory_created_at ON agent_memory(created_at DESC);
CREATE INDEX idx_agent_memory_expires_at ON agent_memory(expires_at);
CREATE INDEX idx_agent_memory_value_gin ON agent_memory USING gin(memory_value);

-- ============================================
-- FUNCTIONS
-- ============================================

-- Function: Update accessed_at on read
CREATE OR REPLACE FUNCTION update_context_dna_accessed()
RETURNS TRIGGER AS $$
BEGIN
    NEW.accessed_at = NOW();
    NEW.access_count = OLD.access_count + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function: Auto-delete expired Context DNA entries
CREATE OR REPLACE FUNCTION cleanup_expired_context_dna()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM context_dna_entries
    WHERE expires_at IS NOT NULL AND expires_at < NOW();

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function: Set expiration date based on retention_days
CREATE OR REPLACE FUNCTION set_context_dna_expiration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.retention_days IS NOT NULL THEN
        NEW.expires_at = NOW() + (NEW.retention_days || ' days')::INTERVAL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers
CREATE TRIGGER update_context_dna_updated_at
    BEFORE UPDATE ON context_dna_entries
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_context_dna_expiration_trigger
    BEFORE INSERT OR UPDATE OF retention_days ON context_dna_entries
    FOR EACH ROW
    EXECUTE FUNCTION set_context_dna_expiration();

CREATE TRIGGER update_artifact_metadata_updated_at
    BEFORE UPDATE ON artifact_metadata
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- SCHEDULED CLEANUP JOB (Example)
-- ============================================

-- Note: Requires pg_cron extension (optional)
-- CREATE EXTENSION IF NOT EXISTS pg_cron;
--
-- SELECT cron.schedule(
--     'cleanup-expired-context-dna',
--     '0 2 * * *', -- Run at 2 AM daily
--     'SELECT cleanup_expired_context_dna();'
-- );

COMMIT;

-- ============================================
-- VALIDATION
-- ============================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'context_dna_entries') THEN
        RAISE EXCEPTION 'Migration failed: context_dna_entries table not created';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'artifact_metadata') THEN
        RAISE EXCEPTION 'Migration failed: artifact_metadata table not created';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'agent_memory') THEN
        RAISE EXCEPTION 'Migration failed: agent_memory table not created';
    END IF;

    RAISE NOTICE 'Migration 002_add_context_dna.sql completed successfully';
END $$;
