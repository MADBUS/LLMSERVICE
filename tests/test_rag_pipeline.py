"""RAG 파이프라인 테스트"""
import pytest
from unittest.mock import Mock, patch
from src.rag_pipeline import RAGPipeline


class TestRAGPipeline:
    """RAG 파이프라인 통합 테스트"""

    def test_query_search_generate_integration(self):
        """질의 → 검색 → 생성 통합 테스트"""
        # Given: Mock 서비스들
        mock_embedding_service = Mock()
        mock_vector_store = Mock()
        mock_llm_service = Mock()

        # 임베딩 서비스가 쿼리를 벡터로 변환
        mock_embedding_service.embed_text.return_value = [0.1, 0.2, 0.3]

        # 벡터 스토어가 유사한 아이템 반환
        mock_vector_store.search.return_value = [
            {"id": "1", "metadata": {"name": "상품A", "description": "좋은 상품"}, "distance": 0.1},
            {"id": "2", "metadata": {"name": "상품B", "description": "훌륭한 상품"}, "distance": 0.2},
        ]

        # LLM 서비스가 추천 생성
        mock_llm_service.generate_recommendation.return_value = "상품A를 추천합니다."

        # When: RAG 파이프라인 실행
        pipeline = RAGPipeline(
            embedding_service=mock_embedding_service,
            vector_store=mock_vector_store,
            llm_service=mock_llm_service
        )
        result = pipeline.query("좋은 상품 추천해주세요")

        # Then: 각 서비스가 올바르게 호출됨
        mock_embedding_service.embed_text.assert_called_once_with("좋은 상품 추천해주세요")
        mock_vector_store.search.assert_called_once_with([0.1, 0.2, 0.3], n_results=5)
        mock_llm_service.generate_recommendation.assert_called_once()

        # 결과가 문자열로 반환됨
        assert isinstance(result, str)
        assert result == "상품A를 추천합니다."
