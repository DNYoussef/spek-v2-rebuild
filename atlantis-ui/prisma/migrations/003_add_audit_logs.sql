-- SPEK Platform v2 - Audit Logs Migration
-- Migration: 003_add_audit_logs.sql
-- Created: 2025-10-11
-- Description: Adds comprehensive audit logging for Loop 3 quality system

BEGIN;

-- ============================================
-- TABLE: audit_runs
-- ============================================

CREATE TABLE IF NOT EXISTS audit_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

    -- Audit identification
    audit_type VARCHAR(100) NOT NULL,
    audit_phase VARCHAR(100),

    -- Status tracking
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,

    -- Results summary
    total_checks INTEGER DEFAULT 0,
    passed_checks INTEGER DEFAULT 0,
    failed_checks INTEGER DEFAULT 0,
    warning_checks INTEGER DEFAULT 0,

    -- Scores
    theater_score DECIMAL(5,2),
    production_score DECIMAL(5,2),
    quality_score DECIMAL(5,2),
    overall_score DECIMAL(5,2),

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Constraints
    CONSTRAINT audit_runs_status_check
        CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
    CONSTRAINT audit_runs_audit_type_check
        CHECK (audit_type IN ('theater', 'production', 'quality', 'full'))
);

-- Indexes
CREATE INDEX idx_audit_runs_project_id ON audit_runs(project_id);
CREATE INDEX idx_audit_runs_audit_type ON audit_runs(audit_type);
CREATE INDEX idx_audit_runs_status ON audit_runs(status);
CREATE INDEX idx_audit_runs_created_at ON audit_runs(created_at DESC);
CREATE INDEX idx_audit_runs_overall_score ON audit_runs(overall_score DESC);

-- ============================================
-- TABLE: audit_findings
-- ============================================

CREATE TABLE IF NOT EXISTS audit_findings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_run_id UUID NOT NULL REFERENCES audit_runs(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

    -- Finding details
    category VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,

    -- Location
    file_path VARCHAR(1024),
    line_number INTEGER,
    column_number INTEGER,
    code_snippet TEXT,

    -- Recommendation
    recommendation TEXT,
    auto_fixable BOOLEAN DEFAULT false,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Constraints
    CONSTRAINT audit_findings_severity_check
        CHECK (severity IN ('info', 'low', 'medium', 'high', 'critical'))
);

-- Indexes
CREATE INDEX idx_audit_findings_audit_run_id ON audit_findings(audit_run_id);
CREATE INDEX idx_audit_findings_project_id ON audit_findings(project_id);
CREATE INDEX idx_audit_findings_category ON audit_findings(category);
CREATE INDEX idx_audit_findings_severity ON audit_findings(severity);
CREATE INDEX idx_audit_findings_file_path ON audit_findings(file_path);
CREATE INDEX idx_audit_findings_auto_fixable ON audit_findings(auto_fixable);
CREATE INDEX idx_audit_findings_created_at ON audit_findings(created_at DESC);

-- ============================================
-- TABLE: nasa_compliance_checks
-- ============================================

CREATE TABLE IF NOT EXISTS nasa_compliance_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_run_id UUID NOT NULL REFERENCES audit_runs(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

    -- Function details
    file_path VARCHAR(1024) NOT NULL,
    function_name VARCHAR(255) NOT NULL,
    line_count INTEGER NOT NULL,

    -- NASA Rule 10 compliance
    compliant BOOLEAN DEFAULT false,
    violation_type VARCHAR(100),

    -- Details
    has_assertions BOOLEAN DEFAULT false,
    assertion_count INTEGER DEFAULT 0,
    uses_recursion BOOLEAN DEFAULT false,
    has_fixed_bounds BOOLEAN DEFAULT true,

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT nasa_compliance_line_count_check
        CHECK (line_count > 0)
);

