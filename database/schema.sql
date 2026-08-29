-- ============================================================
-- DocXpert — Full Database Schema
-- SQLite (dev) / PostgreSQL (production)
-- ============================================================

-- Documents: every uploaded file gets a record here
CREATE TABLE IF NOT EXISTS documents (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id         TEXT    NOT NULL UNIQUE,          -- UUID for API references
    original_name   TEXT    NOT NULL,                  -- Original filename
    stored_name     TEXT    NOT NULL,                  -- Name on disk (UUID-based)
    file_type       TEXT    NOT NULL CHECK (file_type IN ('doc', 'docx', 'pdf')),
    file_size_bytes INTEGER NOT NULL,
    upload_path     TEXT    NOT NULL,                  -- Relative path in uploads/
    status          TEXT    NOT NULL DEFAULT 'uploaded' CHECK (status IN ('uploaded', 'processing', 'completed', 'failed')),
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Processing jobs: each operation on a document
CREATE TABLE IF NOT EXISTS processing_jobs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id          TEXT    NOT NULL UNIQUE,           -- UUID for API references
    document_id     INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    job_type        TEXT    NOT NULL CHECK (job_type IN ('convert', 'spelling', 'font_normalize', 'replace', 'compare', 'export')),
    status          TEXT    NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    input_params    TEXT,                               -- JSON string of job parameters
    result_path     TEXT,                               -- Path to result file (if any)
    error_message   TEXT,                               -- Error details (if failed)
    started_at      DATETIME,
    completed_at    DATETIME,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Spelling suggestions: individual corrections found by spell checker
CREATE TABLE IF NOT EXISTS spelling_suggestions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id          INTEGER NOT NULL REFERENCES processing_jobs(id) ON DELETE CASCADE,
    document_id     INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    original_text   TEXT    NOT NULL,                  -- The misspelled word/phrase
    suggested_text  TEXT    NOT NULL,                  -- The suggested correction
    context         TEXT,                               -- Surrounding sentence for context
    position        INTEGER,                            -- Character offset in document
    confidence      REAL    DEFAULT 0.0,               -- 0.0–1.0 confidence score
    accepted        INTEGER DEFAULT 0,                  -- 0 = pending, 1 = accepted, -1 = rejected
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Font reports: fonts detected during normalization
CREATE TABLE IF NOT EXISTS font_reports (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id          INTEGER NOT NULL REFERENCES processing_jobs(id) ON DELETE CASCADE,
    document_id     INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    font_name       TEXT    NOT NULL,                  -- Detected font name
    font_size       REAL,                               -- Detected size in pt
    occurrences     INTEGER NOT NULL DEFAULT 1,         -- How many times this font appears
    is_target       INTEGER NOT NULL DEFAULT 0,         -- 1 = this is the normalization target
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common lookups
CREATE INDEX IF NOT EXISTS idx_documents_file_id     ON documents(file_id);
CREATE INDEX IF NOT EXISTS idx_documents_status      ON documents(status);
CREATE INDEX IF NOT EXISTS idx_jobs_document_id       ON processing_jobs(document_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status            ON processing_jobs(status);
CREATE INDEX IF NOT EXISTS idx_spelling_job_id        ON spelling_suggestions(job_id);
CREATE INDEX IF NOT EXISTS idx_font_reports_job_id    ON font_reports(job_id);
