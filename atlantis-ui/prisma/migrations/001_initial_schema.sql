-- SPEK Platform v2 - Initial Schema Migration
-- Migration: 001_initial_schema.sql
-- Created: 2025-10-11
-- Description: Creates initial database schema for projects, agents, and tasks

BEGIN;

-- ============================================
-- EXTENSIONS
-- ============================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable full-text search
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================
-- TABLE: projects
-- ============================================

CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    path VARCHAR(1024) NOT NULL,

    -- Status tracking
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    current_loop INTEGER DEFAULT 1,
    current_phase VARCHAR(100),

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,

    -- Configuration
    enable_3d BOOLEAN DEFAULT true,
    enable_animations BOOLEAN DEFAULT true,

    -- Constraints
    CONSTRAINT projects_status_check CHECK (status IN ('pending', 'in_progress', 'paused', 'completed', 'failed')),
    CONSTRAINT projects_current_loop_check CHECK (current_loop BETWEEN 1 AND 3)
);

-- Indexes
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_at ON projects(created_at DESC);
CREATE INDEX idx_projects_current_loop ON projects(current_loop);
CREATE INDEX idx_projects_name_trgm ON projects USING gin(name gin_trgm_ops);

-- ============================================
-- TABLE: agents
-- ============================================

CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

    -- Agent identification
    agent_type VARCHAR(100) NOT NULL,
    agent_id VARCHAR(255) NOT NULL,

    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'idle',
    last_heartbeat TIMESTAMP,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Configuration
    config JSONB DEFAULT '{}'::jsonb,

    -- Constraints
    CONSTRAINT agents_status_check CHECK (status IN ('idle', 'active', 'paused', 'completed', 'failed')),
    CONSTRAINT agents_project_agent_unique UNIQUE (project_id, agent_id)
);

-- Indexes
CREATE INDEX idx_agents_project_id ON agents(project_id);
CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_agents_agent_type ON agents(agent_type);
CREATE INDEX idx_agents_config_gin ON agents USING gin(config);

-- ============================================
-- TABLE: tasks
-- ============================================

CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
    parent_task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,

    -- Task details
    title VARCHAR(500) NOT NULL,
    description TEXT,
    task_type VARCHAR(100) NOT NULL,

    -- Status tracking
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    priority INTEGER DEFAULT 5,
    progress DECIMAL(5,2) DEFAULT 0.00,

    -- Timing
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_duration_minutes INTEGER,
    actual_duration_minutes INTEGER,

    -- Results
    result JSONB,
    error TEXT,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Constraints
    CONSTRAINT tasks_status_check CHECK (status IN ('pending', 'in_progress', 'paused', 'completed', 'failed', 'cancelled')),
    CONSTRAINT tasks_priority_check CHECK (priority BETWEEN 1 AND 10),
    CONSTRAINT tasks_progress_check CHECK (progress BETWEEN 0 AND 100)
);

-- Indexes
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_agent_id ON tasks(agent_id);
CREATE INDEX idx_tasks_parent_task_id ON tasks(parent_task_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority DESC);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX idx_tasks_task_type ON tasks(task_type);
CREATE INDEX idx_tasks_metadata_gin ON tasks USING gin(metadata);

-- ============================================
-- TABLE: agent_logs
-- ============================================

CREATE TABLE IF NOT EXISTS agent_logs (
    id BIGSERIAL PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,

    -- Log details
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Constraints
    CONSTRAINT agent_logs_level_check CHECK (level IN ('debug', 'info', 'warn', 'error', 'fatal'))
);

-- Indexes
CREATE INDEX idx_agent_logs_project_id ON agent_logs(project_id);
CREATE INDEX idx_agent_logs_agent_id ON agent_logs(agent_id);
CREATE INDEX idx_agent_logs_task_id ON agent_logs(task_id);
CREATE INDEX idx_agent_logs_level ON agent_logs(level);
CREATE INDEX idx_agent_logs_created_at ON agent_logs(created_at DESC);

-- ============================================
-- FUNCTIONS
-- ============================================

-- Function: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agents_updated_at
    BEFORE UPDATE ON agents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- INITIAL DATA
-- ============================================

-- Insert example project (optional - remove in production)
-- INSERT INTO projects (name, description, path, status)
-- VALUES ('Example Project', 'Initial example project for testing', '/path/to/project', 'pending');

COMMIT;

-- ============================================
-- VALIDATION
-- ============================================

-- Verify tables were created
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'projects') THEN
        RAISE EXCEPTION 'Migration failed: projects table not created';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'agents') THEN
        RAISE EXCEPTION 'Migration failed: agents table not created';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tasks') THEN
        RAISE EXCEPTION 'Migration failed: tasks table not created';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'agent_logs') THEN
        RAISE EXCEPTION 'Migration failed: agent_logs table not created';
    END IF;

    RAISE NOTICE 'Migration 001_initial_schema.sql completed successfully';
END $$;
