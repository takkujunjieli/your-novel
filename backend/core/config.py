from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Your Novel API"

    # By default, use a local SQLite file named sql_app.db
    DATABASE_URL: str = "sqlite:///./sql_app.db"

    # LLM Configuration — change these 3 values to switch providers
    # Works with OpenAI, Ollama, vLLM, or any OpenAI-compatible server
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_MAX_TOKENS: int = 2000
    LLM_TEMPERATURE: float = 0.8
    LLM_TIMEOUT: int = 120

    # This tells Pydantic to read from a .env file if it exists
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Create a global settings object to import elsewhere
settings = Settings()
