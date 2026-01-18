from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import logging

from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.oauth2.credentials import Credentials
from google.auth.transport import requests as google_requests

from app.db.base import get_db
from app.db.models import User
from app.models.schemas import Token, UserCreate, UserResponse, GoogleLoginResponse
from app.utils.auth import verify_password, get_password_hash, create_access_token, get_current_active_user
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_google_client_config() -> dict:
    """Google OAuth 클라이언트 설정을 반환합니다."""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth 설정이 완료되지 않았습니다. GOOGLE_CLIENT_ID와 GOOGLE_CLIENT_SECRET을 확인하세요."
        )
    
    return {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
        }
    }


def _create_google_flow() -> Flow:
    """Google OAuth Flow 객체를 생성합니다."""
    client_config = _get_google_client_config()
    
    flow = Flow.from_client_config(
        client_config,
        scopes=settings.GOOGLE_OAUTH_SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )
    
    return flow


def _get_or_create_user_from_google(
    db: Session,
    google_id: str,
    email: str,
    full_name: str,
    refresh_token: Optional[str],
    access_token: Optional[str],
    token_expiry: Optional[datetime]
) -> User:
    """Google 정보를 사용하여 사용자를 조회하거나 생성합니다."""
    user = db.query(User).filter(User.google_id == google_id).first()
    
    if user:
        user.google_refresh_token = refresh_token or user.google_refresh_token
        user.google_access_token = access_token
        user.google_token_expiry = token_expiry
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        logger.info(f"기존 Google 사용자 업데이트: {email}")
        return user
    
    existing_email_user = db.query(User).filter(User.email == email).first()
    if existing_email_user:
        if existing_email_user.google_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이 이메일은 다른 Google 계정으로 이미 연결되어 있습니다."
            )
        
        existing_email_user.google_id = google_id
        existing_email_user.google_refresh_token = refresh_token
        existing_email_user.google_access_token = access_token
        existing_email_user.google_token_expiry = token_expiry
        existing_email_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_email_user)
        logger.info(f"기존 사용자에 Google 계정 연결: {email}")
        return existing_email_user
    
    username = email.split("@")[0]
    base_username = username
    counter = 1
    while db.query(User).filter(User.username == username).first():
        username = f"{base_username}_{counter}"
        counter += 1
    
    new_user = User(
        username=username,
        email=email,
        full_name=full_name or email.split("@")[0],
        role="user",
        password_hash=None,
        google_id=google_id,
        google_refresh_token=refresh_token,
        google_access_token=access_token,
        google_token_expiry=token_expiry,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"새 Google 사용자 생성: {email}")
    return new_user


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """일반 회원가입 (이메일/비밀번호 방식)"""
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="이미 등록된 사용자명입니다.")
    
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """일반 로그인 (사용자명/비밀번호 방식)"""
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 사용자명 또는 비밀번호입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이 계정은 Google 로그인만 지원합니다. Google 로그인을 사용하세요.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 사용자명 또는 비밀번호입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="비활성화된 사용자입니다.")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/google/login", response_model=GoogleLoginResponse)
async def google_login(
    redirect_uri: Optional[str] = Query(
        None,
        description="인증 후 리다이렉트할 프론트엔드 URL (기본값: settings.FRONTEND_URL)"
    )
):
    """
    Google OAuth 로그인 URL을 생성합니다.
    
    프론트엔드에서 이 URL로 사용자를 리다이렉트하여 Google 로그인을 시작합니다.
    """
    try:
        flow = _create_google_flow()
        
        state = redirect_uri or settings.FRONTEND_URL
        
        authorization_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
            state=state
        )
        
        logger.info("Google OAuth 인증 URL 생성 완료")
        return GoogleLoginResponse(
            login_url=authorization_url,
            message="Google 로그인 URL이 생성되었습니다. 이 URL로 리다이렉트하세요."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth URL 생성 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google OAuth URL 생성에 실패했습니다: {str(e)}"
        )


