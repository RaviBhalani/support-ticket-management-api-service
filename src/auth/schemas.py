from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.users.constants import EMAIL_MAX_LENGTH, PASSWORD_MAX_LENGTH, UserRole


class LoginRequest(BaseModel):
    email: EmailStr = Field(max_length=EMAIL_MAX_LENGTH)
    password: str = Field(max_length=PASSWORD_MAX_LENGTH)


class LoginResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str
    last_name: str
    role: UserRole
