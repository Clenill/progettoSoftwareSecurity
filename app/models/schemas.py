from pydantic import BaseModel, EmailStr, Field

# dati in ingresso (request)
class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=25)
    email: EmailStr
    password: str = Field(min_length=3, max_length=72)

# dati in uscita (response)
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True  # necessario per SQLAlchemy