@router.get("/google/callback")
async def google_callback(
    code: str = Query(..., description="Google에서 발급한 인증 코드"),
    state: Optional[str] = Query(None, description="프론트엔드 리다이렉트 URL"),
    error: Optional[str] = Query(None, description="OAuth 에러 코드"),
    error_description: Optional[str] = Query(None, description="OAuth 에러 설명"),
    db: Session = Depends(get_db)
):
    """
    Google OAuth 콜백을 처리합니다.
    
    1. 인증 코드를 토큰으로 교환
    2. ID 토큰 검증 및 사용자 정보 추출
    3. 사용자 생성/업데이트
    4. JWT 액세스 토큰 발급
    5. 프론트엔드로 리다이렉트
    """
    if error:
        logger.error(f"Google OAuth 에러: {error} - {error_description}")
        frontend_url = state or settings.FRONTEND_URL
        return RedirectResponse(
            url=f"{frontend_url}/login?error={error}&error_description={error_description or ''}"
        )
    
    try:
        flow = _create_google_flow()
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        if not credentials.id_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google에서 ID 토큰을 받지 못했습니다."
            )
        
        request = google_requests.Request()
        
        try:
            id_info = id_token.verify_oauth2_token(
                credentials.id_token,
                request,
                settings.GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=10
            )
        except ValueError as e:
            logger.error(f"ID 토큰 검증 실패: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Google ID 토큰 검증에 실패했습니다: {str(e)}"
            )
        
        if id_info.get("iss") not in ["accounts.google.com", "https://accounts.google.com"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="잘못된 토큰 발급자입니다."
            )
        
        google_id = id_info.get("sub")
        email = id_info.get("email")
        full_name = id_info.get("name", "")
        
        if not google_id or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google 계정에서 필수 정보(ID, 이메일)를 가져올 수 없습니다."
            )
        
        if not id_info.get("email_verified", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이메일이 인증되지 않은 Google 계정입니다."
            )
        
        token_expiry = None
        if credentials.expiry:
            token_expiry = credentials.expiry
        
        user = _get_or_create_user_from_google(
            db=db,
            google_id=google_id,
            email=email,
            full_name=full_name,
            refresh_token=credentials.refresh_token,
            access_token=credentials.token,
            token_expiry=token_expiry
        )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "google_id": google_id},
            expires_delta=access_token_expires
        )
        
        frontend_url = state or settings.FRONTEND_URL
        redirect_url = f"{frontend_url}/auth/callback?access_token={access_token}&token_type=bearer"
        
        logger.info(f"Google OAuth 로그인 성공: {email}")
        return RedirectResponse(url=redirect_url)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth 콜백 처리 실패: {str(e)}")
        frontend_url = state or settings.FRONTEND_URL
        return RedirectResponse(
            url=f"{frontend_url}/login?error=callback_failed&error_description={str(e)}"
        )


@router.post("/google/refresh", response_model=Token)
async def refresh_google_token(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Google OAuth 토큰을 갱신합니다.
    
    사용자의 저장된 refresh_token을 사용하여 새 access_token을 발급받습니다.
    """
    if not current_user.google_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google refresh token이 없습니다. 다시 로그인하세요."
        )
    
    try:
        credentials = Credentials(
            token=current_user.google_access_token,
            refresh_token=current_user.google_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=settings.GOOGLE_OAUTH_SCOPES
        )
        
        request = google_requests.Request()
        credentials.refresh(request)
        
        current_user.google_access_token = credentials.token
        current_user.google_token_expiry = credentials.expiry
        if credentials.refresh_token:
            current_user.google_refresh_token = credentials.refresh_token
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": current_user.username, "google_id": current_user.google_id},
            expires_delta=access_token_expires
        )
        
        logger.info(f"Google 토큰 갱신 성공: {current_user.email}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except Exception as e:
        logger.error(f"Google 토큰 갱신 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Google 토큰 갱신에 실패했습니다. 다시 로그인하세요: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """현재 로그인한 사용자 정보를 반환합니다."""
    return current_user


def get_user_google_credentials(user: User) -> Optional[Credentials]:
    """
    사용자의 Google Credentials 객체를 반환합니다.
    
    Google Drive API 등을 사용할 때 이 함수를 호출하여 credentials를 얻습니다.
    """
    if not user.google_refresh_token:
        return None
    
    credentials = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=settings.GOOGLE_OAUTH_SCOPES
    )
    
    if credentials.expired and credentials.refresh_token:
        try:
            request = google_requests.Request()
            credentials.refresh(request)
        except Exception as e:
            logger.error(f"Google credentials 갱신 실패: {str(e)}")
            return None
    
    return credentials
