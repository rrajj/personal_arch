from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Literal

app = FastAPI()


class Person(BaseModel):
    name: str
    soeid: str


class PbqAnswer(BaseModel):
    pbq_id: str          # the pbq# selected
    answer: Literal["Yes", "No"]


class CreatePptRequest(BaseModel):
    pts_id: str
    permit_type: Literal["Build", "Deploy"]
    architecture: List[Person]
    presenter: List[Person]
    pbq_answers: List[PbqAnswer]


@app.post("/create_ppt_template")
def create_ppt_template(request: CreatePptRequest):
    return request
