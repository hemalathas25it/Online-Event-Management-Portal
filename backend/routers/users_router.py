from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from backend.models import UserOut
from backend.database import get_all_users
from backend.auth import require_admin

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("", response_model=List[UserOut])
def list_users(
    search: Optional[str] = Query(None, description="Filter users by username"),
    admin_user: dict = Depends(require_admin),
):
    """List all registered users (Administrators only)."""
    return get_all_users(search=search)
