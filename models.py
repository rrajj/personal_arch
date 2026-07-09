from pydantic import BaseModel
from typing import List, Literal


class Person(BaseModel):
    name: str
    soeid: str


class PbqAnswer(BaseModel):
    pbq_id: str
    answer: Literal["Yes", "No"]


class CreatePptRequest(BaseModel):
    pts_id: str
    architecture: List[Person]
    presenter: List[Person]
    pbq_answers: List[PbqAnswer]


class CreatePptResponse(BaseModel):
    id: int
    pts_id: str
    permit_type: str
    version: int
    status: str
    file_name: str
    created_at: str
