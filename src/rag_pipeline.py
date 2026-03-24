"""RAG 파이프라인 - 질의 → 검색 → 생성 통합"""
from typing import List, Dict, Any

from src.embedding_service import EmbeddingService
from src.vector_store import VectorStore
from src.llm_service import LLMService


class RAGPipeline:
    """RAG(Retrieval-Augmented Generation) 파이프라인"""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
        llm_service: LLMService
    ):
        """
        RAGPipeline 초기화

        Args:
            embedding_service: 텍스트 임베딩 서비스
            vector_store: 벡터 저장/검색 서비스
            llm_service: LLM 텍스트 생성 서비스
        """
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.llm_service = llm_service

    def query(self, user_query: str, n_results: int = 5) -> str:
        """
        사용자 질의에 대한 추천 생성

        Args:
            user_query: 사용자 질의 문자열
            n_results: 검색할 결과 수 (기본값: 5)

        Returns:
            LLM이 생성한 추천 답변
        """
        # 1. 질의를 임베딩 벡터로 변환
        query_embedding = self.embedding_service.embed_text(user_query)

        # 2. 벡터 DB에서 유사한 아이템 검색
        search_results = self.vector_store.search(query_embedding, n_results=n_results)

        # 3. 검색 결과의 메타데이터 추출
        context_items = [result["metadata"] for result in search_results]

        # 4. LLM으로 추천 답변 생성
        response = self.llm_service.generate_recommendation(user_query, context_items)

        return response
