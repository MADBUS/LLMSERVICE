"""임베딩 서비스 테스트 - TDD Red Phase"""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestEmbeddingService:
    """임베딩 서비스 테스트"""

    def test_embedding_service_can_be_instantiated(self):
        """EmbeddingService 클래스를 인스턴스화할 수 있어야 함"""
        with patch("src.embedding_service.genai"):
            from src.embedding_service import EmbeddingService
            service = EmbeddingService(api_key="test_api_key")
            assert service is not None

    def test_embedding_service_has_embed_text_method(self):
        """EmbeddingService에 embed_text 메서드가 있어야 함"""
        with patch("src.embedding_service.genai"):
            from src.embedding_service import EmbeddingService
            service = EmbeddingService(api_key="test_api_key")
            assert hasattr(service, "embed_text")
            assert callable(service.embed_text)

    def test_embed_text_returns_list_of_floats(self):
        """embed_text는 float 리스트를 반환해야 함"""
        with patch("src.embedding_service.genai") as mock_genai:
            # Mock the new API structure
            mock_embedding = MagicMock()
            mock_embedding.values = [0.1, 0.2, 0.3, 0.4, 0.5]
            mock_result = MagicMock()
            mock_result.embeddings = [mock_embedding]
            mock_genai.Client.return_value.models.embed_content.return_value = mock_result

            from src.embedding_service import EmbeddingService
            service = EmbeddingService(api_key="test_api_key")
            result = service.embed_text("테스트 텍스트")

            assert isinstance(result, list)
            assert len(result) > 0
            assert all(isinstance(x, float) for x in result)

    def test_embed_text_calls_gemini_api(self):
        """embed_text는 Gemini API를 호출해야 함"""
        with patch("src.embedding_service.genai") as mock_genai:
            mock_embedding = MagicMock()
            mock_embedding.values = [0.1, 0.2, 0.3]
            mock_result = MagicMock()
            mock_result.embeddings = [mock_embedding]
            mock_client = MagicMock()
            mock_client.models.embed_content.return_value = mock_result
            mock_genai.Client.return_value = mock_client

            from src.embedding_service import EmbeddingService
            service = EmbeddingService(api_key="test_api_key")
            service.embed_text("치킨")

            mock_client.models.embed_content.assert_called_once()

    def test_embed_texts_batch_returns_list_of_embeddings(self):
        """embed_texts는 여러 텍스트의 임베딩 리스트를 반환해야 함"""
        with patch("src.embedding_service.genai") as mock_genai:
            mock_embedding = MagicMock()
            mock_embedding.values = [0.1, 0.2, 0.3]
            mock_result = MagicMock()
            mock_result.embeddings = [mock_embedding]
            mock_genai.Client.return_value.models.embed_content.return_value = mock_result

            from src.embedding_service import EmbeddingService
            service = EmbeddingService(api_key="test_api_key")
            texts = ["치킨", "맥주", "피자"]
            results = service.embed_texts(texts)

            assert isinstance(results, list)
            assert len(results) == 3
            assert all(isinstance(emb, list) for emb in results)
