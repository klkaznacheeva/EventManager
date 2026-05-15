ALTER TABLE users
ADD COLUMN IF NOT EXISTS is_temporary BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE users
ADD COLUMN IF NOT EXISTS password_changed BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE users
ADD COLUMN IF NOT EXISTS invited_by UUID NULL REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE session_participants
ADD COLUMN IF NOT EXISTS role_id UUID NULL REFERENCES roles(id);


INSERT INTO roles (name)
SELECT 'speaker'
WHERE NOT EXISTS (
    SELECT 1
    FROM roles
    WHERE name = 'speaker'
);


CREATE INDEX IF NOT EXISTS idx_session_participants_role_id
ON session_participants(role_id);

CREATE INDEX IF NOT EXISTS idx_users_is_temporary
ON users(is_temporary);