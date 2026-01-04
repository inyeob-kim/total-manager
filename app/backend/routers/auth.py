"""Authentication router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.backend.db.session import get_db
from app.backend.schemas.auth import (
    SignupRequest,
    PhoneLoginRequest,
    KakaoLoginRequest,
    AuthResponse,
    UserOut,
    SendVerificationCodeRequest,
    SendVerificationCodeResponse,
)
from app.backend.services.auth_service import (
    create_user,
    get_user_by_phone,
    create_access_token,
    phone_login,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(
    signup_data: SignupRequest,
    db: Session = Depends(get_db),
):
    """회원가입."""
    user = create_user(db, signup_data)
    access_token = create_access_token(user.id)
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )


@router.post("/login/phone", response_model=AuthResponse)
def login_phone(
    login_data: PhoneLoginRequest,
    db: Session = Depends(get_db),
):
    """전화번호 로그인."""
    user = phone_login(db, login_data)
    access_token = create_access_token(user.id)
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )


@router.post("/login/kakao", response_model=AuthResponse)
def login_kakao(
    login_data: KakaoLoginRequest,
    db: Session = Depends(get_db),
):
    """카카오톡 로그인."""
    # TODO: 카카오톡 로그인 구현
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="카카오톡 로그인은 아직 구현되지 않았습니다"
    )


@router.post("/send-verification-code", response_model=SendVerificationCodeResponse)
def send_verification_code(
    request: SendVerificationCodeRequest,
    db: Session = Depends(get_db),
):
    """SMS 인증 코드 발송."""
    # TODO: SMS 발송 서비스 연동
    # 현재는 임시로 성공 응답만 반환
    return SendVerificationCodeResponse(
        success=True,
        message="인증 코드가 발송되었습니다 (개발 모드: 실제 발송되지 않음)"
    )


@router.get("/me", response_model=UserOut)
def get_current_user(
    db: Session = Depends(get_db),
    # TODO: JWT 토큰에서 user_id 추출
    user_id: str = "user_123",  # 임시
):
    """현재 사용자 정보 조회."""
    from app.backend.db.models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    return UserOut.model_validate(user)

