from typing import List

from pydantic import BaseModel, Field


class Character(BaseModel):
    name: str = Field(..., description="name of character.")
    backstory: str = Field(..., description="backstory of character.")
    personality: str = Field(..., description="personality of character.")


class Characters(BaseModel):
    characters: List[Character] = Field(
        ...,
        description="list of characters, including names, backstories, and personalities.",
    )


class OutLine(BaseModel):
    outline: List[str] = Field(
        ..., description="list of outline, around 12 plot beats."
    )

class Scene(BaseModel):
    scenes: List[str] = Field(..., description="list of short description for each scene.")