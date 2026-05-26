from pydantic import BaseModel, ConfigDict


class shortenerRequest(BaseModel):
    url: str

    model_config = ConfigDict(from_attributes=True)


class shortenerResponse(BaseModel):
    url: str
    short_url: str

    model_config = ConfigDict(from_attributes=True)
