import pydantic


class UserRequest(pydantic.BaseModel):
    username: str
    email: str
    password: str

    class Config:
        orm_mode = True

class UserResponse(pydantic.BaseModel):
    username: str
    email: str

    class Config:
        orm_mode = True