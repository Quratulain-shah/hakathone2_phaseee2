"""
Authentication routes for the Todo App backend API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

try:
    from dependencies import get_db_session
    from models.user import User, UserCreate, UserLogin, Token, UserRead
    from utils import verify_password, get_password_hash, create_access_token
    from config import settings
except ImportError:
    from backend.dependencies import get_db_session
    from backend.models.user import User, UserCreate, UserLogin, Token, UserRead
    from backend.utils import verify_password, get_password_hash, create_access_token
    from backend.config import settings


# Create API router for auth endpoints
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/register", response_model=UserRead)
async def register_user(
    user_create: UserCreate,
    db_session: AsyncSession = Depends(get_db_session)
) -> UserRead:
    """
    Register a new user with email and password.

    Args:
        user_create: User registration data (email and password)
        db_session: Database session for async operations

    Returns:
        UserRead: Created user data (without password)

    Raises:
        HTTPException: If email already exists or registration fails
    """
    try:
        # Check if user with email already exists
        existing_user_result = await db_session.execute(
            select(User).where(User.email == user_create.email)
        )
        existing_user = existing_user_result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )

        # Hash the password, handling potential bcrypt issues
        try:
            hashed_password = get_password_hash(user_create.password)
        except Exception as e:
            print(f"Password hashing error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password format"
            )

        # Create new user
        db_user = User(
            email=user_create.email,
            hashed_password=hashed_password
        )

        # Add user to database
        db_session.add(db_user)
        await db_session.commit()
        await db_session.refresh(db_user)

        # Return user data (excluding password)
        return UserRead(
            id=db_user.id,
            email=db_user.email,
            created_at=db_user.created_at,
            is_active=db_user.is_active
        )

    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        # Log the error (in a real application, use proper logging)
        print(f"Unexpected error during user registration: {str(e)}")
        import traceback
        traceback.print_exc()

        # Raise HTTP exception with structured response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration"
        )


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_session: AsyncSession = Depends(get_db_session)
) -> Token:
    """
    Authenticate user and return JWT token.

    Args:
        form_data: OAuth2 form data containing username (email) and password
        db_session: Database session for async operations

    Returns:
        Token: JWT access token and token type

    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        # Find user by email
        result = await db_session.execute(
            select(User).where(User.email == form_data.username)
        )
        user = result.scalar_one_or_none()

        # Check if user exists first
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password, handling potential bcrypt issues
        try:
            password_valid = verify_password(form_data.password, user.hashed_password)
        except Exception as e:
            print(f"Password verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication error",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not password_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})

        # Return token
        return Token(access_token=access_token, token_type="bearer")

    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        # Log the error (in a real application, use proper logging)
        print(f"Unexpected error during user login: {str(e)}")

        # Raise HTTP exception with structured response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login"
        )


@router.get("/me", response_model=UserRead)
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db_session: AsyncSession = Depends(get_db_session)
) -> UserRead:
    """
    Get current authenticated user based on JWT token.

    Args:
        token: JWT token from Authorization header
        db_session: Database session for async operations

    Returns:
        UserRead: Current user data (without password)

    Raises:
        HTTPException: If token is invalid or user doesn't exist
    """
    try:
        from backend.utils import verify_token

        # Verify token and get user ID
        user_id = verify_token(token)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user from database
        result = await db_session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Return user data (excluding password)
        return UserRead(
            id=user.id,
            email=user.email,
            created_at=user.created_at,
            is_active=user.is_active
        )

    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        # Log the error (in a real application, use proper logging)
        print(f"Unexpected error getting current user: {str(e)}")

        # Raise HTTP exception with structured response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving user data"
        )