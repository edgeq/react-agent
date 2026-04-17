from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    model: str = "gpt-5.4-mini"

    model_config = {"env_file": ".env"}

settings = Settings()  # type: ignore[call-arg]