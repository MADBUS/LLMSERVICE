"""추천 서비스 - RAG 파이프라인을 쉽게 사용하는 고수준 API"""
from src.embedding_service import EmbeddingService
from src.vector_store import VectorStore
from src.llm_service import LLMService
from src.rag_pipeline import RAGPipeline


class RecommendationService:
    """
    추천 서비스 클래스

    사용법:
        service = RecommendationService(api_key="...", collection_name="products")
        result = service.recommend("노트북 추천해줘")
    """

    def __init__(self, api_key: str, collection_name: str):
        """
        RecommendationService 초기화

        Args:
            api_key: Gemini API 키
            collection_name: 벡터DB 컬렉션 이름
        """
        # 3개 컴포넌트 자동 생성
        self.embedding_service = EmbeddingService(api_key=api_key)
        self.vector_store = VectorStore(collection_name=collection_name)
        self.llm_service = LLMService(api_key=api_key)

        # RAG 파이프라인 연결
        self.pipeline = RAGPipeline(
            embedding_service=self.embedding_service,
            vector_store=self.vector_store,
            llm_service=self.llm_service
        )

    def recommend(self, query: str) -> str:
        """
        사용자 질의에 대한 추천 생성

        Args:
            query: 사용자 질의 (예: "가벼운 노트북 추천해줘")

        Returns:
            LLM이 생성한 추천 답변
        """
        return self.pipeline.query(query)
