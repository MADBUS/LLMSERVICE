# RAG 기반 상품 추천 시스템

LLM(Gemini)과 벡터DB(ChromaDB)를 활용한 시맨틱 검색 기반 추천 시스템

## 기술 스택

| 구성요소 | 기술 |
|----------|------|
| 언어 | Python |
| LLM | Gemini 2.5 Flash |
| 임베딩 | Gemini Embedding |
| 벡터DB | ChromaDB |

---

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. API 키 설정
`.env.dev.example`을 복사하여 `.env.dev` 파일 생성:
```bash
cp .env.dev.example .env.dev
```

`.env.dev` 파일에 Gemini API 키 입력:
```
GEMINI_API_KEY=your-api-key-here
```

API 키 발급: https://aistudio.google.com/app/apikey

### 3. 실행
```bash
py main.py
```

---

## 프로젝트 구조

```
LLMSERVICE/
├── main.py                      # 데모 실행 파일
├── src/
│   ├── embedding_service.py     # 텍스트 → 벡터 변환
│   ├── vector_store.py          # 벡터 저장/검색 (ChromaDB)
│   ├── llm_service.py           # LLM 답변 생성 (Gemini)
│   ├── rag_pipeline.py          # RAG 파이프라인 (위 3개 연결)
│   ├── recommendation_service.py # 추천 서비스 API
│   └── init_data.py             # 샘플 데이터 초기화
├── tests/                       # 테스트 코드
├── chroma_data/                 # 벡터DB 영구 저장 (자동 생성)
├── .env.dev                     # API 키 (git 제외)
└── .env.dev.example             # API 키 예시
```

---

## 핵심 개념

### RAG (Retrieval-Augmented Generation)

"검색 + 생성" 기법. LLM이 모르는 정보를 먼저 검색해서 제공하는 방식.

```
사용자 질문 → 벡터 검색 → 관련 정보 찾기 → LLM에게 전달 → 답변 생성
```

### 벡터 (Embedding)

텍스트를 숫자 리스트로 변환한 것. 의미가 비슷하면 숫자도 비슷해짐.

```python
"노트북" → [0.82, 0.15, 0.43, ...]
"랩탑"   → [0.81, 0.14, 0.44, ...]  # 거의 비슷!
"바나나" → [0.12, 0.91, 0.03, ...]  # 완전 다름
```

### 벡터DB vs 일반 DB

| 비교 | 벡터DB (ChromaDB) | 일반 DB (MySQL) |
|------|-------------------|-----------------|
| 100만 개 검색 | ~10ms | ~10초 이상 |
| 검색 방식 | ANN 인덱스 | 전체 스캔 |
| 용도 | 유사도 검색 | 정확한 값 검색 |

---

## 코드 실행 흐름

### 1. 데이터 저장 (최초 1회)

```python
# init_data.py
text = "LG 그램 16 - 초경량 노트북"
embedding = embedding_service.embed_text(text)  # 텍스트 → 벡터
vector_store.add_item(id, embedding, metadata)  # 벡터DB에 저장
```

### 2. 사용자 질문 처리

```python
# rag_pipeline.py

# STEP 1: 질문을 벡터로 변환
query_embedding = embedding_service.embed_text("가벼운 노트북 추천해줘")
# → [0.11, -0.33, 0.55, ...]

# STEP 2: 벡터DB에서 유사한 상품 검색
results = vector_store.search(query_embedding, n_results=5)
# → LG 그램, 맥북 에어 등 비슷한 상품 반환

# STEP 3: LLM에게 답변 생성 요청
response = llm_service.generate_recommendation(query, results)
# → "가벼운 노트북을 찾으시는군요! LG 그램 16을 추천드립니다..."
```

### 전체 흐름 다이어그램

```
┌─────────────────────────────────────────────────────────────┐
│  사용자: "가벼운 노트북 추천해줘"                              │
└─────────────────┬───────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  EmbeddingService.embed_text()                              │
│  "가벼운 노트북 추천해줘" → [0.11, -0.33, 0.55, ...]         │
└─────────────────┬───────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  VectorStore.search()                                       │
│  벡터 비교 → LG 그램, 맥북 에어 등 유사 상품 5개 반환         │
└─────────────────┬───────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  LLMService.generate_recommendation()                       │
│  검색 결과 + 질문 → Gemini API → 자연어 답변 생성            │
└─────────────────┬───────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  "LG 그램 16을 추천드립니다. 무게 1.19kg으로 가볍고..."       │
└─────────────────────────────────────────────────────────────┘
```

---

## RAG 추천 시스템 핵심 구조

### 전체 흐름

```
사용자 질문 → 임베딩 변환 → 벡터 검색 → LLM 답변 생성
```

