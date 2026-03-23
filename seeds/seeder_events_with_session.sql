INSERT INTO events (title, description, start_date, end_date, organizer_id, status)
VALUES (
    'Tech Conference 2026',
    'Annual tech conference',
    NOW() + INTERVAL '1 day',
    NOW() + INTERVAL '2 days',
    (SELECT id FROM users WHERE email = 'organizer@example.com'),
    'draft'
);

INSERT INTO events (title, description, start_date, end_date, organizer_id, status)
VALUES (
    'Startup Meetup',
    'Local startup meetup',
    NOW() + INTERVAL '3 days',
    NOW() + INTERVAL '3 days' + INTERVAL '4 hours',
    (SELECT id FROM users WHERE email = 'organizer@example.com'),
    'draft'
);

INSERT INTO sessions (event_id, title, description, start_date, end_date, responsible_id, status)
VALUES
(
    (SELECT id FROM events WHERE title='Tech Conference 2026'),
    'Tech Conference 2026 - Opening Session',
    'Opening session description',
    NOW() + INTERVAL '1 day',
    NOW() + INTERVAL '1 day' + INTERVAL '2 hours',
    (SELECT id FROM users WHERE email='organizer@example.com'),
    'draft'
),
(
    (SELECT id FROM events WHERE title='Startup Meetup'),
    'Startup Meetup - Opening Session',
    'Opening session description',
    NOW() + INTERVAL '3 days',
    NOW() + INTERVAL '3 days' + INTERVAL '2 hours',
    (SELECT id FROM users WHERE email='organizer@example.com'),
    'draft'
);

INSERT INTO event_participants (event_id, user_id, role_id)
SELECT e.id, u.id, r.id
FROM events e
JOIN users u ON u.email = 'organizer@example.com'
JOIN roles r ON r.name = 'Organizer'
WHERE e.title IN ('Tech Conference 2026','Startup Meetup')
ON CONFLICT (event_id, user_id) DO NOTHING;