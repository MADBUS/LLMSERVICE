"""임베딩 서비스 - Gemini API를 사용한 텍스트 임베딩"""
from google import genai
from typing import List


class EmbeddingService:
    """Gemini API를 사용하여 텍스트를 임베딩 벡터로 변환하는 서비스"""

    def __init__(self, api_key: str, model: str = "gemini-embedding-001"):
        """
        EmbeddingService 초기화

        Args:
            api_key: Gemini API 키
            model: 사용할 임베딩 모델 (기본값: text-embedding-004)
        """
        self.api_key = api_key
        self.model = model
        self.client = genai.Client(api_key=api_key)

    def embed_text(self, text: str) -> List[float]:
        """
        단일 텍스트를 임베딩 벡터로 변환

        Args:
            text: 임베딩할 텍스트

        Returns:
            임베딩 벡터 (float 리스트)
        """
        result = self.client.models.embed_content(
            model=self.model,
            contents=text
        )
        return list(result.embeddings[0].values)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        여러 텍스트를 임베딩 벡터로 변환

        Args:
            texts: 임베딩할 텍스트 리스트

        Returns:
            임베딩 벡터 리스트
        """
        embeddings = []
        for text in texts:
            embedding = self.embed_text(text)
            embeddings.append(embedding)
        return embeddings