-- Indexes
CREATE INDEX idx_nasa_compliance_audit_run_id ON nasa_compliance_checks(audit_run_id);
CREATE INDEX idx_nasa_compliance_project_id ON nasa_compliance_checks(project_id);
CREATE INDEX idx_nasa_compliance_file_path ON nasa_compliance_checks(file_path);
CREATE INDEX idx_nasa_compliance_compliant ON nasa_compliance_checks(compliant);
CREATE INDEX idx_nasa_compliance_line_count ON nasa_compliance_checks(line_count DESC);

-- ============================================
-- TABLE: export_logs
-- ============================================

CREATE TABLE IF NOT EXISTS export_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

    -- Export details
    export_type VARCHAR(100) NOT NULL,
    destination_type VARCHAR(50) NOT NULL,
    destination_path VARCHAR(1024),

    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    -- Results
    files_exported INTEGER DEFAULT 0,
    total_size_bytes BIGINT DEFAULT 0,
    error TEXT,

    -- GitHub integration (if applicable)
    github_repo_url VARCHAR(500),
    github_commit_sha VARCHAR(40),

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Constraints
    CONSTRAINT export_logs_export_type_check
        CHECK (export_type IN ('github', 'folder', 'zip', 'docker')),
    CONSTRAINT export_logs_destination_type_check
        CHECK (destination_type IN ('github', 'local', 's3', 'docker')),
    CONSTRAINT export_logs_status_check
        CHECK (status IN ('pending', 'in_progress', 'completed', 'failed'))
);

-- Indexes
CREATE INDEX idx_export_logs_project_id ON export_logs(project_id);
CREATE INDEX idx_export_logs_export_type ON export_logs(export_type);
CREATE INDEX idx_export_logs_status ON export_logs(status);
CREATE INDEX idx_export_logs_created_at ON export_logs(created_at DESC);

-- ============================================
-- FUNCTIONS
-- ============================================

-- Function: Calculate overall audit score
CREATE OR REPLACE FUNCTION calculate_audit_score(
    p_total_checks INTEGER,
    p_passed_checks INTEGER,
    p_failed_checks INTEGER,
    p_warning_checks INTEGER
)
RETURNS DECIMAL(5,2) AS $$
BEGIN
    IF p_total_checks = 0 THEN
        RETURN 0.0;
    END IF;

    -- Calculate weighted score
    -- Passed: 1.0 weight
    -- Warning: 0.5 weight
    -- Failed: 0.0 weight
    RETURN ROUND(
        ((p_passed_checks * 1.0) + (p_warning_checks * 0.5)) / p_total_checks * 100,
        2
    );
END;
$$ LANGUAGE plpgsql;

-- Function: Update audit run scores
CREATE OR REPLACE FUNCTION update_audit_run_scores()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate overall score
    NEW.overall_score = calculate_audit_score(
        NEW.total_checks,
        NEW.passed_checks,
        NEW.failed_checks,
        NEW.warning_checks
    );

    -- Calculate duration if completed
    IF NEW.status = 'completed' AND NEW.started_at IS NOT NULL AND NEW.completed_at IS NOT NULL THEN
        NEW.duration_seconds = EXTRACT(EPOCH FROM (NEW.completed_at - NEW.started_at))::INTEGER;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers
CREATE TRIGGER update_audit_run_scores_trigger
    BEFORE INSERT OR UPDATE ON audit_runs
    FOR EACH ROW
    EXECUTE FUNCTION update_audit_run_scores();

COMMIT;

-- ============================================
-- VALIDATION
-- ============================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'audit_runs') THEN
        RAISE EXCEPTION 'Migration failed: audit_runs table not created';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'audit_findings') THEN
        RAISE EXCEPTION 'Migration failed: audit_findings table not created';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'nasa_compliance_checks') THEN
        RAISE EXCEPTION 'Migration failed: nasa_compliance_checks table not created';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'export_logs') THEN
        RAISE EXCEPTION 'Migration failed: export_logs table not created';
    END IF;

    RAISE NOTICE 'Migration 003_add_audit_logs.sql completed successfully';
END $$;
