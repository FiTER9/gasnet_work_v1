from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "天然气管网智能安全监测与仿真平台 V1.0"
    database_url: str = "sqlite:///./gasnet.db"
    secret_key: str = "dev-only-change-me"
    simulator_mode: str = "builtin"
    simulink_model: str = "gas_network"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

