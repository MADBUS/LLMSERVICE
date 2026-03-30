# 날씨 기반 코디 추천 시스템

사용자의 옷장 데이터와 실시간 날씨 정보를 기반으로 최적의 코디를 추천하는 AI 서비스입니다.

## 주요 기능

- **날씨 기반 추천**: 기상청 API로 실시간 날씨를 조회하여 기온/강수에 맞는 옷 추천
- **TPO 맞춤 추천**: 데이트, 출근, 운동 등 상황에 맞는 코디 제안
- **RAG 기반 검색**: 벡터DB(ChromaDB)로 사용자 옷장에서 관련 옷 검색
- **LLM 코디 생성**: Gemini API로 자연스러운 코디 추천 답변 생성

---

## 시스템 아키텍처

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   사용자    │────▶│   main.py   │────▶│  LLM 응답   │
└─────────────┘     └──────┬──────┘     └─────────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ 기상청 API  │   │   MySQL     │   │  ChromaDB   │
│ (날씨 조회) │   │ (옷 데이터) │   │ (벡터 검색) │
└─────────────┘   └─────────────┘   └─────────────┘
```

---

## 워크플로우

```
1. 사용자 질문 입력 (예: "오늘 데이트 코디 추천해줘")
        │
        ▼
2. 기상청 API로 현재 날씨 조회
   - 기온, 습도, 강수 여부 확인
   - 계절감/보온성 레벨 결정
        │
        ▼
3. 질문 + 날씨 정보로 임베딩 생성 (Gemini Embedding)
        │
        ▼
4. ChromaDB에서 관련 옷 검색 (벡터 유사도)
   - 카테고리별 분류 (아우터/상의/하의/신발)
        │
        ▼
5. LLM(Gemini)에게 코디 추천 요청
   - 날씨 정보 + 옷장 데이터 + 사용자 요청 전달
        │
        ▼
6. 최종 코디 추천 응답 출력
```

---

## 핵심 코드 구조

```
LLMSERVICE/
├── main.py                      # 메인 실행 파일
├── setup_db.py                  # DB 초기화 & 샘플 데이터 삽입
├── .env.dev                     # 환경변수 (API 키, DB 설정)
├── requirements.txt             # 의존성 패키지
│
└── src/
    ├── models/
    │   └── clothing.py          # 옷 데이터 모델 (카테고리/색상/계절/스타일)
    │
    ├── database/
    │   ├── mysql_connection.py  # MySQL 연결 관리
    │   └── clothing_repository.py # 옷 CRUD 레포지토리
    │
    ├── weather_service.py       # 기상청 API 연동
    ├── clothing_service.py      # 옷 관리 (MySQL + 벡터DB 동기화)
    ├── embedding_service.py     # Gemini 임베딩 서비스
    ├── vector_store.py          # ChromaDB 벡터 저장/검색
    ├── llm_service.py           # Gemini LLM 텍스트 생성
    └── outfit_recommendation_service.py  # 코디 추천 통합 서비스
```

### 핵심 파일 설명

| 파일 | 역할 |
|------|------|
| `main.py` | CLI 인터페이스, 사용자 입력 처리 |
| `weather_service.py` | 기상청 단기예보 API 호출, 날씨 정보 파싱 |
| `clothing_service.py` | MySQL 옷 데이터와 ChromaDB 벡터 동기화 |
| `outfit_recommendation_service.py` | 날씨 + 옷장 + LLM 연결하여 코디 추천 |
| `llm_service.py` | Gemini API로 자연어 응답 생성 |

---

## API 발급 안내

### 1. Gemini API (필수)

Google AI Studio에서 무료 발급

1. https://aistudio.google.com/app/apikey 접속
2. Google 계정으로 로그인
3. "Create API Key" 클릭
4. 생성된 키 복사

```env
GEMINI_API_KEY=발급받은_키
```

### 2. 기상청_단기예보 조회서비스 (필수)

공공데이터포털에서 무료 발급 (하루 10,000회 무료)

**API 신청 페이지**: https://www.data.go.kr/iim/api/selectAPIAcountView.do

1. https://www.data.go.kr 접속
2. 회원가입/로그인
3. "기상청 단기예보" 검색
4. "기상청_단기예보 ((구)_동네예보) 조회서비스" 활용신청
5. 즉시 승인 → API 키 발급

```env
KMA_API_KEY=발급받은_키(디코딩된_키_사용)
KMA_API_ENDPOINT=https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0
```

> **주의**: 공공데이터포털에서 **"일반 인증키(Decoding)"**를 사용하세요. 인코딩된 키를 사용하면 이중 인코딩되어 401 에러가 발생합니다.

### 3. MySQL (필수)

로컬 또는 원격 MySQL 서버 필요

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=비밀번호
MYSQL_DATABASE=clothing_db
```

