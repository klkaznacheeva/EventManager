-- =========================================
-- EXTENSIONS
-- =========================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =========================================
-- USERS
-- =========================================

-- Пароль у ВСЕХ пользователей:
-- password

INSERT INTO users (
    id,
    first_name,
    last_name,
    email,
    password_hash,
    is_system,
    is_temporary,
    password_changed,
    created_at
)
VALUES
(
    gen_random_uuid(),
    'Александр',
    'Админов',
    'admin1@example.com',
    crypt('password', gen_salt('bf')),
    TRUE,
    FALSE,
    TRUE,
    NOW()
),
(
    gen_random_uuid(),
    'Мария',
    'Супервайзер',
    'admin2@example.com',
    crypt('password', gen_salt('bf')),
    TRUE,
    FALSE,
    TRUE,
    NOW()
),
(
    gen_random_uuid(),
    'Иван',
    'Организаторов',
    'organizer@example.com',
    crypt('password', gen_salt('bf')),
    FALSE,
    FALSE,
    TRUE,
    NOW()
),
(
    gen_random_uuid(),
    'Петр',
    'Участников',
    'user1@example.com',
    crypt('password', gen_salt('bf')),
    FALSE,
    FALSE,
    TRUE,
    NOW()
),
(
    gen_random_uuid(),
    'Анна',
    'Слушатель',
    'user2@example.com',
    crypt('password', gen_salt('bf')),
    FALSE,
    FALSE,
    TRUE,
    NOW()
);

-- =========================================
-- CATEGORIES
-- =========================================

INSERT INTO categories (
    id,
    name,
    created_at
)
VALUES
(
    gen_random_uuid(),
    'Информационные технологии',
    NOW()
),
(
    gen_random_uuid(),
    'Медицина',
    NOW()
);

-- =========================================
-- EVENTS
-- =========================================

INSERT INTO events (
    id,
    title,
    description,
    category_id,
    start_date,
    end_date,
    location,
    organizer_id,
    status,
    created_at
)
VALUES
(
    gen_random_uuid(),
    'Российский IT Форум 2026',
    'Крупное мероприятие для разработчиков, DevOps инженеров, архитекторов и руководителей IT-команд.',
    (SELECT id FROM categories WHERE name = 'Информационные технологии'),
    NOW() + INTERVAL '7 days',
    NOW() + INTERVAL '8 days',
    'Москва, Экспоцентр',
    (SELECT id FROM users WHERE email = 'organizer@example.com'),
    'draft',
    NOW()
),
(
    gen_random_uuid(),
    'Медицинский Конгресс 2026',
    'Современные подходы в диагностике, хирургии и цифровой медицине.',
    (SELECT id FROM categories WHERE name = 'Медицина'),
    NOW() + INTERVAL '14 days',
    NOW() + INTERVAL '15 days',
    'Санкт-Петербург, КВЦ',
    (SELECT id FROM users WHERE email = 'organizer@example.com'),
    'draft',
    NOW()
);

-- =========================================
-- EVENT PARTICIPANTS
-- =========================================

-- Организатор привязан к обоим мероприятиям

INSERT INTO event_participants (
    id,
    event_id,
    user_id,
    role_id,
    created_at
)
SELECT
    gen_random_uuid(),
    e.id,
    u.id,
    r.id,
    NOW()
FROM events e
JOIN users u
    ON u.email = 'organizer@example.com'
JOIN roles r
    ON r.name = 'organizer'
ON CONFLICT (event_id, user_id) DO NOTHING;

-- Обычные пользователи участвуют в мероприятиях

INSERT INTO event_participants (
    id,
    event_id,
    user_id,
    role_id,
    created_at
)
SELECT
    gen_random_uuid(),
    e.id,
    u.id,
    r.id,
    NOW()
FROM events e
JOIN users u
    ON u.email IN ('user1@example.com', 'user2@example.com')
JOIN roles r
    ON r.name = 'user'
ON CONFLICT (event_id, user_id) DO NOTHING;

-- =========================================
-- SESSIONS
-- =========================================

-- IT EVENT SESSIONS

INSERT INTO sessions (
    id,
    event_id,
    title,
    description,
    start_date,
    end_date,
    location,
    type,
    responsible_id,
    age_limit,
    status,
    created_at
)
VALUES
(
    gen_random_uuid(),
    (SELECT id FROM events WHERE title = 'Российский IT Форум 2026'),
    'AI и современные LLM системы',
    'Обсуждение современных языковых моделей, AI-агентов и автоматизации бизнеса.',
    NOW() + INTERVAL '7 days',
    NOW() + INTERVAL '7 days 2 hours',
    'Зал A1',
    'lecture',
    (SELECT id FROM users WHERE email = 'organizer@example.com'),
    16,
    'draft',
    NOW()
),
(
    gen_random_uuid(),
    (SELECT id FROM events WHERE title = 'Российский IT Форум 2026'),
    'DevOps и Kubernetes',
    'Практики CI/CD, Docker, Kubernetes и инфраструктура высокой нагрузки.',
    NOW() + INTERVAL '7 days 3 hours',
    NOW() + INTERVAL '7 days 5 hours',
    'Зал B2',
    'workshop',
    (SELECT id FROM users WHERE email = 'organizer@example.com'),
    16,
    'draft',
    NOW()
);

-- MEDICAL EVENT SESSIONS

INSERT INTO sessions (
    id,
    event_id,
    title,
    description,
    start_date,
    end_date,
    location,
    type,
    responsible_id,
    age_limit,
    status,
    created_at
)
VALUES
(
    gen_random_uuid(),
    (SELECT id FROM events WHERE title = 'Медицинский Конгресс 2026'),
    'Современная кардиология',
    'Новые методы диагностики и лечения сердечно-сосудистых заболеваний.',
    NOW() + INTERVAL '14 days',
    NOW() + INTERVAL '14 days 2 hours',
    'Конференц-зал №1',
    'lecture',
    (SELECT id FROM users WHERE email = 'organizer@example.com'),
    18,
    'draft',
    NOW()
),
(
    gen_random_uuid(),
    (SELECT id FROM events WHERE title = 'Медицинский Конгресс 2026'),
    'Цифровая медицина и AI',
    'Использование искусственного интеллекта в диагностике и медицинских системах.',
    NOW() + INTERVAL '14 days 3 hours',
    NOW() + INTERVAL '14 days 5 hours',
    'Конференц-зал №2',
    'panel',
    (SELECT id FROM users WHERE email = 'organizer@example.com'),
    18,
    'draft',
    NOW()
);

-- =========================================
-- SESSION PARTICIPANTS
-- =========================================

-- user1 участвует в IT сессии

INSERT INTO session_participants (
    id,
    session_id,
    user_id,
    role_id,
    created_at
)
SELECT
    gen_random_uuid(),
    s.id,
    u.id,
    r.id,
    NOW()
FROM sessions s
JOIN users u
    ON u.email = 'user1@example.com'
JOIN roles r
    ON r.name = 'user'
WHERE s.title = 'AI и современные LLM системы'
ON CONFLICT (session_id, user_id) DO NOTHING;

-- user2 участвует в медицинской сессии

INSERT INTO session_participants (
    id,
    session_id,
    user_id,
    role_id,
    created_at
)
SELECT
    gen_random_uuid(),
    s.id,
    u.id,
    r.id,
    NOW()
FROM sessions s
JOIN users u
    ON u.email = 'user2@example.com'
JOIN roles r
    ON r.name = 'user'
WHERE s.title = 'Современная кардиология'
ON CONFLICT (session_id, user_id) DO NOTHING;