### 1. 데이터 저장 단계 (`init_data.py`)

| 단계 | 코드 위치 | 설명 |
|------|-----------|------|
| 상품 정의 | `init_data.py:9-59` | SAMPLE_PRODUCTS 리스트에 상품 데이터 정의 |
| 중복 확인 | `init_data.py:99` | `vector_store.exists(product["id"])` |
| 텍스트 결합 | `init_data.py:104` | `{name} - {description}` 형태로 결합 |
| 임베딩 변환 | `init_data.py:105` | `embedding_service.embed_text()` 호출 |
| 벡터DB 저장 | `init_data.py:108-117` | `vector_store.add_item()` 호출 |

### 2. 검색 단계 (`rag_pipeline.py:41-48`)

| 단계 | 코드 | 설명 |
|------|------|------|
| 질문 임베딩 | `query_embedding = self.embedding_service.embed_text(user_query)` | 사용자 질문을 벡터로 변환 |
| 유사도 검색 | `search_results = self.vector_store.search(query_embedding, n_results)` | 코사인 유사도로 가장 비슷한 상품 검색 |
| 컨텍스트 추출 | `context_items = [result["metadata"] for result in search_results]` | 검색된 상품의 메타데이터 추출 |

### 3. 답변 생성 단계 (`rag_pipeline.py:50-51`)

| 단계 | 코드 | 설명 |
|------|------|------|
| LLM 호출 | `response = self.llm_service.generate_recommendation(user_query, context_items)` | 질문 + 검색 결과를 LLM에 전달 |
| 답변 반환 | `return response` | 자연어 추천 답변 반환 |

### 핵심 용어 (단계별)

| 단계 | 용어 | 의미 |
|------|------|------|
| 저장 | Embedding | 텍스트 → 숫자 벡터 변환 |
| 저장 | Upsert | 있으면 스킵, 없으면 추가 |
| 검색 | Query Embedding | 질문 텍스트의 벡터 표현 |
| 검색 | Cosine Similarity | 벡터 간 유사도 (1에 가까울수록 유사) |
| 검색 | n_results | 반환할 검색 결과 수 |
| 생성 | Context | LLM에 제공되는 참고 정보 |
| 생성 | Prompt | LLM에 전달되는 전체 입력 |

---

## 핵심 파일 설명

### embedding_service.py
텍스트를 벡터(숫자 리스트)로 변환. Gemini Embedding API 사용.

```python
service = EmbeddingService(api_key)
vector = service.embed_text("노트북")  # → [0.12, -0.34, ...]
```

### vector_store.py
벡터 저장 및 유사도 검색. ChromaDB 사용.

```python
store = VectorStore("products", persist_directory="./chroma_data")
store.add_item(id, embedding, metadata)      # 저장
store.search(query_embedding, n_results=5)   # 검색
store.exists(id)                             # 존재 확인
```

### llm_service.py
LLM을 사용한 자연어 답변 생성. Gemini 2.5 Flash 사용.

```python
service = LLMService(api_key)
response = service.generate_recommendation(query, context_items)
```

### rag_pipeline.py
위 3개 서비스를 연결하는 파이프라인.

```python
pipeline = RAGPipeline(embedding_service, vector_store, llm_service)
result = pipeline.query("가벼운 노트북 추천해줘")
```

### recommendation_service.py
사용하기 쉽게 포장한 고수준 API.

```python
service = RecommendationService(api_key, "products", "./chroma_data")
result = service.recommend("가벼운 노트북 추천해줘")
```

### init_data.py
샘플 상품 데이터 정의 및 벡터DB 초기화.

```python
initializer = DataInitializer(api_key, "products", "./chroma_data")
result = initializer.initialize()
# {"total": 7, "added": 7, "skipped": 0}
```

---

## 용어 정리

| 용어 | 설명 |
|------|------|
| **RAG** | Retrieval-Augmented Generation. 검색 + 생성 기법 |
| **Embedding** | 텍스트를 숫자 벡터로 변환한 것 |
| **Vector DB** | 벡터 저장 및 유사도 검색 전용 데이터베이스 |
| **LLM** | Large Language Model. 대규모 언어 모델 (Gemini, GPT 등) |
| **Semantic Search** | 단어가 아닌 "의미"로 검색하는 방식 |
| **Cosine Similarity** | 두 벡터의 유사도 측정 방법. 1에 가까울수록 비슷 |
| **Context** | LLM에게 제공하는 참고 정보 |
| **Upsert** | Update + Insert. 있으면 업데이트, 없으면 추가 |

---

## 테스트 실행

```bash
py -m pytest tests/ -v
```

---

## 라이선스

MIT License
