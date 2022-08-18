from pydantic import BaseModel, EmailStr, Field, validator, UUID4
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """ Проверяет sign-up запрос """
    email: EmailStr
    name: str
    password: str


class UserBase(BaseModel):
    """ Формирует тело ответа с деталями пользователя """
    id: int
    email: EmailStr
    name: str


class TokenBase(BaseModel):
    token: UUID4 = Field(..., alias="access_token")
    expires: datetime
    token_type: Optional[str] = "bearer"

    class Config:
        allow_population_by_field_name = True


    @validator("token")
    def hexlify_token(cls, value):
        """ Конвертирует UUID в hex строку """
        return value.hex


class User(UserBase):
    """ Return detailed response data with token """
    token: TokenBase = {}