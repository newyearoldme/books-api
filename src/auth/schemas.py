from pydantic import BaseModel


class LoginRequestSchema(BaseModel):
    username: str
    password: str
