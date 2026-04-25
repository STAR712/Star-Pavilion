from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ===== 讯飞星辰 API =====
    xfyun_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("XFYUN_API_KEY", "OPENAI_API_KEY"),
    )
    xfyun_base_url: str = Field(
        default="https://maas-api.cn-huabei-1.xf-yun.com/v2",
        validation_alias=AliasChoices("XFYUN_BASE_URL", "OPENAI_BASE_URL"),
    )
    xfyun_chat_model: str = Field(
        default="xop35qwen2b",
        validation_alias=AliasChoices("XFYUN_CHAT_MODEL", "MODEL_NAME"),
    )
    xfyun_embedding_model: str = Field(
        default="xop3qwen8bembedding",
        validation_alias=AliasChoices("XFYUN_EMBEDDING_MODEL", "EMBED_MODEL"),
    )

    # ===== 安全配置（生产环境必须修改 AUTH_SECRET） =====
    auth_secret: str = Field(
        default="star-pavilion-dev-secret-change-in-production",
        validation_alias=AliasChoices("AUTH_SECRET"),
        description="JWT 签名密钥，生产环境请设置为至少32位随机字符串",
    )
    access_token_ttl: int = Field(
        default=900,
        validation_alias=AliasChoices("ACCESS_TOKEN_TTL"),
        description="access_token 有效期（秒），默认15分钟",
    )
    refresh_token_ttl: int = Field(
        default=604800,
        validation_alias=AliasChoices("REFRESH_TOKEN_TTL"),
        description="refresh_token 有效期（秒），默认7天",
    )
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        validation_alias=AliasChoices("CORS_ORIGINS"),
        description="允许的跨域来源，多个用逗号分隔",
    )

    # ===== 数据库 =====
    database_url: str = "sqlite:///./novel.db"
    chroma_dir: str = "./chroma_db"
    default_user_id: int = 1
    default_user_role: str = "reader"

    class Config:
        env_file = ".env"


settings = Settings()
