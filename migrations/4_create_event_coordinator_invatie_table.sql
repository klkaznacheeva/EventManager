CREATE TABLE IF NOT EXISTS event_coordinator_invites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,

    token VARCHAR(255) NOT NULL UNIQUE,

    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    is_active BOOLEAN DEFAULT TRUE,

    expires_at TIMESTAMPTZ NULL,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_event_coordinator_invites_event_id
ON event_coordinator_invites(event_id);

CREATE INDEX IF NOT EXISTS idx_event_coordinator_invites_token
ON event_coordinator_invites(token);