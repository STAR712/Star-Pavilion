from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_base_url: str = "https://maas-api.cn-huabei-1.xf-yun.com/v2"
    model_name: str = "xop35qwen2b"
    embed_model: str = "sde0a5839"
    api_key: str = "test_api_key_123456"
    auth_secret: str = "star-pavilion-auth-secret"
    database_url: str = "sqlite:///./novel.db"
    chroma_dir: str = "./chroma_db"
    default_user_id: int = 1
    default_user_role: str = "reader"

    class Config:
        env_file = ".env"


settings = Settings()
