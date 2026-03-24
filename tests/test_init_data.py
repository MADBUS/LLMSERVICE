"""데이터 초기화 스크립트 테스트"""
import pytest
import os
from unittest.mock import patch, MagicMock


class TestSampleData:
    """샘플 상품 데이터 테스트"""

    def test_sample_products_defined(self):
        """샘플 상품 데이터가 정의되어 있는지 테스트"""
        from src.init_data import SAMPLE_PRODUCTS

        # 샘플 데이터가 리스트로 정의됨
        assert isinstance(SAMPLE_PRODUCTS, list)
        # 최소 5개 이상의 상품이 있음
        assert len(SAMPLE_PRODUCTS) >= 5

    def test_sample_product_has_required_fields(self):
        """각 상품에 필수 필드가 있는지 테스트"""
        from src.init_data import SAMPLE_PRODUCTS

        for product in SAMPLE_PRODUCTS:
            # 필수 필드 확인
            assert "id" in product
            assert "name" in product
            assert "description" in product
            assert "category" in product
            assert "price" in product


class TestDataInitializer:
    """데이터 초기화 클래스 테스트"""

    @patch('src.init_data.EmbeddingService')
    @patch('src.init_data.VectorStore')
    def test_initializer_loads_data_to_vectordb(
        self, mock_vector_cls, mock_embedding_cls
    ):
        """초기화 시 데이터가 벡터DB에 저장되는지 테스트"""
        from src.init_data import DataInitializer, SAMPLE_PRODUCTS

        # Mock 설정
        mock_embedding = MagicMock()
        mock_vector = MagicMock()
        mock_embedding_cls.return_value = mock_embedding
        mock_vector_cls.return_value = mock_vector

        # 임베딩 반환값 설정
        mock_embedding.embed_text.return_value = [0.1, 0.2, 0.3]
        # 기존 데이터 없음
        mock_vector.exists.return_value = False

        # When: 데이터 초기화 실행
        initializer = DataInitializer(
            api_key="test-key",
            collection_name="products"
        )
        result = initializer.initialize()

        # Then: 각 상품이 벡터DB에 저장됨
        assert mock_vector.add_item.call_count == len(SAMPLE_PRODUCTS)
        assert result["added"] == len(SAMPLE_PRODUCTS)
        assert result["skipped"] == 0
