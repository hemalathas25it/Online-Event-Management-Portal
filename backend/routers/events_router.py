from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from backend.models import EventCreate, EventUpdate, EventOut
from backend.database import (
    get_all_events,
    get_event_by_id,
    create_event,
    update_event,
    delete_event,
)
from backend.auth import require_admin

router = APIRouter(prefix="/api/events", tags=["Events"])


@router.get("", response_model=List[EventOut])
def list_events(
    filter: Optional[str] = Query(
        None,
        description="Filter events: 'upcoming' or 'past'",
        pattern="^(upcoming|past)$",
    ),
    search: Optional[str] = Query(None, description="Search query string"),
):
    """Retrieve all events, optionally filtered by status (upcoming/past) and search text."""
    return get_all_events(filter_type=filter, search=search)


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int):
    """Retrieve a single event by ID."""
    event = get_event_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found",
        )
    return event


@router.post("", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def add_event(data: EventCreate, admin_user: dict = Depends(require_admin)):
    """Create a new event (Administrators only)."""
    event = create_event(
        title=data.title,
        description=data.description or "",
        date_str=data.date,
        location=data.location or "",
    )
    return event


@router.put("/{event_id}", response_model=EventOut)
def edit_event(
    event_id: int,
    data: EventUpdate,
    admin_user: dict = Depends(require_admin),
):
    """Update an existing event (Administrators only)."""
    existing = get_event_by_id(event_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found",
        )

    title = data.title if data.title is not None else existing["title"]
    description = (
        data.description if data.description is not None else existing["description"]
    )
    date_str = data.date if data.date is not None else existing["date"]
    location = data.location if data.location is not None else existing["location"]

    updated = update_event(
        event_id=event_id,
        title=title,
        description=description,
        date_str=date_str,
        location=location,
    )
    return updated


@router.delete("/{event_id}")
def remove_event(event_id: int, admin_user: dict = Depends(require_admin)):
    """Delete an event and its associated participant registrations (Administrators only)."""
    existing = get_event_by_id(event_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found",
        )

    delete_event(event_id)
    return {"message": "Event deleted successfully", "id": event_id}
