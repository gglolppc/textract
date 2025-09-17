from pydantic import BaseModel, EmailStr
import re

class UserCreate(BaseModel):
    email: str = EmailStr