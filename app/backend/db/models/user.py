"""User database models."""
from sqlalchemy import Column, String, Boolean, DateTime, Index
from sqlalchemy.sql import func
from app.backend.db.base import Base


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)  # ULID string
    phone = Column(String, unique=True, nullable=True, index=True)  # 전화번호
    kakao_id = Column(String, unique=True, nullable=True, index=True)  # 카카오톡 ID
    name = Column(String, nullable=True)  # 사용자 이름
    email = Column(String, nullable=True)  # 이메일
    profile_image_url = Column(String, nullable=True)  # 프로필 이미지 URL
    is_onboarded = Column(Boolean, default=False, nullable=False)  # 온보딩 완료 여부
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    __table_args__ = (
        Index('ix_users_phone', 'phone'),
        Index('ix_users_kakao_id', 'kakao_id'),
    )

