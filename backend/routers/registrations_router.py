from datetime import date
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from backend.models import RegistrationCreate, RegistrationOut
from backend.database import (
    get_all_registrations,
    get_registration_by_id,
    check_registration_exists,
    create_registration,
    delete_registration,
    get_event_by_id,
)
from backend.auth import get_current_user, get_optional_user

router = APIRouter(prefix="/api/registrations", tags=["Registrations"])


@router.get("", response_model=List[RegistrationOut])
def list_registrations(
    search: Optional[str] = Query(None, description="Search query string"),
    current_user: dict = Depends(get_current_user),
):
    """
    List participant registrations.
    Administrators see all registrations. Regular users see their own registrations.
    """
    if current_user.get("role") == "admin":
        return get_all_registrations(search=search)
    else:
        return get_all_registrations(search=search, user_id=current_user["id"])


@router.post("", response_model=RegistrationOut, status_code=status.HTTP_201_CREATED)
def register_for_event(
    data: RegistrationCreate,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    Register a participant for an upcoming event.
    Validates that the event exists, is upcoming, and avoids duplicate registrations.
    """
    event = get_event_by_id(data.event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {data.event_id} does not exist",
        )

    # Check if event is past
    today_str = date.today().isoformat()
    if event["date"] < today_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration closed: Cannot register for past events",
        )

    # Check for duplicate registration for this participant in the event
    participant_name = data.participant_name.strip()
    if check_registration_exists(data.event_id, participant_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{participant_name}' is already registered for this event",
        )

    user_id = current_user["id"] if current_user else None
    registration = create_registration(
        event_id=data.event_id,
        participant_name=participant_name,
        user_id=user_id,
    )
    return registration


@router.delete("/{reg_id}")
def remove_registration(
    reg_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    Remove/cancel a participant registration.
    Allowed for administrators or the user who created the registration.
    """
    registration = get_registration_by_id(reg_id)
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registration with ID {reg_id} not found",
        )

    # Authorization check
    if current_user.get("role") != "admin" and registration.get("user_id") != current_user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this registration",
        )

    delete_registration(reg_id)
    return {"message": "Participant registration removed successfully", "id": reg_id}
