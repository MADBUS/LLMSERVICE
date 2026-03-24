"""RAG 기반 추천 시스템 데모"""
import os
from dotenv import load_dotenv
from src.recommendation_service import RecommendationService
from src.init_data import DataInitializer

# .env.dev 파일에서 환경변수 로드
load_dotenv(".env.dev")


def run_demo(api_key: str = None, collection_name: str = "products"):
    """
    대화형 추천 데모 실행

    Args:
        api_key: Gemini API 키 (기본값: 환경변수 GEMINI_API_KEY)
        collection_name: 벡터DB 컬렉션 이름
    """
    # API 키 설정
    if api_key is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("오류: GEMINI_API_KEY 환경변수를 설정해주세요.")
            return

    print("=" * 50)
    print("[RAG 기반 상품 추천 시스템]")
    print("=" * 50)
    print()

    # 데이터 초기화
    print(">> 샘플 데이터를 로딩 중...")
    initializer = DataInitializer(api_key=api_key, collection_name=collection_name)
    count = initializer.initialize()
    print(f">> {count}개의 상품이 로딩되었습니다.")
    print()

    # 추천 서비스 초기화
    service = RecommendationService(api_key=api_key, collection_name=collection_name)

    print("질문을 입력하세요 (종료: quit)")
    print("-" * 50)

    while True:
        try:
            user_input = input("\n[질문] ").strip()

            if user_input.lower() in ['quit', 'exit', 'q', '종료']:
                print("\n이용해주셔서 감사합니다!")
                break

            if not user_input:
                print("질문을 입력해주세요.")
                continue

            print("\n[추천 결과]")
            print("-" * 30)
            result = service.recommend(user_input)
            print(result)

        except KeyboardInterrupt:
            print("\n\n프로그램을 종료합니다.")
            break


if __name__ == "__main__":
    run_demo()
