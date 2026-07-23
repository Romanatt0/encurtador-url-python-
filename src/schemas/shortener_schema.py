from pydantic import BaseModel, ConfigDict


class shortenerRequest(BaseModel):
    url: str

    model_config = ConfigDict(from_attributes=True)


class shortenerResponse(BaseModel):
    url: str
    short_url: str
    expiration_date: str | None = None

    model_config = ConfigDict(from_attributes=True)

class allLinksResponse(BaseModel):
    links: list[shortenerResponse]

    model_config = ConfigDict(from_attributes=True)
