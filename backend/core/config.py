from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Your Novel API"
    
    # By default, use a local SQLite file named sql_app.db
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    
    # This tells Pydantic to read from a .env file if it exists
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Create a global settings object to import elsewhere
settings = Settings()
