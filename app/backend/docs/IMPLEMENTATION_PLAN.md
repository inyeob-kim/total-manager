# 백엔드 구현 계획 (인증 제외)

## 구현 순서 및 우선순위

인증 시스템을 제외하고, 다음 순서로 구현합니다:

---

## Phase 1: 리마인더 시스템 (최우선)

프론트엔드의 "알림" 탭에서 리마인더 목록을 보여주고 생성할 수 있어야 합니다.

### 1.1 데이터베이스 모델 추가

**새 테이블: `tm_reminders`**
```python
# app/backend/db/models/total_manager.py에 추가

class TMReminder(Base):
    __tablename__ = "tm_reminders"
    
    id = Column(String, primary_key=True)  # ULID
    user_id = Column(String, nullable=False, index=True)  # 임시로 문자열, 나중에 FK
    collection_id = Column(String, ForeignKey("tm_collections.id"), nullable=True)
    title = Column(String, nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    repeat_type = Column(String, nullable=False)  # "none", "daily", "weekly"
    message = Column(String, nullable=True)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**필요한 작업:**
- `models/total_manager.py`에 `TMReminder` 클래스 추가
- Alembic 마이그레이션 생성 (`002_add_reminders_table.py`)

### 1.2 스키마 추가

**`schemas/total_manager.py`에 추가:**
```python
class ReminderCreate(BaseModel):
    collection_id: Optional[str] = None
    title: str
    scheduled_at: datetime
    repeat_type: str  # "none", "daily", "weekly"
    message: Optional[str] = None

class ReminderOut(BaseModel):
    id: str
    user_id: str
    collection_id: Optional[str]
    title: str
    scheduled_at: datetime
    repeat_type: str
    message: Optional[str]
    is_sent: bool
    sent_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    repeat_type: Optional[str] = None
    message: Optional[str] = None
