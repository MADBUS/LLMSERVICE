"""날씨 기반 코디 추천 서비스"""
from typing import List, Dict, Any, Optional

from src.models.clothing import Clothing, ClothingCategory, Season
from src.clothing_service import ClothingService
from src.weather_service import WeatherService, WeatherInfo
from src.embedding_service import EmbeddingService
from src.vector_store import VectorStore
from src.llm_service import LLMService


OUTFIT_SYSTEM_PROMPT = """당신은 전문 패션 코디네이터 AI 비서입니다.
사용자의 옷장에 있는 옷들을 기반으로, 날씨와 상황(TPO)에 맞는 최적의 코디를 추천합니다.

## 추천 원칙
1. **날씨 고려**: 기온에 맞는 보온성, 비/눈 시 방수 아이템
2. **TPO 고려**: 데이트/출근/운동/면접 등 상황에 맞는 스타일
3. **색상 조화**: 어울리는 색상 조합 (유사색/보색 매칭)
4. **스타일 통일**: 캐주얼/포멀/스포티 등 일관된 무드

## 답변 형식
1. 오늘의 코디 추천 (상의 + 하의 + 아우터(필요시) + 신발)
2. 각 아이템을 선택한 이유
3. 전체 코디의 포인트 설명

친근하고 자연스러운 톤으로 답변해주세요. 반드시 옷장에 있는 옷 이름을 정확히 사용하세요."""


