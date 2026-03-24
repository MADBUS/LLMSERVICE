"""추천 서비스 테스트"""
import pytest
from unittest.mock import patch, MagicMock
from src.recommendation_service import RecommendationService


class TestRecommendationService:
    """추천 서비스 클래스 테스트"""

    @patch('src.recommendation_service.EmbeddingService')
    @patch('src.recommendation_service.VectorStore')
    @patch('src.recommendation_service.LLMService')
    def test_service_creates_all_components(
        self, mock_llm_cls, mock_vector_cls, mock_embedding_cls
    ):
        """서비스 생성 시 3개 컴포넌트가 자동으로 만들어지는지 테스트"""
        # Given
        api_key = "test-api-key"
        collection_name = "products"

        # When: RecommendationService 생성
        service = RecommendationService(
            api_key=api_key,
            collection_name=collection_name
        )

        # Then: 3개 서비스가 자동 생성됨
        mock_embedding_cls.assert_called_once_with(api_key=api_key)
        mock_vector_cls.assert_called_once_with(collection_name=collection_name)
        mock_llm_cls.assert_called_once_with(api_key=api_key)

    @patch('src.recommendation_service.EmbeddingService')
    @patch('src.recommendation_service.VectorStore')
    @patch('src.recommendation_service.LLMService')
    def test_recommend_returns_answer(
        self, mock_llm_cls, mock_vector_cls, mock_embedding_cls
    ):
        """recommend() 호출 시 추천 답변을 반환하는지 테스트"""
        # Given: Mock 설정
        mock_embedding = MagicMock()
        mock_vector = MagicMock()
        mock_llm = MagicMock()

        mock_embedding_cls.return_value = mock_embedding
        mock_vector_cls.return_value = mock_vector
        mock_llm_cls.return_value = mock_llm

        # 각 컴포넌트의 동작 설정
        mock_embedding.embed_text.return_value = [0.1, 0.2]
        mock_vector.search.return_value = [
            {"id": "1", "metadata": {"name": "노트북"}, "distance": 0.1}
        ]
        mock_llm.generate_recommendation.return_value = "노트북을 추천합니다."

        service = RecommendationService(
            api_key="test-key",
            collection_name="products"
        )

        # When: 추천 요청
        result = service.recommend("좋은 상품 추천해줘")

        # Then: 추천 답변 반환
        assert result == "노트북을 추천합니다."