---

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env.dev` 파일 수정:

```env
# Gemini API
GEMINI_API_KEY=your_gemini_api_key

# 기상청 API
KMA_API_KEY=your_kma_api_key
KMA_API_ENDPOINT=https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0

# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=clothing_db
```

### 3. 데이터베이스 초기화

```bash
python setup_db.py
```

샘플 옷 29개가 추가됩니다:
- 아우터 6개 (패딩, 트렌치코트, 블레이저 등)
- 상의 8개 (티셔츠, 셔츠, 니트 등)
- 하의 6개 (슬랙스, 청바지, 치노 등)
- 신발 5개 (운동화, 로퍼, 부츠 등)
- 액세서리 4개 (벨트, 모자, 머플러, 가방)

### 4. 실행

```bash
python main.py
```

---

## 사용 예시

```
==================================================
[날씨 기반 코디 추천 시스템]
==================================================

>> 서울 현재 날씨: 맑음, 기온 15.0°C (체감 14.2°C), 습도 45%

>> 등록된 옷: 29개

명령어:
  - 질문 입력: 코디 추천 받기
  - 'list': 등록된 옷 목록
  - 'weather': 현재 날씨
  - 'quit': 종료
--------------------------------------------------

[질문] 오늘 데이트 코디 추천해줘

[코디 추천]
------------------------------
오늘 날씨가 15도로 선선하니, 가을 느낌의 데이트룩을 추천드릴게요!

상의: 베이지 맨투맨
하의: 인디고 청바지
아우터: 베이지 트렌치코트
신발: 흰색 운동화

베이지 톤으로 통일감을 주면서, 청바지로 캐주얼한 포인트를 줬어요.
트렌치코트는 15도 날씨에 딱 맞는 보온성이고, 데이트에 어울리는
깔끔한 분위기를 연출할 수 있습니다!
```

### 추천 질문 예시

| 상황 | 질문 예시 |
|------|----------|
| 데이트 | "오늘 데이트 코디 추천해줘" |
| 출근 | "출근할 때 입을 옷 추천해줘" |
| 운동 | "운동하러 갈 건데 뭐 입을까?" |
| 면접 | "면접 보러 가는데 코디 추천" |
| 날씨 | "비 오는 날 뭐 입지?" |

---

## 지원 도시

기상청 API 격자 좌표가 설정된 도시:

| 도시 | 격자 좌표 (X, Y) |
|------|-----------------|
| 서울 | (60, 127) |
| 부산 | (98, 76) |
| 인천 | (55, 124) |
| 대구 | (89, 90) |
| 대전 | (67, 100) |
| 광주 | (58, 74) |
| 수원 | (60, 121) |
| 울산 | (102, 84) |
| 세종 | (66, 103) |
| 제주 | (52, 38) |

---

## 옷 데이터 구조

### 카테고리
- 아우터, 상의, 하의, 원피스, 신발, 액세서리

### 색상
- 블랙, 화이트, 그레이, 네이비, 베이지, 브라운, 레드, 블루, 그린, 옐로우, 핑크, 퍼플, 오렌지, 멀티컬러

### 계절
- 봄, 여름, 가을, 겨울, 사계절

### 스타일
- 캐주얼, 포멀, 스포티, 스트릿, 미니멀, 빈티지

### 보온성 (1~5)
- 1: 시원함 (여름용)
- 3: 보통 (봄가을용)
- 5: 따뜻함 (겨울용)

---

## 기술 스택

| 구성요소 | 기술 |
|----------|------|
| Language | Python 3.10+ |
| LLM | Google Gemini 2.5 Flash |
| Embedding | Gemini Embedding |
| Vector DB | ChromaDB |
| Database | MySQL |
| Weather API | 기상청 단기예보 API |

---

## 핵심 개념

### RAG (Retrieval-Augmented Generation)

"검색 + 생성" 기법. LLM이 모르는 정보(사용자 옷장)를 먼저 검색해서 제공하는 방식.

```
사용자 질문 → 벡터 검색 → 관련 옷 찾기 → LLM에게 전달 → 코디 추천 생성
```

### 벡터 (Embedding)

텍스트를 숫자 리스트로 변환한 것. 의미가 비슷하면 숫자도 비슷해짐.

```python
"따뜻한 겨울 코트" → [0.82, 0.15, 0.43, ...]
"패딩 점퍼"       → [0.81, 0.14, 0.44, ...]  # 거의 비슷!
"여름 반팔"       → [0.12, 0.91, 0.03, ...]  # 완전 다름
```

---

## 테스트 실행

```bash
python -m pytest tests/ -v
```

---

## 라이선스

MIT License
