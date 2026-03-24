"""데이터 초기화 스크립트 - 샘플 상품 데이터를 벡터DB에 저장"""
from typing import List, Dict, Any

from src.embedding_service import EmbeddingService
from src.vector_store import VectorStore


# 샘플 상품 데이터
SAMPLE_PRODUCTS: List[Dict[str, Any]] = [
    {
        "id": "prod_001",
        "name": "LG 그램 16",
        "description": "초경량 16인치 노트북, 무게 1.19kg, 긴 배터리 수명",
        "category": "노트북",
        "price": 1890000
    },
    {
        "id": "prod_002",
        "name": "삼성 갤럭시북3 프로",
        "description": "AMOLED 디스플레이, 슬림 디자인, 고성능 프로세서",
        "category": "노트북",
        "price": 1690000
    },
    {
        "id": "prod_003",
        "name": "애플 맥북 에어 M3",
        "description": "M3 칩셋, 팬리스 디자인, 18시간 배터리, macOS",
        "category": "노트북",
        "price": 1590000
    },
    {
        "id": "prod_004",
        "name": "소니 WH-1000XM5",
        "description": "프리미엄 노이즈캔슬링 헤드폰, 30시간 배터리",
        "category": "헤드폰",
        "price": 450000
    },
    {
        "id": "prod_005",
        "name": "에어팟 프로 2",
        "description": "애플 무선 이어폰, 액티브 노이즈캔슬링, 공간음향",
        "category": "이어폰",
        "price": 359000
    },
    {
        "id": "prod_006",
        "name": "삼성 갤럭시 버즈2 프로",
        "description": "하이레졸루션 오디오, 노이즈캔슬링, IPX7 방수",
        "category": "이어폰",
        "price": 229000
    },
    {
        "id": "prod_007",
        "name": "로지텍 MX Master 3S",
        "description": "무선 마우스, 인체공학 디자인, 조용한 클릭",
        "category": "마우스",
        "price": 149000
    },
]


class DataInitializer:
    """벡터DB에 샘플 데이터를 초기화하는 클래스"""

    def __init__(self, api_key: str, collection_name: str, persist_directory: str = None):
        """
        DataInitializer 초기화

        Args:
            api_key: Gemini API 키
            collection_name: 벡터DB 컬렉션 이름
            persist_directory: 데이터 영구 저장 경로
        """
        self.api_key = api_key
        self.embedding_service = EmbeddingService(api_key=api_key)
        self.vector_store = VectorStore(
            collection_name=collection_name,
            persist_directory=persist_directory
        )

    def initialize(self, products: List[Dict[str, Any]] = None) -> dict:
        """
        상품 데이터를 벡터DB에 저장 (있으면 스킵, 없으면 추가)

        Args:
            products: 저장할 상품 리스트 (기본값: SAMPLE_PRODUCTS)

        Returns:
            {"total": 전체 수, "added": 새로 추가된 수, "skipped": 스킵된 수}
        """
        if products is None:
            products = SAMPLE_PRODUCTS

        added = 0
        skipped = 0

        for product in products:
            # 이미 존재하는지 확인
            if self.vector_store.exists(product["id"]):
                skipped += 1
                continue

            # 상품 설명을 임베딩으로 변환 (새 상품만)
            text_to_embed = f"{product['name']} - {product['description']}"
            embedding = self.embedding_service.embed_text(text_to_embed)

            # 벡터DB에 저장
            self.vector_store.add_item(
                item_id=product["id"],
                embedding=embedding,
                metadata={
                    "name": product["name"],
                    "description": product["description"],
                    "category": product["category"],
                    "price": product["price"]
                }
            )
            added += 1

        return {"total": len(products), "added": added, "skipped": skipped}
