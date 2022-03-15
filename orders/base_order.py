from pydantic import BaseModel, validator


class BaseOrder(BaseModel):
    id: str
    name: str

    @validator("id")
    def must_be_4_characters(cls, id_to_match):
        if len(id_to_match) != 4:
            raise ValueError("Id has to be 4 characters len!")
        return id_to_match


def side_validator(validated_side):
    if validated_side not in ["S", "B"]:
        raise ValueError("Wrong side value!")
    return validated_side
