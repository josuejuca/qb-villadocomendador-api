from pathlib import Path
from email.message import EmailMessage
import aiosmtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .settings import settings

TEMPLATES_DIR = Path(__file__).parent / "templates"
env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)

def render_template(template_name: str, context: dict) -> str:
    template = env.get_template(template_name)
    return template.render(**context)

async def send_email_html(to_email: str, subject: str, html: str):
    msg = EmailMessage()
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content("Seu cliente de e-mail não suporta HTML.")
    msg.add_alternative(html, subtype="html")

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASS,
        start_tls=True,
        timeout=20,
    )
