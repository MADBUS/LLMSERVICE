"""벡터DB 서비스 테스트 - TDD Red Phase"""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestVectorStore:
    """벡터DB 서비스 테스트"""

    def test_vector_store_can_be_instantiated(self):
        """VectorStore 클래스를 인스턴스화할 수 있어야 함"""
        from src.vector_store import VectorStore

        store = VectorStore(collection_name="test_collection")
        assert store is not None

    def test_vector_store_has_add_item_method(self):
        """VectorStore에 add_item 메서드가 있어야 함"""
        from src.vector_store import VectorStore

        store = VectorStore(collection_name="test_collection")
        assert hasattr(store, "add_item")
        assert callable(store.add_item)

    def test_vector_store_has_search_method(self):
        """VectorStore에 search 메서드가 있어야 함"""
        from src.vector_store import VectorStore

        store = VectorStore(collection_name="test_collection")
        assert hasattr(store, "search")
        assert callable(store.search)

    def test_add_item_stores_data(self):
        """add_item은 데이터를 저장해야 함"""
        from src.vector_store import VectorStore

        # 메모리 모드 사용 (persist_directory 없음)
        store = VectorStore(collection_name="test_add_item")

        item_id = "item_1"
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        metadata = {"name": "치킨", "category": "음식"}

        store.add_item(item_id, embedding, metadata)

        # 저장 후 검색해서 확인
        results = store.search(embedding, n_results=1)
        assert len(results) > 0

    def test_search_returns_similar_items(self):
        """search는 유사한 아이템을 반환해야 함"""
        from src.vector_store import VectorStore

        store = VectorStore(collection_name="test_search_similar")

        # 아이템 추가
        store.add_item("chicken", [0.9, 0.1, 0.1], {"name": "치킨"})
        store.add_item("beer", [0.8, 0.2, 0.1], {"name": "맥주"})
        store.add_item("shampoo", [0.1, 0.1, 0.9], {"name": "샴푸"})

        # 치킨과 비슷한 벡터로 검색
        query_embedding = [0.85, 0.15, 0.1]
        results = store.search(query_embedding, n_results=2)

        assert len(results) == 2
        # 치킨이 가장 유사해야 함
        assert results[0]["id"] == "chicken"

    def test_search_returns_metadata(self):
        """search 결과에 메타데이터가 포함되어야 함"""
        from src.vector_store import VectorStore

        store = VectorStore(collection_name="test_search_metadata")

        store.add_item(
            "item_1",
            [0.5, 0.5, 0.5],
            {"name": "테스트 상품", "price": 10000}
        )

        results = store.search([0.5, 0.5, 0.5], n_results=1)

        assert "metadata" in results[0]
        assert results[0]["metadata"]["name"] == "테스트 상품"

    def test_add_items_batch(self):
        """add_items는 여러 아이템을 한번에 저장해야 함"""
        from src.vector_store import VectorStore

        store = VectorStore(collection_name="test_add_items_batch")

        items = [
            {"id": "item_1", "embedding": [0.1, 0.2, 0.3], "metadata": {"name": "상품1"}},
            {"id": "item_2", "embedding": [0.4, 0.5, 0.6], "metadata": {"name": "상품2"}},
            {"id": "item_3", "embedding": [0.7, 0.8, 0.9], "metadata": {"name": "상품3"}},
        ]

        store.add_items(items)

        results = store.search([0.1, 0.2, 0.3], n_results=3)
        assert len(results) == 3

    def test_get_collection_count(self):
        """get_collection_count는 아이템 수를 반환해야 함"""
        from src.vector_store import VectorStore

        store = VectorStore(collection_name="test_count")

        assert store.get_collection_count() == 0

        store.add_item("item_1", [0.1, 0.2, 0.3], {"name": "상품1"})
        store.add_item("item_2", [0.4, 0.5, 0.6], {"name": "상품2"})

        assert store.get_collection_count() == 2
