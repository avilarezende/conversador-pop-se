-- =============================================================================
-- SegPortal — Pedidos de terminais/aplicações (aprovação do administrador)
-- =============================================================================

BEGIN;

CREATE TABLE IF NOT EXISTS segportal_connection_request (
  request_id          SERIAL PRIMARY KEY,
  requester_username  VARCHAR(128) NOT NULL,
  connection_name     VARCHAR(256) NOT NULL,
  protocol            VARCHAR(32)  NOT NULL,
  hostname            VARCHAR(256) NOT NULL,
  port                INTEGER,
  username_hint       VARCHAR(128),
  justification       TEXT NOT NULL,
  status              VARCHAR(32)  NOT NULL DEFAULT 'pending'
                      CHECK (status IN ('pending', 'approved', 'rejected', 'cancelled')),
  reviewed_by         VARCHAR(128),
  review_notes        TEXT,
  reviewed_at         TIMESTAMPTZ,
  guacamole_connection_id INTEGER,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_segportal_req_status
  ON segportal_connection_request (status);

CREATE INDEX IF NOT EXISTS idx_segportal_req_user
  ON segportal_connection_request (requester_username);

COMMENT ON TABLE segportal_connection_request IS
  'Pedidos de conexão feitos por usuários; só liberados após aprovação do admin.';

COMMIT;
