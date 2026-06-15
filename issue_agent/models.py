from pydantic import BaseModel, Field


class IssueComment(BaseModel):
    author: str
    body: str
    created_at: str


class IssueInput(BaseModel):
    number: int
    title: str
    body: str
    labels: list[str] = Field(default_factory=list)
    author: str
    url: str
    created_at: str
    updated_at: str
    comments: list[IssueComment] = Field(default_factory=list)


class LabelInfo(BaseModel):
    name: str
    description: str | None = None
