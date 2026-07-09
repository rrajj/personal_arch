-- =========================================
-- Table 1: temp_pts_table (master PTS record)
-- =========================================
CREATE TABLE temp_pts_table (
    pts_id           TEXT PRIMARY KEY,
    project_summary  TEXT,
    project_name     TEXT NOT NULL,
    project_manager  TEXT
);

-- =========================================
-- Table 2: temp_csi_data (PTS -> CSI, one-to-many)
-- =========================================
CREATE TABLE temp_csi_data (
    id           BIGSERIAL PRIMARY KEY,
    pts_id       TEXT NOT NULL REFERENCES temp_pts_table(pts_id),
    csi_id       TEXT NOT NULL,
    app_name     TEXT,
    dsmt         TEXT,
    bhs_value    TEXT,
    change_type  TEXT,
    UNIQUE (pts_id, csi_id)
);

CREATE INDEX idx_temp_csi_data_pts_id ON temp_csi_data(pts_id);

-- =========================================
-- Table 3: temp_template_store (generated PPTs, versioned)
-- =========================================
CREATE TABLE temp_template_store (
    id            BIGSERIAL PRIMARY KEY,
    pts_id        TEXT NOT NULL REFERENCES temp_pts_table(pts_id),
    permit_type   TEXT NOT NULL CHECK (permit_type IN ('Build', 'Deploy')),
    version       INT NOT NULL,
    is_latest     BOOLEAN NOT NULL DEFAULT TRUE,
    status        TEXT NOT NULL DEFAULT 'Draft'
                  CHECK (status IN ('Draft', 'In Review', 'Approve')),
    ppt_blob      BYTEA NOT NULL,
    file_name     TEXT NOT NULL,
    file_size     INT,
    created_by    TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE (pts_id, permit_type, version)
);

-- Enforce exactly one "latest" version per (pts_id, permit_type)
CREATE UNIQUE INDEX idx_one_latest_per_pts_permit
    ON temp_template_store (pts_id, permit_type)
    WHERE is_latest = TRUE;

-- Helpful for lookups by pts_id + permit_type
CREATE INDEX idx_temp_template_store_pts_permit
    ON temp_template_store (pts_id, permit_type);
