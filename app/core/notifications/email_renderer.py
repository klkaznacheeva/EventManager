from pathlib import Path

from jinja2 import (
    Environment,
    FileSystemLoader,
    select_autoescape
)


BASE_DIR = Path(__file__).resolve().parent


env = Environment(
    loader=FileSystemLoader("/app/app/admin/templates"),
    autoescape=True
)



def render_email_template(
    template_name: str,
    context: dict
) -> str:

    template = env.get_template(template_name)

    return template.render(**context)