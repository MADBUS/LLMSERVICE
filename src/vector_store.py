"""벡터DB 서비스 - ChromaDB를 사용한 벡터 저장 및 검색"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional


class VectorStore:
    """ChromaDB를 사용하여 벡터를 저장하고 검색하는 서비스"""

    def __init__(
        self,
        collection_name: str,
        persist_directory: Optional[str] = None
    ):
        """
        VectorStore 초기화

        Args:
            collection_name: 컬렉션 이름
            persist_directory: 데이터 저장 경로 (None이면 메모리에만 저장)
        """
        self.collection_name = collection_name

        if persist_directory:
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            self.client = chromadb.Client()

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_item(
        self,
        item_id: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> None:
        """
        단일 아이템 저장

        Args:
            item_id: 아이템 고유 ID
            embedding: 임베딩 벡터
            metadata: 아이템 메타데이터
        """
        self.collection.add(
            ids=[item_id],
            embeddings=[embedding],
            metadatas=[metadata]
        )

    def add_items(self, items: List[Dict[str, Any]]) -> None:
        """
        여러 아이템을 한번에 저장

        Args:
            items: 아이템 리스트 (각 아이템은 id, embedding, metadata 포함)
        """
        ids = [item["id"] for item in items]
        embeddings = [item["embedding"] for item in items]
        metadatas = [item["metadata"] for item in items]

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def search(
        self,
        query_embedding: List[float],
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        유사한 아이템 검색

        Args:
            query_embedding: 검색 쿼리 임베딩 벡터
            n_results: 반환할 결과 수

        Returns:
            유사한 아이템 리스트 (id, metadata, distance 포함)
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        items = []
        for i in range(len(results["ids"][0])):
            item = {
                "id": results["ids"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if results["distances"] else None
            }
            items.append(item)

        return items

    def get_collection_count(self) -> int:
        """컬렉션의 아이템 수 반환"""
        return self.collection.count()

    def exists(self, item_id: str) -> bool:
        """아이템이 존재하는지 확인"""
        result = self.collection.get(ids=[item_id])
        return len(result["ids"]) > 0

    def upsert_item(
        self,
        item_id: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> bool:
        """
        아이템 추가 또는 업데이트 (있으면 스킵, 없으면 추가)

        Args:
            item_id: 아이템 고유 ID
            embedding: 임베딩 벡터
            metadata: 아이템 메타데이터

        Returns:
            True: 새로 추가됨, False: 이미 존재하여 스킵
        """
        if self.exists(item_id):
            return False  # 이미 있으면 스킵

        self.collection.add(
            ids=[item_id],
            embeddings=[embedding],
            metadatas=[metadata]
        )
        return True

    def delete_item(self, item_id: str) -> bool:
        """
        아이템 삭제

        Args:
            item_id: 삭제할 아이템 ID

        Returns:
            삭제 성공 여부
        """
        try:
            self.collection.delete(ids=[item_id])
            return True
        except Exception:
            return False

    def delete_collection(self) -> None:
        """컬렉션 삭제"""
        self.client.delete_collection(self.collection_name)
