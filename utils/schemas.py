from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class CustomerBase(BaseModel):
    first_name: Optional[str] = Field(..., min_length=1, description="Name Cannot be empty")
    last_name: Optional[str] = Field(..., min_length=1, description="Name Cannot be empty")
    company: Optional[str] = Field(..., description="The company from which the customer is")
    email: Optional[EmailStr] = Field(..., description="The email address of the customer")
    phone: Optional[str] = Field(None, description="Mobile number of the customer")


class TicketType(str, Enum):
    BUG = "Bug"
    FEATURE = "Feature Request"
    INQUIRY = "Inquiry"
    BILLING = "Billing"
    ACCESS = "Access"


class TicketStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    CLOSED = "Closed"


class TicketPriority(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class TicketBase(BaseModel):
    title: str = Field(...,description="The title or subject of the ticket")
    description: Optional[str] = Field(None,description="THe detailed description of the ticket if needed")
    customer_id: int = Field(...,description="The customer who has requested to make this ticket.")
    assignee_id: Optional[int] = Field(None,description="The employee or agent this ticket is assigned to.")
    ticket_type: Optional[TicketType] = Field(None,description="The type of ticket for available ones")
    priority: Optional[TicketPriority] = Field(None,description="The priority of the ticket based on urgency.")
    status: Optional[TicketStatus] = Field(None,description="The current status of the ticket.")


class AccessLevel(str, Enum):
    ADMIN = "admin"
    AGENT = "agent"


class EmployeeBase(BaseModel):
    first_name: str = Field(..., min_length=1, description="First name of the employee")
    last_name: str = Field(..., min_length=1, description="Last name of the employee")
    email: EmailStr = Field(..., description="Official work email address")
    phone: Optional[str] = Field(..., description="Contact phone number")
    access_level: Optional[AccessLevel] = Field(None, description="Role or access level (e.g., AGENT, ADMIN)")
    password_hash: str = Field(..., min_length=8, description="Initial password for the account (hashed or raw)")


