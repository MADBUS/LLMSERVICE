"""LLM 서비스 - Gemini API를 사용한 텍스트 생성"""
from google import genai
from typing import List, Dict, Any, Optional


DEFAULT_SYSTEM_PROMPT = """당신은 친절한 상품 추천 전문가입니다.
사용자의 질문에 맞는 상품을 추천하고, 왜 그 상품을 추천하는지 설명해주세요.
답변은 자연스럽고 친근하게 해주세요."""


class LLMService:
    """Gemini API를 사용하여 텍스트를 생성하는 서비스"""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.5-flash",
        system_prompt: Optional[str] = None
    ):
        """
        LLMService 초기화

        Args:
            api_key: Gemini API 키
            model: 사용할 LLM 모델 (기본값: gemini-2.5-flash)
            system_prompt: 시스템 프롬프트 (기본값: DEFAULT_SYSTEM_PROMPT)
        """
        self.api_key = api_key
        self.model = model
        self.system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        self.client = genai.Client(api_key=api_key)

    def generate(self, prompt: str) -> str:
        """
        프롬프트에 대한 응답 생성

        Args:
            prompt: 사용자 프롬프트

        Returns:
            생성된 텍스트
        """
        full_prompt = f"{self.system_prompt}\n\n사용자: {prompt}"

        response = self.client.models.generate_content(
            model=self.model,
            contents=full_prompt
        )

        return response.text

    def generate_recommendation(
        self,
        query: str,
        context_items: List[Dict[str, Any]]
    ) -> str:
        """
        컨텍스트 아이템을 기반으로 추천 생성

        Args:
            query: 사용자 질의
            context_items: 검색된 관련 아이템 리스트

        Returns:
            추천 답변 텍스트
        """
        # 컨텍스트 아이템을 문자열로 변환
        context_str = self._format_context(context_items)

        prompt = f"""다음은 사용자 질문과 관련된 상품 정보입니다:

{context_str}

사용자 질문: {query}

위 상품 정보를 참고하여 사용자에게 적절한 추천을 해주세요."""

        return self.generate(prompt)

    def _format_context(self, items: List[Dict[str, Any]]) -> str:
        """컨텍스트 아이템을 문자열로 포맷팅"""
        lines = []
        for i, item in enumerate(items, 1):
            item_info = ", ".join(f"{k}: {v}" for k, v in item.items())
            lines.append(f"{i}. {item_info}")
        return "\n".join(lines)
