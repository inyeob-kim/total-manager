"""Authentication schemas."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class SignupRequest(BaseModel):
    """회원가입 요청 스키마."""
    name: str = Field(..., min_length=1, max_length=50, description="사용자 이름")
    phone: str = Field(..., min_length=10, max_length=11, description="전화번호 (숫자만)")
    email: Optional[str] = Field(None, description="이메일 (선택)")
    verification_code: Optional[str] = Field(None, description="SMS 인증 코드 (선택)")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """전화번호 검증 (숫자만)."""
        if not v.isdigit():
            raise ValueError('전화번호는 숫자만 입력 가능합니다')
        if len(v) < 10 or len(v) > 11:
            raise ValueError('전화번호는 10~11자리여야 합니다')
        return v


class PhoneLoginRequest(BaseModel):
    """전화번호 로그인 요청 스키마."""
    phone: str = Field(..., min_length=10, max_length=11, description="전화번호")
    verification_code: Optional[str] = Field(None, description="SMS 인증 코드 (선택)")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """전화번호 검증."""
        if not v.isdigit():
            raise ValueError('전화번호는 숫자만 입력 가능합니다')
        return v


class KakaoLoginRequest(BaseModel):
    """카카오톡 로그인 요청 스키마."""
    kakao_token: str = Field(..., description="카카오 액세스 토큰")
    kakao_id: str = Field(..., description="카카오 사용자 ID")


class UserOut(BaseModel):
    """사용자 정보 응답 스키마."""
    id: str
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    profile_image_url: Optional[str] = None
    is_onboarded: bool = False
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """인증 응답 스키마."""
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class SendVerificationCodeRequest(BaseModel):
    """SMS 인증 코드 발송 요청 스키마."""
    phone: str = Field(..., min_length=10, max_length=11, description="전화번호")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """전화번호 검증."""
        if not v.isdigit():
            raise ValueError('전화번호는 숫자만 입력 가능합니다')
        return v


class SendVerificationCodeResponse(BaseModel):
    """SMS 인증 코드 발송 응답 스키마."""
    success: bool = True
    message: str = "인증 코드가 발송되었습니다"

