-- =============================================================================
-- SegPortal AQNE — Papéis admin e usuário (Guacamole JDBC PostgreSQL 1.5.x)
-- Aplicar APÓS o schema oficial (001/002).
-- =============================================================================
-- Admin  → grupo segportal-admins (+ guacadmin)
-- Usuário → grupo segportal-users (+ usuário demo "usuario" / senha "usuario")
-- =============================================================================

BEGIN;

-- Grupos de papéis
INSERT INTO guacamole_entity (name, type)
SELECT 'segportal-admins', 'USER_GROUP'
WHERE NOT EXISTS (
  SELECT 1 FROM guacamole_entity WHERE name = 'segportal-admins' AND type = 'USER_GROUP'
);

INSERT INTO guacamole_entity (name, type)
SELECT 'segportal-users', 'USER_GROUP'
WHERE NOT EXISTS (
  SELECT 1 FROM guacamole_entity WHERE name = 'segportal-users' AND type = 'USER_GROUP'
);

INSERT INTO guacamole_user_group (entity_id, disabled)
SELECT e.entity_id, FALSE
FROM guacamole_entity e
WHERE e.name = 'segportal-admins' AND e.type = 'USER_GROUP'
  AND NOT EXISTS (SELECT 1 FROM guacamole_user_group ug WHERE ug.entity_id = e.entity_id);

INSERT INTO guacamole_user_group (entity_id, disabled)
SELECT e.entity_id, FALSE
FROM guacamole_entity e
WHERE e.name = 'segportal-users' AND e.type = 'USER_GROUP'
  AND NOT EXISTS (SELECT 1 FROM guacamole_user_group ug WHERE ug.entity_id = e.entity_id);

-- Permissões de SISTEMA do grupo admin (visão de sessões via ADMINISTER)
INSERT INTO guacamole_system_permission (entity_id, permission)
SELECT e.entity_id, p.permission::guacamole_system_permission_type
FROM guacamole_entity e
CROSS JOIN (VALUES
  ('ADMINISTER'),
  ('CREATE_CONNECTION'),
  ('CREATE_CONNECTION_GROUP'),
  ('CREATE_SHARING_PROFILE'),
  ('CREATE_USER'),
  ('CREATE_USER_GROUP')
) AS p(permission)
WHERE e.name = 'segportal-admins' AND e.type = 'USER_GROUP'
  AND NOT EXISTS (
    SELECT 1 FROM guacamole_system_permission sp
    WHERE sp.entity_id = e.entity_id
      AND sp.permission = p.permission::guacamole_system_permission_type
  );

-- Usuário demo "usuario" — senha: usuario
-- salt = A1B2C3D4...EFF00
-- hash = SHA-256(UTF-8(password) || salt)
INSERT INTO guacamole_entity (name, type)
SELECT 'usuario', 'USER'
WHERE NOT EXISTS (
  SELECT 1 FROM guacamole_entity WHERE name = 'usuario' AND type = 'USER'
);

INSERT INTO guacamole_user (
  entity_id, password_hash, password_salt, password_date, disabled, expired, timezone
)
SELECT
  e.entity_id,
  decode('0D04D05B76354021AB68CD037911CEB212D3C39BB6CC369B862BDE5E21D83977', 'hex'),
  decode('A1B2C3D4E5F60718293A4B5C6D7E8F90112233445566778899AABBCCDDEEFF00', 'hex'),
  CURRENT_TIMESTAMP,
  FALSE,
  FALSE,
  'America/Maceio'
FROM guacamole_entity e
WHERE e.name = 'usuario' AND e.type = 'USER'
  AND NOT EXISTS (SELECT 1 FROM guacamole_user u WHERE u.entity_id = e.entity_id);

-- Atualiza hash caso o usuário já exista (idempotente)
UPDATE guacamole_user u
SET
  password_hash = decode('0D04D05B76354021AB68CD037911CEB212D3C39BB6CC369B862BDE5E21D83977', 'hex'),
  password_salt = decode('A1B2C3D4E5F60718293A4B5C6D7E8F90112233445566778899AABBCCDDEEFF00', 'hex'),
  password_date = CURRENT_TIMESTAMP
FROM guacamole_entity e
WHERE u.entity_id = e.entity_id AND e.name = 'usuario' AND e.type = 'USER';

-- Membership: usuario → segportal-users (SEM permissões de sistema)
INSERT INTO guacamole_user_group_member (user_group_id, member_entity_id)
SELECT ug.user_group_id, ue.entity_id
FROM guacamole_user_group ug
JOIN guacamole_entity ge ON ge.entity_id = ug.entity_id AND ge.name = 'segportal-users'
JOIN guacamole_entity ue ON ue.name = 'usuario' AND ue.type = 'USER'
WHERE NOT EXISTS (
  SELECT 1 FROM guacamole_user_group_member m
  WHERE m.user_group_id = ug.user_group_id AND m.member_entity_id = ue.entity_id
);

-- Membership: guacadmin → segportal-admins
INSERT INTO guacamole_user_group_member (user_group_id, member_entity_id)
SELECT ug.user_group_id, ue.entity_id
FROM guacamole_user_group ug
JOIN guacamole_entity ge ON ge.entity_id = ug.entity_id AND ge.name = 'segportal-admins'
JOIN guacamole_entity ue ON ue.name = 'guacadmin' AND ue.type = 'USER'
WHERE NOT EXISTS (
  SELECT 1 FROM guacamole_user_group_member m
  WHERE m.user_group_id = ug.user_group_id AND m.member_entity_id = ue.entity_id
);

-- Grupos de negócio (conexões por perfil de cliente)
INSERT INTO guacamole_entity (name, type)
SELECT g.name, 'USER_GROUP'
FROM (VALUES
  ('segportal-financeiro'),
  ('segportal-consulta'),
  ('segportal-externo')
) AS g(name)
WHERE NOT EXISTS (
  SELECT 1 FROM guacamole_entity e WHERE e.name = g.name AND e.type = 'USER_GROUP'
);

INSERT INTO guacamole_user_group (entity_id, disabled)
SELECT e.entity_id, FALSE
FROM guacamole_entity e
WHERE e.name IN ('segportal-financeiro', 'segportal-consulta', 'segportal-externo')
  AND e.type = 'USER_GROUP'
  AND NOT EXISTS (SELECT 1 FROM guacamole_user_group ug WHERE ug.entity_id = e.entity_id);

-- Usuário normal no grupo financeiro (exemplo de contexto restrito)
INSERT INTO guacamole_user_group_member (user_group_id, member_entity_id)
SELECT ug.user_group_id, ue.entity_id
FROM guacamole_user_group ug
JOIN guacamole_entity ge ON ge.entity_id = ug.entity_id AND ge.name = 'segportal-financeiro'
JOIN guacamole_entity ue ON ue.name = 'usuario' AND ue.type = 'USER'
WHERE NOT EXISTS (
  SELECT 1 FROM guacamole_user_group_member m
  WHERE m.user_group_id = ug.user_group_id AND m.member_entity_id = ue.entity_id
);

COMMIT;
