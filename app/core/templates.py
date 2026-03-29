# app/core/templates.py
from jinja2 import Environment, FileSystemLoader
from fastapi.responses import HTMLResponse

# Создаем окружение
env = Environment(
    loader=FileSystemLoader("/app/app/admin/templates"),
    autoescape=True
)

def render_template(template_name: str, context: dict) -> HTMLResponse:
    """Рендерит шаблон и возвращает HTMLResponse"""
    template = env.get_template(template_name)
    content = template.render(**context)
    return HTMLResponse(content=content)