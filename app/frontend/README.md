# Total Manager Frontend

총무노트 Flutter 프론트엔드 애플리케이션입니다.

## 설정

### 환경 변수

`.env.development` 또는 `.env.production` 파일을 생성하고 다음 변수를 설정하세요:

```env
API_BASE_URL=http://localhost:8000
```

### 의존성 설치

```bash
flutter pub get
```

### JSON Serialization 코드 생성

도메인 모델의 JSON serialization 코드를 생성합니다:

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

## 실행

```bash
flutter run
```

## 기능

### 화면 구조

1. **TMHomeScreen**: 그룹 목록 화면
   - 그룹 목록 조회
   - 그룹 생성

2. **TMGroupScreen**: 그룹 상세 화면
   - 컬렉션 목록 조회
   - 컬렉션 생성 화면으로 이동

3. **TMCollectionCreateScreen**: 컬렉션 생성 화면
   - 제목, 금액, 마감일, 결제 방식 입력
   - 컬렉션 생성

4. **TMCollectionScreen**: 컬렉션 상세 화면
   - 컬렉션 정보 표시
   - 멤버 목록 및 상태 관리
   - 멤버 추가
   - 읽음/납부 처리
   - 공지 발송
   - 로그 화면으로 이동

5. **TMLogsScreen**: 로그 타임라인 화면
   - 이벤트 로그 목록 표시

## 라우팅

메인 화면에서 "총무노트(베타)" 버튼을 통해 TMHomeScreen으로 진입합니다.

## 개발 참고사항

- 모든 네트워크 호출은 `tm_api.dart`에서 처리됩니다
- 비즈니스 로직은 `tm_repository.dart`에서 처리됩니다
- 화면은 상태 관리와 렌더링만 담당합니다
- API 호출 실패 시 사용자에게 에러 메시지를 표시합니다
