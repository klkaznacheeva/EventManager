from sqladmin import ModelView
from wtforms import Form, PasswordField, StringField, BooleanField, DateField
from app.models.user import User
from app.core.security import hash_password

# Создаём кастомную форму для SQLAdmin
class UserForm(Form):
    email = StringField("Email")
    first_name = StringField("Имя")
    second_name = StringField("Отчество")
    last_name = StringField("Фамилия")
    phone = StringField("Телефон")
    birth_date = DateField("Дата рождения")
    is_system = BooleanField("Системный пользователь")
    is_active = BooleanField("Активен")
    password = PasswordField("Пароль")  # вот здесь реально поле появляется

class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"

    # Используем кастомную форму
    form = UserForm

    # Исключаем поля, которые создаются системой
    form_excluded_columns = ["password_hash", "created_at", "updated_at"]

    column_list = [
        User.email,
        User.first_name,
        User.second_name,
        User.last_name,
        User.phone,
        User.birth_date,
        User.is_system,
        User.is_active,
    ]

    column_labels = {
        User.email: "Email",
        User.first_name: "Имя",
        User.second_name: "Отчество",
        User.last_name: "Фамилия",
        User.phone: "Телефон",
        User.birth_date: "Дата рождения",
        User.is_system: "Системный пользователь",
        User.is_active: "Активен",
    }

    async def on_model_change(self, data, model, is_created, request):
        # Берём пароль из формы
        password = getattr(data, "password", None)

        # При создании пароль обязателен
        if is_created and not password:
            raise ValueError("Пароль обязателен при создании пользователя")

        # Хэшируем пароль
        if password:
            model.password_hash = hash_password(password)

        return model