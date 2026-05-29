-- Таблица комнат чатов мероприятий
CREATE TABLE event_chat_rooms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL CHECK (type IN ('coordinators', 'speakers')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(event_id, type)
);

-- Таблица участников чатов мероприятий
CREATE TABLE event_chat_participants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_id UUID NOT NULL REFERENCES event_chat_rooms(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(chat_id, user_id)
);

-- Таблица сообщений чатов мероприятий
CREATE TABLE event_chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_id UUID NOT NULL REFERENCES event_chat_rooms(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Индексы
CREATE INDEX idx_event_chat_rooms_event_id ON event_chat_rooms(event_id);
CREATE INDEX idx_event_chat_participants_chat_id ON event_chat_participants(chat_id);
CREATE INDEX idx_event_chat_participants_user_id ON event_chat_participants(user_id);
CREATE INDEX idx_event_chat_messages_chat_id ON event_chat_messages(chat_id);
CREATE INDEX idx_event_chat_messages_created_at ON event_chat_messages(created_at);