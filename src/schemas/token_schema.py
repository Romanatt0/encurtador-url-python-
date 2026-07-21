from pydantic import BaseModel, ConfigDict


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

    model_config = ConfigDict(from_attributes=True)


class RefreshTokenResponse(BaseModel):
    refresh_token: str
    token_type: str

    model_config = ConfigDict(from_attributes=True)

class RefreshTokenRequest(BaseModel):
    access_token: str

    model_config = ConfigDict(from_attributes=True)