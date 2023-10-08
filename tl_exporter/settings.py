from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    tl_base_url: str = Field(..., title="Switch URL")
    tl_username: str = Field(..., title="Switch username")
    tl_password: str = Field(..., title="Switch password")
    log_format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        title="Log format",
    )
    log_level: str = Field("info", title="Log level")
    host: str = Field("", title="Address on which to listen")
    port: int = Field(8000, title="Port on which to listen")
