    INSERT INTO roles (name)
    VALUES
        ('admin'),
        ('organizer'),
        ('coordinator'),
        ('speaker'),
        ('user')
    ON CONFLICT (name) DO NOTHING;