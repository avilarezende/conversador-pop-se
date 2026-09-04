-- =============================================================================
-- SegPortal — Navegador HTML padrão para TODOS os usuários
-- Aplicar após 001/002 e 003-segportal-roles.sql
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

-- Inclui usuários conhecidos no grupo do navegador
INSERT INTO guacamole_user_group_member (user_group_id, member_entity_id)
SELECT ug.user_group_id, ue.entity_id
FROM guacamole_user_group ug
JOIN guacamole_entity ge ON ge.entity_id = ug.entity_id AND ge.name = 'segportal-browser-default'
JOIN guacamole_entity ue ON ue.type = 'USER' AND ue.name IN ('guacadmin', 'usuario')
WHERE NOT EXISTS (
  SELECT 1 FROM guacamole_user_group_member m
  WHERE m.user_group_id = ug.user_group_id AND m.member_entity_id = ue.entity_id
);

-- Também vincula grupos de papel ao grupo do navegador (herança)
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

-- Conexão VNC → pod web-browser (Firefox)
INSERT INTO guacamole_connection (connection_name, protocol, max_connections, max_connections_per_user)
SELECT 'Navegador Web SegPortal', 'vnc', NULL, 1
WHERE NOT EXISTS (
  SELECT 1 FROM guacamole_connection WHERE connection_name = 'Navegador Web SegPortal'
);

-- Parâmetros VNC
INSERT INTO guacamole_connection_parameter (connection_id, parameter_name, parameter_value)
SELECT c.connection_id, p.name, p.value
FROM guacamole_connection c
CROSS JOIN (VALUES
  ('hostname', 'web-browser'),
  ('port', '5900'),
  ('read-only', 'false'),
  ('swap-red-blue', 'false'),
  ('cursor', 'local'),
  ('color-depth', '24'),
  ('clipboard-encoding', 'UTF-8')
) AS p(name, value)
WHERE c.connection_name = 'Navegador Web SegPortal'
  AND NOT EXISTS (
    SELECT 1 FROM guacamole_connection_parameter cp
    WHERE cp.connection_id = c.connection_id AND cp.parameter_name = p.name
  );

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

-- READ também direto aos grupos de papel (redundância segura)
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

COMMIT;
