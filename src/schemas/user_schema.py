from pydantic import BaseModel, ConfigDict


class UserCreateRequest(BaseModel):
    name: str
    email: str
    password: str

    model_config = ConfigDict(from_attributes=True)


class UserLoginRequest(BaseModel):
    email: str
    password: str

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)
