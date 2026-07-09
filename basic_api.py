from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Literal

router = APIRouter()


class Person(BaseModel):
    name: str
    soeid: str


class PbqAnswer(BaseModel):
    pbq_id: str          # the pbq# selected
    answer: Literal["Yes", "No"]


class CreatePptRequest(BaseModel):
    pts_id: str
    architecture: List[Person]
    presenter: List[Person]
    pbq_answers: List[PbqAnswer]


@router.post("/generate_pb_ppt")
def generate_pb_ppt(request: CreatePptRequest):
    return request