```

### 1.3 서비스 레이어 구현

**`services/total_manager_service.py`에 추가:**
```python
def create_reminder(
    db: Session,
    user_id: str,
    reminder_data: ReminderCreate
) -> TMReminder:
    """Create a new reminder."""
    # collection_id가 있으면 접근 권한 확인
    if reminder_data.collection_id:
        verify_collection_access(db, reminder_data.collection_id, user_id)
    
    reminder = TMReminder(
        id=generate_ulid(),
        user_id=user_id,
        collection_id=reminder_data.collection_id,
        title=reminder_data.title,
        scheduled_at=reminder_data.scheduled_at,
        repeat_type=reminder_data.repeat_type,
        message=reminder_data.message,
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder

def list_reminders(
    db: Session,
    user_id: str,
    is_sent: Optional[bool] = None,
    collection_id: Optional[str] = None
) -> List[TMReminder]:
    """List reminders for a user."""
    query = db.query(TMReminder).filter(TMReminder.user_id == user_id)
    
    if is_sent is not None:
        query = query.filter(TMReminder.is_sent == is_sent)
    if collection_id:
        query = query.filter(TMReminder.collection_id == collection_id)
    
    return query.order_by(TMReminder.scheduled_at.asc()).all()

def get_reminder(db: Session, reminder_id: str) -> Optional[TMReminder]:
    """Get a reminder by ID."""
    return db.query(TMReminder).filter(TMReminder.id == reminder_id).first()

def verify_reminder_access(db: Session, reminder_id: str, user_id: str) -> TMReminder:
    """Verify reminder exists and belongs to user."""
    reminder = get_reminder(db, reminder_id)
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    if reminder.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return reminder

def update_reminder(
    db: Session,
    reminder_id: str,
    user_id: str,
    reminder_data: ReminderUpdate
) -> TMReminder:
    """Update a reminder."""
    reminder = verify_reminder_access(db, reminder_id, user_id)
    
    if reminder_data.title is not None:
        reminder.title = reminder_data.title
    if reminder_data.scheduled_at is not None:
        reminder.scheduled_at = reminder_data.scheduled_at
    if reminder_data.repeat_type is not None:
        reminder.repeat_type = reminder_data.repeat_type
    if reminder_data.message is not None:
        reminder.message = reminder_data.message
    
    db.commit()
    db.refresh(reminder)
    return reminder

def delete_reminder(db: Session, reminder_id: str, user_id: str) -> None:
    """Delete a reminder."""
    reminder = verify_reminder_access(db, reminder_id, user_id)
    db.delete(reminder)
    db.commit()

def send_reminder(db: Session, reminder_id: str, user_id: str) -> TMReminder:
    """Send a reminder immediately."""
    reminder = verify_reminder_access(db, reminder_id, user_id)
    
    reminder.is_sent = True
    reminder.sent_at = datetime.now(timezone.utc)
    
    # 이벤트 로그 생성
    if reminder.collection_id:
        log = TMEventLog(
            id=generate_ulid(),
            collection_id=reminder.collection_id,
            type=LogType.REMINDER_SENT,
            message=reminder.message or reminder.title,
        )
        db.add(log)
    
    # 반복 리마인더 처리
    if reminder.repeat_type == "daily":
        # 다음날 리마인더 생성
        next_reminder = TMReminder(
            id=generate_ulid(),
            user_id=user_id,
            collection_id=reminder.collection_id,
            title=reminder.title,
            scheduled_at=reminder.scheduled_at + timedelta(days=1),
            repeat_type=reminder.repeat_type,
            message=reminder.message,
        )
        db.add(next_reminder)
    elif reminder.repeat_type == "weekly":
        # 다음주 리마인더 생성
        next_reminder = TMReminder(
            id=generate_ulid(),
            user_id=user_id,
            collection_id=reminder.collection_id,
            title=reminder.title,
            scheduled_at=reminder.scheduled_at + timedelta(weeks=1),
            repeat_type=reminder.repeat_type,
            message=reminder.message,
        )
        db.add(next_reminder)
    
    db.commit()
    db.refresh(reminder)
    return reminder
```

### 1.4 라우터 추가

**`routers/total_manager.py`에 추가:**
```python
@router.post("/reminders", response_model=ReminderOut, status_code=status.HTTP_201_CREATED)
def create_reminder_endpoint(
    reminder_data: ReminderCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Create a new reminder."""
    from app.backend.services.total_manager_service import create_reminder
    return create_reminder(db, user_id, reminder_data)

@router.get("/reminders", response_model=List[ReminderOut])
def list_reminders_endpoint(
    is_sent: Optional[bool] = None,
    collection_id: Optional[str] = None,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """List reminders for the current user."""
    from app.backend.services.total_manager_service import list_reminders
    return list_reminders(db, user_id, is_sent=is_sent, collection_id=collection_id)

@router.get("/reminders/{reminder_id}", response_model=ReminderOut)
def get_reminder_endpoint(
    reminder_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get a reminder by ID."""
    from app.backend.services.total_manager_service import verify_reminder_access
    return verify_reminder_access(db, reminder_id, user_id)

@router.patch("/reminders/{reminder_id}", response_model=ReminderOut)
def update_reminder_endpoint(
    reminder_id: str,
    reminder_data: ReminderUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Update a reminder."""
    from app.backend.services.total_manager_service import update_reminder
    return update_reminder(db, reminder_id, user_id, reminder_data)

@router.delete("/reminders/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder_endpoint(
    reminder_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Delete a reminder."""
    from app.backend.services.total_manager_service import delete_reminder
    delete_reminder(db, reminder_id, user_id)
    return None

@router.post("/reminders/{reminder_id}/send", response_model=ReminderOut)
def send_reminder_endpoint(
    reminder_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Send a reminder immediately."""
    from app.backend.services.total_manager_service import send_reminder
    return send_reminder(db, reminder_id, user_id)
```

---

## Phase 2: 기존 API 보완

### 2.1 그룹 API 확장

**추가할 엔드포인트:**
- `GET /total-manager/groups/{group_id}` - 그룹 상세 조회
- `PATCH /total-manager/groups/{group_id}` - 그룹 수정
- `DELETE /total-manager/groups/{group_id}` - 그룹 삭제

**스키마 추가:**
```python
class GroupUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[GroupType] = None

class GroupDetailOut(GroupOut):
    collections_count: int
    total_amount: int
```

**서비스 함수:**
```python
def update_group(
    db: Session,
    group_id: str,
    owner_id: str,
    group_data: GroupUpdate
) -> TMGroup:
    """Update a group."""
    group = verify_group_owner(db, group_id, owner_id)
    
    if group_data.name is not None:
        group.name = group_data.name
    if group_data.type is not None:
        group.type = group_data.type
    
    db.commit()
    db.refresh(group)
    return group

def delete_group(db: Session, group_id: str, owner_id: str) -> None:
    """Delete a group."""
    group = verify_group_owner(db, group_id, owner_id)
    db.delete(group)
    db.commit()

def get_group_detail(db: Session, group_id: str, owner_id: str) -> GroupDetailOut:
    """Get group detail with statistics."""
    group = verify_group_owner(db, group_id, owner_id)
    
    collections = db.query(TMCollection).filter(TMCollection.group_id == group_id).all()
    collections_count = len(collections)
    total_amount = sum(c.amount for c in collections)
    
    return GroupDetailOut(
        id=group.id,
        owner_id=group.owner_id,
        name=group.name,
        type=group.type,
        created_at=group.created_at,
        collections_count=collections_count,
        total_amount=total_amount,
    )
```

### 2.2 컬렉션 API 확장

**추가할 엔드포인트:**
- `PATCH /total-manager/collections/{collection_id}` - 컬렉션 수정
- `DELETE /total-manager/collections/{collection_id}` - 컬렉션 삭제
- `GET /total-manager/collections/{collection_id}/summary` - 컬렉션 요약 정보

**스키마 추가:**
```python
class CollectionUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[int] = None
    due_date: Optional[date] = None
    payment_type: Optional[PaymentType] = None
    payment_value: Optional[str] = None

class CollectionSummaryOut(BaseModel):
    id: str
    title: str
    amount: int
    due_date: date
    status: CollectionStatus
    total_members: int
    read_members: int
    paid_members: int
    current_amount: int  # paid_members * (amount / total_members) 또는 실제 납부액
    payment_type: PaymentType
    payment_value: str
```

**서비스 함수:**
```python
def update_collection(
    db: Session,
    collection_id: str,
    owner_id: str,
    collection_data: CollectionUpdate
) -> TMCollection:
    """Update a collection."""
    collection = verify_collection_access(db, collection_id, owner_id)
    
    if collection_data.title is not None:
        collection.title = collection_data.title
    if collection_data.amount is not None:
        collection.amount = collection_data.amount
    if collection_data.due_date is not None:
        collection.due_date = collection_data.due_date
        # 상태 재계산
        today = date.today()
        if collection_data.due_date <= today:
            collection.status = CollectionStatus.CLOSED
        elif (collection_data.due_date - today).days <= 3:
            collection.status = CollectionStatus.DUE_SOON
        else:
            collection.status = CollectionStatus.ACTIVE
    if collection_data.payment_type is not None:
        collection.payment_type = collection_data.payment_type
    if collection_data.payment_value is not None:
        collection.payment_value = collection_data.payment_value
    
    db.commit()
    db.refresh(collection)
    return collection

def delete_collection(db: Session, collection_id: str, owner_id: str) -> None:
    """Delete a collection."""
    collection = verify_collection_access(db, collection_id, owner_id)
    db.delete(collection)
    db.commit()

def get_collection_summary(
    db: Session,
    collection_id: str,
    owner_id: str
) -> CollectionSummaryOut:
    """Get collection summary with statistics."""
    collection = verify_collection_access(db, collection_id, owner_id)
    
    members = db.query(TMMemberStatus).filter(
        TMMemberStatus.collection_id == collection_id
    ).all()
    
    total_members = len(members)
    read_members = sum(1 for m in members if m.read_at is not None)
    paid_members = sum(1 for m in members if m.paid_at is not None)
    
    # 현재 모금액 계산 (간단히: 납부한 멤버 수 * (목표 금액 / 전체 멤버 수))
    # 실제로는 각 멤버의 납부액을 추적해야 하지만, MVP에서는 간단히 계산
    current_amount = int((paid_members / total_members * collection.amount)) if total_members > 0 else 0
    
    return CollectionSummaryOut(
        id=collection.id,
        title=collection.title,
        amount=collection.amount,
        due_date=collection.due_date,
        status=collection.status,
        total_members=total_members,
        read_members=read_members,
        paid_members=paid_members,
        current_amount=current_amount,
        payment_type=collection.payment_type,
        payment_value=collection.payment_value,
    )
```

### 2.3 멤버 API 확장

**추가할 엔드포인트:**
- `PATCH /total-manager/members/{member_id}` - 멤버 정보 수정
- `DELETE /total-manager/members/{member_id}` - 멤버 삭제
- `POST /total-manager/collections/{collection_id}/members/bulk` - 멤버 일괄 추가

**스키마 추가:**
```python
class MemberUpdate(BaseModel):
    display_name: Optional[str] = None
    phone: Optional[str] = None

class BulkMemberCreate(BaseModel):
    members: List[MemberCreate]
```

**서비스 함수:**
```python
def update_member(
    db: Session,
    member_id: str,
    owner_id: str,
    member_data: MemberUpdate
) -> TMMemberStatus:
    """Update a member."""
    member = verify_member_access(db, member_id, owner_id)
    
    if member_data.display_name is not None:
        member.display_name = member_data.display_name
    if member_data.phone is not None:
        member.phone = member_data.phone
    
    db.commit()
    db.refresh(member)
    return member

def delete_member(db: Session, member_id: str, owner_id: str) -> None:
    """Delete a member."""
    member = verify_member_access(db, member_id, owner_id)
    db.delete(member)
    db.commit()

def bulk_add_members(
    db: Session,
    collection_id: str,
    owner_id: str,
    bulk_data: BulkMemberCreate
) -> dict:
    """Add multiple members at once."""
    verify_collection_access(db, collection_id, owner_id)
    
    created = []
    failed = []
    
    for member_data in bulk_data.members:
        try:
            member = TMMemberStatus(
                id=generate_ulid(),
                collection_id=collection_id,
                display_name=member_data.display_name,
                phone=member_data.phone,
            )
            db.add(member)
            created.append(member)
        except Exception as e:
            failed.append({"member": member_data.dict(), "error": str(e)})
    
    db.commit()
    
    # Refresh created members
    for member in created:
        db.refresh(member)
    
    return {
        "created": len(created),
        "failed": len(failed),
        "members": created,
        "errors": failed if failed else None,
    }
```

### 2.4 로그 API 확장

**추가할 엔드포인트:**
- `GET /total-manager/logs` - 전체 로그 조회 (사용자별)
- `GET /total-manager/logs/stats` - 로그 통계

**서비스 함수:**
```python
def list_all_logs(
    db: Session,
    user_id: str,
    collection_id: Optional[str] = None,
    log_type: Optional[LogType] = None,
    limit: int = 50,
    offset: int = 0
) -> dict:
    """List all logs for a user."""
    # 사용자가 소유한 그룹의 컬렉션들 조회
    groups = db.query(TMGroup).filter(TMGroup.owner_id == user_id).all()
    group_ids = [g.id for g in groups]
    
    collections = db.query(TMCollection).filter(
        TMCollection.group_id.in_(group_ids)
    ).all()
    collection_ids = [c.id for c in collections]
    
    query = db.query(TMEventLog).filter(
        TMEventLog.collection_id.in_(collection_ids)
    )
    
    if collection_id:
        query = query.filter(TMEventLog.collection_id == collection_id)
    if log_type:
        query = query.filter(TMEventLog.type == log_type)
    
    total = query.count()
    logs = query.order_by(TMEventLog.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "logs": logs,
    }

def get_log_stats(db: Session, user_id: str) -> dict:
    """Get log statistics for a user."""
    groups = db.query(TMGroup).filter(TMGroup.owner_id == user_id).all()
    group_ids = [g.id for g in groups]
    
    collections = db.query(TMCollection).filter(
        TMCollection.group_id.in_(group_ids)
    ).all()
    collection_ids = [c.id for c in collections]
    
    logs = db.query(TMEventLog).filter(
        TMEventLog.collection_id.in_(collection_ids)
    ).all()
    
    by_type = {}
    for log_type in LogType:
        by_type[log_type.value] = sum(1 for log in logs if log.type == log_type)
    
    # 최근 활동 (날짜별)
    from collections import defaultdict
    recent_activity = defaultdict(int)
    for log in logs:
        date_key = log.created_at.date().isoformat()
        recent_activity[date_key] += 1
    
    return {
        "total_logs": len(logs),
        "by_type": by_type,
        "recent_activity": [
            {"date": date, "count": count}
            for date, count in sorted(recent_activity.items(), reverse=True)[:7]
        ],
    }
```

---

## Phase 3: 사용자 설정 (임시 user_id 사용)

인증이 완료되기 전까지는 `get_current_user_id()`로 임시 user_id를 사용합니다.

### 3.1 데이터베이스 모델 추가

**새 테이블 4개:**
1. `user_settings` - 알림 설정
2. `user_payment_methods` - 결제 수단
3. `user_security_settings` - 보안 설정 (선택적)
4. `user_login_devices` - 로그인 기기 (선택적)

**모델 파일: `db/models/user_settings.py` 생성:**
```python
class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id = Column(String, primary_key=True)  # ULID
    user_id = Column(String, unique=True, nullable=False, index=True)
    push_notifications_enabled = Column(Boolean, default=True)
    email_notifications_enabled = Column(Boolean, default=False)
    reminder_notifications_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UserPaymentMethod(Base):
    __tablename__ = "user_payment_methods"
    
    id = Column(String, primary_key=True)  # ULID
    user_id = Column(String, nullable=False, index=True)
    bank_name = Column(String, nullable=False)
    account_number = Column(String, nullable=False)
    account_holder = Column(String, nullable=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 3.2 API 엔드포인트

**새 라우터: `routers/user_settings.py` 생성:**
- `GET /users/me/settings/notifications` - 알림 설정 조회
- `PATCH /users/me/settings/notifications` - 알림 설정 수정
- `GET /users/me/payment-methods` - 결제 수단 목록
- `POST /users/me/payment-methods` - 결제 수단 추가
- `PATCH /users/me/payment-methods/{id}` - 결제 수단 수정
- `DELETE /users/me/payment-methods/{id}` - 결제 수단 삭제
- `POST /users/me/payment-methods/{id}/set-default` - 기본 설정

---

## 구현 체크리스트

### Phase 1: 리마인더 시스템
- [ ] `TMReminder` 모델 추가
- [ ] Alembic 마이그레이션 생성
- [ ] `ReminderCreate`, `ReminderOut`, `ReminderUpdate` 스키마 추가
- [ ] 리마인더 CRUD 서비스 함수 구현
- [ ] 리마인더 라우터 엔드포인트 추가
- [ ] 테스트

### Phase 2: 기존 API 보완
- [ ] 그룹 상세/수정/삭제 API
- [ ] 컬렉션 수정/삭제/요약 API
- [ ] 멤버 수정/삭제/일괄추가 API
- [ ] 전체 로그 조회/통계 API
- [ ] 테스트

### Phase 3: 사용자 설정
- [ ] `UserSettings`, `UserPaymentMethod` 모델 추가
- [ ] Alembic 마이그레이션 생성
- [ ] 사용자 설정 스키마 추가
- [ ] 사용자 설정 서비스 함수 구현
- [ ] 사용자 설정 라우터 추가
- [ ] 테스트

---

## 주의사항

1. **임시 user_id 사용**: 인증이 완료되기 전까지 `get_current_user_id()`는 하드코딩된 값(`"user_123"`)을 반환합니다. 나중에 실제 인증 시스템과 연동할 때만 수정하면 됩니다.

2. **데이터베이스 마이그레이션**: 각 Phase마다 Alembic 마이그레이션을 생성하고 적용해야 합니다.

3. **에러 처리**: 모든 엔드포인트에서 적절한 에러 처리(404, 403 등)를 구현해야 합니다.

4. **테스트**: 각 기능 구현 후 API 테스트를 수행해야 합니다.

5. **프론트엔드 연동**: 백엔드 구현 후 프론트엔드의 `tm_api.dart`에 새로운 엔드포인트를 추가해야 합니다.

