INSERT INTO users (first_name, second_name, last_name, email, password_hash, phone, birth_date, is_system)
VALUES (
    'Admin', 'System', 'Admin',
    'admin@example.com',
    '$2b$12$6MVT5MtDplDEE0Juo.WVZeOWoN0PjCdb3ohGLNLOyWoAa8fFVWFb6', -- bcrypt hash of "password"
    '+10000000000',
    '1990-01-01',
    TRUE
)
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (first_name, second_name, last_name, email, password_hash, phone, birth_date)
VALUES (
    'User', 'User', 'Organizer',
    'organizer@example.com',
    '$2b$12$6MVT5MtDplDEE0Juo.WVZeOWoN0PjCdb3ohGLNLOyWoAa8fFVWFb6', -- bcrypt hash of "password"
    '+10000000001',
    '1992-02-02'
)
ON CONFLICT (email) DO NOTHING;