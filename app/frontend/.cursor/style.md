# Frontend UI & Style Rules (Total Manager / SSAMDAESHIN)

이 문서는 ssamdaeshin 프로젝트의 프론트엔드(UI/UX) 스타일 규칙이다.
총무노트(total_manager) 모듈을 포함한 모든 신규 프론트엔드 작업은 이 규칙을 따른다.

---

## 1. 기본 원칙 (절대 규칙)

### 1.1 화면에는 로직을 넣지 않는다
- Screen / Widget 파일에는 다음을 **절대** 작성하지 않는다:
  - API 호출
  - 비즈니스 로직
  - 데이터 가공/정렬/필터링
- 화면은 아래만 담당한다:
  - 상태 구독
  - 사용자 이벤트 전달
  - UI 렌더링

### 1.2 단일 책임(SRP)
- 하나의 위젯 = 하나의 역할
- 하나의 파일 = 하나의 목적
- “재사용 목적이 명확하지 않으면” 위젯/함수를 만들지 않는다

---

## 2. 레이어 구조 (강제)

프론트엔드 레이어는 아래 순서를 반드시 따른다:

Screen / Widget
→ Controller / Provider
→ Service or Repository
→ API Client

yaml
Copy code

- Screen → Repository 직접 접근 ❌
- Screen → API Client 직접 호출 ❌

---

## 3. Feature-first 구조 (필수)

- 신규 기능은 반드시 `features/` 아래에 위치한다.
- 총무노트는 아래 경로만 사용한다:

```txt
lib/features/total_manager/
├─ data/          # api, repository
├─ domain/        # model
├─ presentation/  # screen
└─ widgets/       # reusable ui
다른 feature 파일을 수정해서 기능을 끼워 넣지 않는다.

4. UI 스타일 원칙
4.1 디자인 톤
미니멀 / 업무형 / 카드 기반

감성적인 덕담/문구 최소화

“한 화면에서 바로 파악 가능”이 최우선

4.2 카드 중심 UI
모든 주요 정보는 카드 단위로 표현한다.

카드 규칙:

radius: Radii.card

padding: Gaps.card

border 또는 약한 shadow 사용

카드 배경에 강한 색 사용 금지

5. 컬러 사용 규칙
브랜드 primary 색은 CTA 또는 강조에만

상태 표현은 아래 방식만 허용:

chip

아이콘

왼쪽 상태 라인

상태색을 카드 전체 배경으로 쓰지 않는다.

6. 성능 규칙 (항상 고려)
6.1 렌더링
List는 반드시 lazy (ListView.builder, SliverList)

불필요한 rebuild 금지

가능한 const 위젯 사용

6.2 상태 관리
상태 변경 최소화

한 provider가 과도한 상태를 가지지 않도록 분리

화면 전체 rebuild 유발 구조 금지

7. 재사용 규칙
다음 경우에만 공통 위젯 생성 허용:

동일 UI가 2회 이상 사용

명확한 역할 이름이 붙을 수 있을 때

“한 화면에서만 쓰는 위젯”은 분리하지 않는다.

8. 입력 UX 규칙
입력은 AlertDialog 대신 BottomSheet 우선

Confirm 버튼은 하단 고정 

필드 수 최소화 (MVP 기준)

9. 금지 사항 (DON’Ts)
한 화면에 강조색 3개 이상 ❌

UI 파일에 로직 작성 ❌

의미 없는 helper 함수 ❌

디자인 통일성 없는 radius/spacing ❌

한 번만 쓰는 추상화 ❌

10. Cursor 작업 지침
이 규칙을 어기는 코드 제안은 하지 않는다.

UI 생성 시 항상:

“이 위젯이 재사용 대상인가?”

“이 로직은 화면에 있어도 되는가?”
를 먼저 검토한다.