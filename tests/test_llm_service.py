"""LLM 서비스 테스트 - TDD Red Phase"""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestLLMService:
    """LLM 서비스 테스트"""

    def test_llm_service_can_be_instantiated(self):
        """LLMService 클래스를 인스턴스화할 수 있어야 함"""
        with patch("src.llm_service.genai"):
            from src.llm_service import LLMService
            service = LLMService(api_key="test_api_key")
            assert service is not None

    def test_llm_service_has_generate_method(self):
        """LLMService에 generate 메서드가 있어야 함"""
        with patch("src.llm_service.genai"):
            from src.llm_service import LLMService
            service = LLMService(api_key="test_api_key")
            assert hasattr(service, "generate")
            assert callable(service.generate)

    def test_generate_returns_string(self):
        """generate는 문자열을 반환해야 함"""
        with patch("src.llm_service.genai") as mock_genai:
            mock_response = MagicMock()
            mock_response.text = "치킨을 추천합니다!"
            mock_genai.Client.return_value.models.generate_content.return_value = mock_response

            from src.llm_service import LLMService
            service = LLMService(api_key="test_api_key")
            result = service.generate("야식 추천해줘")

            assert isinstance(result, str)
            assert len(result) > 0

    def test_generate_calls_gemini_api(self):
        """generate는 Gemini API를 호출해야 함"""
        with patch("src.llm_service.genai") as mock_genai:
            mock_response = MagicMock()
            mock_response.text = "추천 결과"
            mock_client = MagicMock()
            mock_client.models.generate_content.return_value = mock_response
            mock_genai.Client.return_value = mock_client

            from src.llm_service import LLMService
            service = LLMService(api_key="test_api_key")
            service.generate("테스트 프롬프트")

            mock_client.models.generate_content.assert_called_once()

    def test_generate_recommendation_with_context(self):
        """generate_recommendation은 컨텍스트를 포함하여 추천을 생성해야 함"""
        with patch("src.llm_service.genai") as mock_genai:
            mock_response = MagicMock()
            mock_response.text = "치킨과 맥주를 추천합니다. 야식으로 좋습니다."
            mock_genai.Client.return_value.models.generate_content.return_value = mock_response

            from src.llm_service import LLMService
            service = LLMService(api_key="test_api_key")

            query = "야식 추천해줘"
            context_items = [
                {"name": "치킨", "category": "음식"},
                {"name": "맥주", "category": "음료"},
            ]

            result = service.generate_recommendation(query, context_items)

            assert isinstance(result, str)
            assert len(result) > 0

    def test_llm_service_has_default_system_prompt(self):
        """LLMService는 기본 시스템 프롬프트를 가져야 함"""
        with patch("src.llm_service.genai"):
            from src.llm_service import LLMService
            service = LLMService(api_key="test_api_key")
            assert hasattr(service, "system_prompt")
            assert len(service.system_prompt) > 0

    def test_llm_service_can_set_custom_system_prompt(self):
        """LLMService는 커스텀 시스템 프롬프트를 설정할 수 있어야 함"""
        with patch("src.llm_service.genai"):
            from src.llm_service import LLMService
            custom_prompt = "당신은 음식 추천 전문가입니다."
            service = LLMService(api_key="test_api_key", system_prompt=custom_prompt)
            assert service.system_prompt == custom_prompt
