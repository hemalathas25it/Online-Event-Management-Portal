from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


# --- Auth Models ---

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    password: str = Field(..., min_length=6, max_length=100, description="Password (at least 6 characters)")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Username cannot be empty")
        if not all(c.isalnum() or c in ("_", "-", ".") for c in v):
            raise ValueError("Username may only contain letters, numbers, and .-_")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    created_at: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# --- Event Models ---

class EventCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = ""
    date: str = Field(..., description="Event date in YYYY-MM-DD format")
    location: Optional[str] = ""

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        v = v.strip()
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in valid YYYY-MM-DD format")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Event title cannot be empty")
        return v


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    location: Optional[str] = None

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Date must be in valid YYYY-MM-DD format")
        return v


class EventOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = ""
    date: str
    location: Optional[str] = ""
    created_at: str
    is_upcoming: bool
    participant_count: int = 0


# --- Registration Models ---

class RegistrationCreate(BaseModel):
    event_id: int = Field(..., gt=0)
    participant_name: str = Field(..., min_length=2, max_length=100)

    @field_validator("participant_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Participant name cannot be empty")
        return v


class RegistrationOut(BaseModel):
    id: int
    event_id: int
    user_id: Optional[int] = None
    participant_name: str
    registered_at: str
    event_title: str
    event_date: str
    event_location: Optional[str] = None
    registered_by_user: Optional[str] = None


# --- Dashboard & Report Models ---

class DashboardStats(BaseModel):
    upcoming_events: int
    past_events: int
    total_registrations: int
    total_users: int


class EventReportItem(BaseModel):
    id: int
    title: str
    date: str
    status: str
    participant_count: int


class RecentRegistrationItem(BaseModel):
    id: int
    participant_name: str
    registered_at: str
    event_title: str


class DashboardReports(BaseModel):
    event_distribution: List[EventReportItem]
    recent_registrations: List[RecentRegistrationItem]
