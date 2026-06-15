from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, field_validator


class ProviderConfig(BaseModel):
    name: str = "fixture"
    base_url: str | None = None
    api_key_env: str = "MINIMAX_API_KEY"


class RepoConfig(BaseModel):
    full_name: str
    owner: str
    name: str

    @classmethod
    def from_full_name(cls, value: str) -> "RepoConfig":
        owner, name = value.split("/", 1)
        return cls(full_name=value, owner=owner, name=name)


class LabelPolicy(BaseModel):
    allowed_labels: list[str] = Field(default_factory=list)


class AppConfig(BaseModel):
    repo: str
    state_root: Path
    batch_size: int = Field(default=20, ge=1, le=100)
    write_policy: Literal["preview"] = "preview"
    provider: ProviderConfig = Field(default_factory=ProviderConfig)
    label_policy: LabelPolicy = Field(default_factory=LabelPolicy)

    @field_validator("repo")
    @classmethod
    def repo_must_be_owner_name(cls, value: str) -> str:
        if "/" not in value or value.startswith("/") or value.endswith("/"):
            raise ValueError("repo must use owner/name format")
        return value

    @property
    def repo_config(self) -> RepoConfig:
        return RepoConfig.from_full_name(self.repo)


def load_config(path: Path) -> AppConfig:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return AppConfig.model_validate(raw)
