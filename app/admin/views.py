from sqladmin import ModelView
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_session
from sqlalchemy.orm import selectinload
from wtforms import Form, PasswordField, StringField, BooleanField, DateField

from app.models import Event, Session, Category
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

# ===== Пользователи =====
class UserAdmin(ModelView, model=User):
    name = "Пользователь"
    name_plural = "Пользователи"

    icon = "fa-solid fa-user"

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

# ===== Мероприятие =====
class EventAdmin(ModelView, model=Event):
    name = "Мероприятие"
    name_plural = "Мероприятия"

    icon = "fa-solid fa-calendar"

    details_template = "event_details.html"
    details_template_mode = "custom"

    form_excluded_columns = ["sessions", "created_at", "updated_at"]

    column_list = [
        Event.title,
        Event.category,
        Event.start_date,
        Event.end_date,
        Event.location,
        Event.status
    ]

    column_labels = {
        Event.title: "Название",
        Event.category: "Категория",
        Event.start_date: "Начало",
        Event.end_date: "Конец",
        Event.location: "Локация",
        Event.status: "Статус"
    }

    column_searchable_list = [
        Event.title,
        Event.location
    ]

    column_sortable_list = [
        Event.start_date,
        Event.end_date
    ]

    form_ajax_refs = {
        "category": {
            "fields": ["name"],  # показываем имя категории
        }
    }

    async def get_details_context(self, request, obj):
        """Возвращаем объект и его сессии для шаблона"""
        sessions = getattr(obj, "sessions", [])
        return {
            "view": self,
            "obj": obj,
            "sessions": sessions or []
        }

# ===== События =====
class SessionAdmin(ModelView, model=Session):
    name = "Событие"
    name_plural = "События"

    icon = "fa-solid fa-clock"

    column_list = [
        Session.title,
        Session.event,
        Session.start_date,
        Session.end_date
    ]

    column_labels = {
        Session.title: "Название",
        Session.event: "Мероприятие",
        Session.start_date: "Начало",
        Session.end_date: "Конец"
    }

    column_searchable_list = [
        Session.title
    ]

    column_filters = [
        Session.event
    ]

# ===== Категории =====
class CategoryAdmin(ModelView, model=Category):
    name = "Категория"
    name_plural = "Категории"

    icon = "fa-solid fa-tags"

    form_excluded_columns = ["events"]

    column_list = [
        Category.name
    ]

    column_labels = {
        Category.name: "Название категории"
    }

    column_searchable_list = [
        Category.name
    ]