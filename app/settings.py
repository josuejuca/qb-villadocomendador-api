from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str

    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASS: str
    SMTP_FROM_NAME: str = "imoGo"
    SMTP_FROM_EMAIL: EmailStr

    INTERNAL_NOTIFY_EMAIL: EmailStr | None = None
    API_KEY: str | None = None

    # Google Forms 
    GOOGLE_FORMS_FORM_RESPONSE_URL: str | None = (
        "https://docs.google.com/forms/d/e/1FAIpQLSeCJd8h4HxmCtmhxV3HKhAu3XQSsWfxXFhacOT2nH_j9rdWbQ/formResponse"
    )

settings = Settings()
