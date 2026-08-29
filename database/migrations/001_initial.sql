-- ============================================================
-- Migration 001: Initial Schema
-- Run with: sqlite3 database/docxpert.db < database/migrations/001_initial.sql
-- ============================================================

-- Migration tracking table
CREATE TABLE IF NOT EXISTS _migrations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    applied_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id         TEXT    NOT NULL UNIQUE,
    original_name   TEXT    NOT NULL,
    stored_name     TEXT    NOT NULL,
    file_type       TEXT    NOT NULL CHECK (file_type IN ('doc', 'docx', 'pdf')),
    file_size_bytes INTEGER NOT NULL,
    upload_path     TEXT    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'uploaded' CHECK (status IN ('uploaded', 'processing', 'completed', 'failed')),
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Processing jobs table
CREATE TABLE IF NOT EXISTS processing_jobs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id          TEXT    NOT NULL UNIQUE,
    document_id     INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    job_type        TEXT    NOT NULL CHECK (job_type IN ('convert', 'spelling', 'font_normalize', 'replace', 'compare', 'export')),
    status          TEXT    NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    input_params    TEXT,
    result_path     TEXT,
    error_message   TEXT,
    started_at      DATETIME,
    completed_at    DATETIME,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Spelling suggestions table
CREATE TABLE IF NOT EXISTS spelling_suggestions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id          INTEGER NOT NULL REFERENCES processing_jobs(id) ON DELETE CASCADE,
    document_id     INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    original_text   TEXT    NOT NULL,
    suggested_text  TEXT    NOT NULL,
    context         TEXT,
    position        INTEGER,
    confidence      REAL    DEFAULT 0.0,
    accepted        INTEGER DEFAULT 0,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Font reports table
CREATE TABLE IF NOT EXISTS font_reports (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id          INTEGER NOT NULL REFERENCES processing_jobs(id) ON DELETE CASCADE,
    document_id     INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    font_name       TEXT    NOT NULL,
    font_size       REAL,
    occurrences     INTEGER NOT NULL DEFAULT 1,
    is_target       INTEGER NOT NULL DEFAULT 0,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_documents_file_id     ON documents(file_id);
CREATE INDEX IF NOT EXISTS idx_documents_status      ON documents(status);
CREATE INDEX IF NOT EXISTS idx_jobs_document_id       ON processing_jobs(document_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status            ON processing_jobs(status);
CREATE INDEX IF NOT EXISTS idx_spelling_job_id        ON spelling_suggestions(job_id);
CREATE INDEX IF NOT EXISTS idx_font_reports_job_id    ON font_reports(job_id);

-- Record this migration
INSERT OR IGNORE INTO _migrations (name) VALUES ('001_initial');
