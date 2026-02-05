from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class CustomerBase(BaseModel):
    first_name: Optional[str] = Field(..., min_length=1, description="Name Cannot be empty")
    last_name: Optional[str] = Field(..., min_length=1, description="Name Cannot be empty")
    company: Optional[str] = Field(..., description="The company from which the customer is")
    email: Optional[EmailStr] = Field(..., description="The email address of the customer")
    phone: Optional[str] = Field(None,description="Mobile number of the customer")
