"""옷 관리 서비스 - MySQL과 벡터DB 동기화"""
from typing import List, Optional

from src.models.clothing import Clothing, ClothingCategory, Color, Season, Style
from src.database.clothing_repository import ClothingRepository
from src.database.mysql_connection import MySQLConnection
from src.embedding_service import EmbeddingService
from src.vector_store import VectorStore


class ClothingService:
    """옷 관리 서비스 (MySQL + 벡터DB 동기화)"""

    def __init__(
        self,
        api_key: str,
        collection_name: str = "clothes",
        persist_directory: str = "./chroma_clothes"
    ):
        """
        ClothingService 초기화

        Args:
            api_key: Gemini API 키 (임베딩용)
            collection_name: 벡터DB 컬렉션 이름
            persist_directory: 벡터DB 저장 경로
        """
        self.repository = ClothingRepository()
        self.embedding_service = EmbeddingService(api_key=api_key)
        self.vector_store = VectorStore(
            collection_name=collection_name,
            persist_directory=persist_directory
        )

    def add_clothing(self, clothing: Clothing) -> int:
        """
        옷 추가 (MySQL + 벡터DB)

        Args:
            clothing: 추가할 옷 정보

        Returns:
            생성된 옷 ID
        """
        # 1. MySQL에 저장
        new_id = self.repository.add(clothing)
        clothing.id = new_id

        # 2. 벡터DB에 저장
        text = clothing.to_text()
        embedding = self.embedding_service.embed_text(text)
        self.vector_store.add_item(
            item_id=f"cloth_{new_id}",
            embedding=embedding,
            metadata=clothing.to_dict()
        )

        return new_id

    def get_all_clothes(self) -> List[Clothing]:
        """모든 옷 조회"""
        return self.repository.get_all()

    def get_by_id(self, clothing_id: int) -> Optional[Clothing]:
        """ID로 옷 조회"""
        return self.repository.get_by_id(clothing_id)

    def get_by_season(self, season: Season) -> List[Clothing]:
        """계절별 옷 조회"""
        return self.repository.get_by_season(season)

    def get_by_category(self, category: ClothingCategory) -> List[Clothing]:
        """카테고리별 옷 조회"""
        return self.repository.get_by_category(category)

    def delete_clothing(self, clothing_id: int) -> bool:
        """
        옷 삭제 (MySQL + 벡터DB)

        Args:
            clothing_id: 삭제할 옷 ID

        Returns:
            삭제 성공 여부
        """
        # MySQL에서 삭제
        result = self.repository.delete(clothing_id)

        # 벡터DB에서도 삭제
        if result:
            try:
                self.vector_store.delete_item(f"cloth_{clothing_id}")
            except Exception:
                pass  # 벡터DB에 없을 수도 있음

        return result

    def sync_to_vector_db(self) -> dict:
        """
        MySQL 데이터를 벡터DB에 동기화

        Returns:
            {"total": 전체 수, "synced": 동기화된 수}
        """
        clothes = self.repository.get_all()
        synced = 0

        for clothing in clothes:
            item_id = f"cloth_{clothing.id}"

            # 이미 있으면 스킵
            if self.vector_store.exists(item_id):
                continue

            text = clothing.to_text()
            embedding = self.embedding_service.embed_text(text)
            self.vector_store.add_item(
                item_id=item_id,
                embedding=embedding,
                metadata=clothing.to_dict()
            )
            synced += 1

        return {"total": len(clothes), "synced": synced}

    def count(self) -> int:
        """총 옷 개수"""
        return self.repository.count()

    @staticmethod
    def init_database():
        """데이터베이스 초기화"""
        MySQLConnection.init_database()
