from pydantic_settings import BaseSettings, SettingsConfigDict


class NombaConfig(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")
    nomba_client_id: str
    nomba_client_secret: str
    nomba_account_id: str
    nomba_base_url: str = "https://api.nomba.com"