class OutfitRecommendationService:
    """날씨 기반 코디 추천 서비스"""

    def __init__(
        self,
        gemini_api_key: str,
        collection_name: str = "clothes",
        persist_directory: str = "./chroma_clothes"
    ):
        """
        OutfitRecommendationService 초기화

        Args:
            gemini_api_key: Gemini API 키
            collection_name: 벡터DB 컬렉션 이름
            persist_directory: 벡터DB 저장 경로
        """
        self.clothing_service = ClothingService(
            api_key=gemini_api_key,
            collection_name=collection_name,
            persist_directory=persist_directory
        )
        self.weather_service = WeatherService()  # 기상청 API (환경변수에서 키 로드)
        self.embedding_service = EmbeddingService(api_key=gemini_api_key)
        self.vector_store = VectorStore(
            collection_name=collection_name,
            persist_directory=persist_directory
        )
        self.llm_service = LLMService(
            api_key=gemini_api_key,
            system_prompt=OUTFIT_SYSTEM_PROMPT
        )

    def get_weather(self, city: str = "서울") -> Optional[WeatherInfo]:
        """날씨 정보 조회"""
        return self.weather_service.get_weather(city)

    def recommend_outfit(
        self,
        query: str,
        city: str = "서울",
        n_results: int = 10
    ) -> str:
        """
        날씨 기반 코디 추천

        Args:
            query: 사용자 질의 (예: "오늘 뭐 입을까?", "데이트 갈 건데 추천해줘")
            city: 도시명 (기본값: Seoul)
            n_results: 검색할 옷 개수

        Returns:
            코디 추천 답변
        """
        # 1. 날씨 정보 조회
        weather = self.weather_service.get_weather(city)
        weather_desc = weather.to_description() if weather else "날씨 정보를 가져올 수 없습니다."

        # 날씨 기반 검색어 생성
        if weather:
            season = weather.get_season_recommendation()
            warmth_min, warmth_max = weather.get_warmth_recommendation()
            weather_query = f"{season} 날씨 {weather.temperature}도 {'비' if weather.rain else ''} {'눈' if weather.snow else ''}"
        else:
            weather_query = ""

        # 2. 사용자 질의 + 날씨 정보로 검색어 구성
        search_query = f"{query} {weather_query}".strip()
        query_embedding = self.embedding_service.embed_text(search_query)

        # 3. 벡터DB에서 관련 옷 검색
        search_results = self.vector_store.search(query_embedding, n_results=n_results)

        if not search_results:
            return "옷장에 등록된 옷이 없습니다. 먼저 옷을 등록해주세요."

        # 4. 카테고리별로 옷 분류
        clothes_by_category = self._categorize_clothes(search_results)

        # 5. LLM으로 코디 추천 생성
        prompt = self._build_recommendation_prompt(
            query=query,
            weather_desc=weather_desc,
            clothes_by_category=clothes_by_category,
            weather=weather
        )

        return self.llm_service.generate(prompt)

    def recommend_by_occasion(
        self,
        occasion: str,
        city: str = "서울"
    ) -> str:
        """
        상황별 코디 추천

        Args:
            occasion: 상황 (예: "출근", "데이트", "운동", "면접")
            city: 도시명

        Returns:
            코디 추천 답변
        """
        return self.recommend_outfit(f"{occasion}에 어울리는 코디 추천해줘", city)

    def get_color_match_advice(self, color: str) -> str:
        """
        색상 매칭 조언

        Args:
            color: 기준 색상

        Returns:
            색상 조합 조언
        """
        query = f"{color}색 옷과 어울리는 색상 조합"
        query_embedding = self.embedding_service.embed_text(query)
        search_results = self.vector_store.search(query_embedding, n_results=10)

        clothes_list = [r["metadata"] for r in search_results]

        prompt = f"""사용자가 {color}색 옷과 어울리는 조합을 찾고 있습니다.

옷장에 있는 옷들:
{self._format_clothes_list(clothes_list)}

{color}색과 잘 어울리는 옷들을 조합해서 추천해주세요.
색상 조화의 이유도 설명해주세요."""

        return self.llm_service.generate(prompt)

    def _categorize_clothes(self, search_results: List[Dict]) -> Dict[str, List[Dict]]:
        """검색 결과를 카테고리별로 분류"""
        categories = {
            "아우터": [],
            "상의": [],
            "하의": [],
            "원피스": [],
            "신발": [],
            "액세서리": []
        }

        for result in search_results:
            metadata = result.get("metadata", {})
            category = metadata.get("category", "")
            if category in categories:
                categories[category].append(metadata)

        return categories

    def _build_recommendation_prompt(
        self,
        query: str,
        weather_desc: str,
        clothes_by_category: Dict[str, List[Dict]],
        weather: Optional[WeatherInfo] = None
    ) -> str:
        """추천 프롬프트 생성"""
        prompt_parts = []

        # 날씨 정보
        prompt_parts.append("## 오늘의 날씨")
        prompt_parts.append(weather_desc)

        if weather:
            season = weather.get_season_recommendation()
            prompt_parts.append(f"추천 계절감: {season}")
            if weather.rain:
                prompt_parts.append("⚠️ 비가 오고 있습니다 - 방수 아우터 고려")
            if weather.snow:
                prompt_parts.append("⚠️ 눈이 오고 있습니다 - 미끄럽지 않은 신발 고려")

        # 사용자 요청
        prompt_parts.append(f"\n## 사용자 요청")
        prompt_parts.append(query)

        # 옷장 정보
        prompt_parts.append("\n## 사용자의 옷장")

        for category, clothes in clothes_by_category.items():
            if clothes:
                prompt_parts.append(f"\n### {category}")
                for cloth in clothes:
                    warmth = cloth.get('warmth_level', 3)
                    warmth_desc = "따뜻" if warmth >= 4 else "보통" if warmth >= 2 else "시원"
                    prompt_parts.append(
                        f"- {cloth.get('name', '이름없음')} (색상: {cloth.get('color', '')}, "
                        f"스타일: {cloth.get('style', '')}, 보온성: {warmth_desc})"
                    )

        prompt_parts.append("\n## 요청사항")
        prompt_parts.append("위 옷장의 옷들 중에서 오늘 날씨와 사용자 요청에 맞는 코디를 추천해주세요.")
        prompt_parts.append("반드시 상의 + 하의 + 신발 조합을 포함하고, 날씨에 따라 아우터도 추천해주세요.")

        return "\n".join(prompt_parts)

    def _format_clothes_list(self, clothes: List[Dict]) -> str:
        """옷 리스트를 문자열로 포맷"""
        lines = []
        for cloth in clothes:
            lines.append(
                f"- {cloth.get('name', '')} (카테고리: {cloth.get('category', '')}, "
                f"색상: {cloth.get('color', '')}, 스타일: {cloth.get('style', '')})"
            )
        return "\n".join(lines)
