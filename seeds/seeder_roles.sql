INSERT INTO roles (name)
VALUES
    ('admin'),
    ('organizer'),
    ('coordinator'),
    ('user')
ON CONFLICT (name) DO NOTHING;