-- =============================================================================
-- SegPortal — Navegador HTML padrão para TODOS os usuários
-- Aplicado automaticamente pelo bootstrap-segportal.sh no boot do stack.
-- Idempotente.
-- =============================================================================

BEGIN;

-- Grupo que recebe o navegador padrão
INSERT INTO guacamole_entity (name, type)
SELECT 'segportal-browser-default', 'USER_GROUP'
WHERE NOT EXISTS (
  SELECT 1 FROM guacamole_entity WHERE name = 'segportal-browser-default' AND type = 'USER_GROUP'
);

INSERT INTO guacamole_user_group (entity_id, disabled)
SELECT e.entity_id, FALSE
FROM guacamole_entity e
WHERE e.name = 'segportal-browser-default' AND e.type = 'USER_GROUP'
  AND NOT EXISTS (SELECT 1 FROM guacamole_user_group ug WHERE ug.entity_id = e.entity_id);

-- Inclui TODOS os usuários existentes no grupo do navegador
INSERT INTO guacamole_user_group_member (user_group_id, member_entity_id)
SELECT ug.user_group_id, ue.entity_id
FROM guacamole_user_group ug
JOIN guacamole_entity ge ON ge.entity_id = ug.entity_id AND ge.name = 'segportal-browser-default'
JOIN guacamole_entity ue ON ue.type = 'USER'
WHERE NOT EXISTS (
  SELECT 1 FROM guacamole_user_group_member m
  WHERE m.user_group_id = ug.user_group_id AND m.member_entity_id = ue.entity_id
);

-- Vincula grupos de papel ao grupo do navegador (herança para LDAP/membros futuros)
INSERT INTO guacamole_user_group_member (user_group_id, member_entity_id)
SELECT ug.user_group_id, ge_member.entity_id
FROM guacamole_user_group ug
JOIN guacamole_entity ge ON ge.entity_id = ug.entity_id AND ge.name = 'segportal-browser-default'
JOIN guacamole_entity ge_member ON ge_member.type = 'USER_GROUP'
  AND ge_member.name IN ('segportal-users', 'segportal-admins')
WHERE NOT EXISTS (
  SELECT 1 FROM guacamole_user_group_member m
  WHERE m.user_group_id = ug.user_group_id AND m.member_entity_id = ge_member.entity_id
);

-- Conexão VNC → serviço web-browser (Firefox ESR + x11vnc)
INSERT INTO guacamole_connection (connection_name, protocol, max_connections, max_connections_per_user)
SELECT 'Navegador Web SegPortal', 'vnc', 50, 2
WHERE NOT EXISTS (
  SELECT 1 FROM guacamole_connection WHERE connection_name = 'Navegador Web SegPortal'
);

UPDATE guacamole_connection
SET max_connections = 50,
    max_connections_per_user = 2,
    protocol = 'vnc'
WHERE connection_name = 'Navegador Web SegPortal';

-- Parâmetros VNC (senha deve coincidir com VNC_PASSWORD do container web-browser)
INSERT INTO guacamole_connection_parameter (connection_id, parameter_name, parameter_value)
SELECT c.connection_id, p.name, p.value
FROM guacamole_connection c
CROSS JOIN (VALUES
  ('hostname', 'web-browser'),
  ('port', '5900'),
  ('password', 'segport1'),
  ('read-only', 'false'),
  ('swap-red-blue', 'false'),
  ('cursor', 'local'),
  ('color-depth', '24'),
  ('clipboard-encoding', 'UTF-8'),
  ('disable-paste', 'false'),
  ('disable-copy', 'false'),
  ('enable-sftp', 'false')
) AS p(name, value)
WHERE c.connection_name = 'Navegador Web SegPortal'
  AND NOT EXISTS (
    SELECT 1 FROM guacamole_connection_parameter cp
    WHERE cp.connection_id = c.connection_id AND cp.parameter_name = p.name
  );

-- Atualiza parâmetros críticos se já existirem (corrige deploys antigos)
UPDATE guacamole_connection_parameter cp
SET parameter_value = v.value
FROM guacamole_connection c
JOIN (VALUES
  ('hostname', 'web-browser'),
  ('port', '5900'),
  ('password', 'segport1')
) AS v(name, value) ON TRUE
WHERE c.connection_name = 'Navegador Web SegPortal'
  AND cp.connection_id = c.connection_id
  AND cp.parameter_name = v.name
  AND cp.parameter_value IS DISTINCT FROM v.value;

-- READ para o grupo segportal-browser-default
INSERT INTO guacamole_connection_permission (entity_id, connection_id, permission)
SELECT e.entity_id, c.connection_id, 'READ'::guacamole_object_permission_type
FROM guacamole_entity e
JOIN guacamole_connection c ON c.connection_name = 'Navegador Web SegPortal'
WHERE e.name = 'segportal-browser-default' AND e.type = 'USER_GROUP'
  AND NOT EXISTS (
    SELECT 1 FROM guacamole_connection_permission cp
    WHERE cp.entity_id = e.entity_id AND cp.connection_id = c.connection_id
      AND cp.permission = 'READ'::guacamole_object_permission_type
  );

-- READ aos grupos de papel
INSERT INTO guacamole_connection_permission (entity_id, connection_id, permission)
SELECT e.entity_id, c.connection_id, 'READ'::guacamole_object_permission_type
FROM guacamole_entity e
JOIN guacamole_connection c ON c.connection_name = 'Navegador Web SegPortal'
WHERE e.type = 'USER_GROUP' AND e.name IN ('segportal-users', 'segportal-admins')
  AND NOT EXISTS (
    SELECT 1 FROM guacamole_connection_permission cp
    WHERE cp.entity_id = e.entity_id AND cp.connection_id = c.connection_id
      AND cp.permission = 'READ'::guacamole_object_permission_type
  );

-- READ direto a TODOS os usuários
INSERT INTO guacamole_connection_permission (entity_id, connection_id, permission)
SELECT e.entity_id, c.connection_id, 'READ'::guacamole_object_permission_type
FROM guacamole_entity e
JOIN guacamole_connection c ON c.connection_name = 'Navegador Web SegPortal'
WHERE e.type = 'USER'
  AND NOT EXISTS (
    SELECT 1 FROM guacamole_connection_permission cp
    WHERE cp.entity_id = e.entity_id AND cp.connection_id = c.connection_id
      AND cp.permission = 'READ'::guacamole_object_permission_type
  );

COMMIT;
