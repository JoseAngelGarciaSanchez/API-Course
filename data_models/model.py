from pydantic import BaseModel, Field


class Creature(BaseModel):
    name: str
    country: str
    area: str
    description: str
    aka: str

class CreatureWithLongName(BaseModel):
    name: str = Field(min_length=2)
    country: str
    area: str
    description: str
    aka: str

class CreatureWithLongRequiredName(BaseModel):
    name: str = Field(..., min_length=2)
    country: str
    area: str
    description: str
    aka: str

thing = Creature(
    name="yeti",
    country="CN",
    area="Himalayas",
    description="Hirsute Himalayan",
    aka="Abominable Snowman",
)

print("Name is", thing.name)
