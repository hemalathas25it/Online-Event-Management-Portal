from fastapi import APIRouter, HTTPException, status, Depends
from backend.models import UserRegister, UserLogin, UserOut, Token
from backend.database import get_user_by_username, create_user
from backend.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister):
    """Register a new user and return an authentication token."""
    existing = get_user_by_username(data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username already exists",
        )

    hashed = hash_password(data.password)
    user = create_user(username=data.username, password_hash=hashed, role="user")

    user_out = UserOut(
        id=user["id"],
        username=user["username"],
        role=user["role"],
        created_at=user["created_at"],
    )

    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"], "id": user["id"]}
    )

    return Token(access_token=access_token, token_type="bearer", user=user_out)


@router.post("/login", response_model=Token)
def login(data: UserLogin):
    """Authenticate a user with username and password, returning a JWT token."""
    user = get_user_by_username(data.username)
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_out = UserOut(
        id=user["id"],
        username=user["username"],
        role=user["role"],
        created_at=user["created_at"],
    )

    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"], "id": user["id"]}
    )

    return Token(access_token=access_token, token_type="bearer", user=user_out)


@router.get("/me", response_model=UserOut)
def get_profile(current_user: dict = Depends(get_current_user)):
    """Retrieve current authenticated user information."""
    return UserOut(
        id=current_user["id"],
        username=current_user["username"],
        role=current_user["role"],
        created_at=current_user["created_at"],
    )
