from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class DebugSettings(BaseSettings):
    DATABASE_URL: str
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

print("CWD:", os.getcwd())
print(".env exists:", os.path.exists(".env"))
try:
    s = DebugSettings()
    print("DATABASE_URL:", s.DATABASE_URL)
except Exception as e:
    print("Error:", e)
