CREATE TABLE checklist_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,

    title VARCHAR(255) NOT NULL,
    description TEXT,

    deadline TIMESTAMP WITH TIME ZONE,

    created_by UUID REFERENCES users(id),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_checklist_tasks_entity
ON checklist_tasks(entity_type, entity_id);


CREATE TABLE checklist_task_assignees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    task_id UUID REFERENCES checklist_tasks(id) ON DELETE CASCADE,

    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    is_completed BOOLEAN DEFAULT FALSE,

    completed_at TIMESTAMP WITH TIME ZONE,

    comment TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(task_id, user_id)
);

CREATE INDEX idx_checklist_assignee_user
ON checklist_task_assignees(user_id);