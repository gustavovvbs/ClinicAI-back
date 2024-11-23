from pydantic import BaseModel, Field 

class ContactModel(BaseModel):
    email: str = Field(None, description="Email of the contact")
    name: str = Field(None, description="Name of the contact")
    phone: str = Field(None, description="Phone of the contact")
    role: str = Field(None, description="Role of the contact")