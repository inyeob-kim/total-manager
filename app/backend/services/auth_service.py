"""Authentication service."""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.backend.db.models.user import User
from app.backend.schemas.auth import SignupRequest, PhoneLoginRequest, UserOut
from app.backend.utils.ulid import generate_ulid
from datetime import datetime, timedelta
import jwt
from app.backend.core.config import settings


def create_user(db: Session, signup_data: SignupRequest) -> User:
    """사용자 생성."""
    # 전화번호 중복 확인
    existing_user = db.query(User).filter(User.phone == signup_data.phone).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 가입된 전화번호입니다"
        )
    
    # TODO: SMS 인증 코드 검증 (선택적)
    # if signup_data.verification_code:
    #     verify_code(signup_data.phone, signup_data.verification_code)
    
    user = User(
        id=generate_ulid(),
        name=signup_data.name,
        phone=signup_data.phone,
        email=signup_data.email,
        is_onboarded=False,
    )
    
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 가입된 전화번호입니다"
        )


def get_user_by_phone(db: Session, phone: str) -> User | None:
    """전화번호로 사용자 조회."""
    return db.query(User).filter(User.phone == phone).first()


def create_access_token(user_id: str) -> str:
    """JWT 액세스 토큰 생성."""
    # TODO: 실제 JWT 구현 시 SECRET_KEY 사용
    # 현재는 간단한 토큰 생성 (임시)
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=7),
        "iat": datetime.utcnow(),
    }
    # 실제 구현 시: return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    # 임시로 간단한 토큰 반환
    return f"token_{user_id}_{datetime.utcnow().timestamp()}"


def verify_access_token(token: str) -> str | None:
    """JWT 토큰 검증 및 user_id 반환."""
    # TODO: 실제 JWT 검증 구현
    # 현재는 임시로 토큰에서 user_id 추출
    if token.startswith("token_"):
        parts = token.split("_")
        if len(parts) >= 2:
            return parts[1]
    return None


def phone_login(db: Session, login_data: PhoneLoginRequest) -> User:
    """전화번호 로그인."""
    user = get_user_by_phone(db, login_data.phone)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="가입되지 않은 전화번호입니다"
        )
    
    # TODO: SMS 인증 코드 검증 (선택적)
    # if login_data.verification_code:
    #     verify_code(login_data.phone, login_data.verification_code)
    
    return user

