from fastapi import FastAPI

from data_models.model import Creature
from data_models.data import get_creatures


app = FastAPI()


@app.get("/hi")
def say_hi():
    return "hi"


@app.get("/creature")
def get_all() -> list[Creature]:
    return get_creatures()
