"""기상청 API 연동 서비스"""
import os
import requests
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta


@dataclass
class WeatherInfo:
    """날씨 정보"""
    temperature: float          # 현재 기온 (섭씨)
    feels_like: float           # 체감 온도
    humidity: int               # 습도 (%)
    description: str            # 날씨 설명 (맑음, 흐림 등)
    wind_speed: float           # 풍속 (m/s)
    city: str                   # 지역명
    rain: bool                  # 비 여부
    snow: bool                  # 눈 여부

    def get_season_recommendation(self) -> str:
        """기온에 따른 계절 추천"""
        if self.temperature >= 28:
            return "여름"
        elif self.temperature >= 20:
            return "봄"
        elif self.temperature >= 10:
            return "가을"
        else:
            return "겨울"

    def get_warmth_recommendation(self) -> tuple[int, int]:
        """기온에 따른 보온성 범위 추천 (min, max)"""
        if self.temperature >= 28:
            return (1, 2)  # 시원한 옷
        elif self.temperature >= 23:
            return (1, 3)  # 시원~보통
        elif self.temperature >= 17:
            return (2, 3)  # 보통
        elif self.temperature >= 10:
            return (3, 4)  # 보통~따뜻
        elif self.temperature >= 5:
            return (4, 5)  # 따뜻한 옷
        else:
            return (5, 5)  # 매우 따뜻한 옷

    def to_description(self) -> str:
        """날씨 설명 문자열 생성"""
        desc = f"{self.city} 현재 날씨: {self.description}, "
        desc += f"기온 {self.temperature}°C (체감 {self.feels_like}°C), "
        desc += f"습도 {self.humidity}%, 풍속 {self.wind_speed}m/s"

        if self.rain:
            desc += ", 비가 오고 있습니다"
        if self.snow:
            desc += ", 눈이 오고 있습니다"

        return desc


# 주요 도시 격자 좌표 (기상청 격자 X, Y)
CITY_COORDS = {
    "서울": (60, 127),
    "부산": (98, 76),
    "인천": (55, 124),
    "대구": (89, 90),
    "대전": (67, 100),
    "광주": (58, 74),
    "수원": (60, 121),
    "울산": (102, 84),
    "세종": (66, 103),
    "제주": (52, 38),
}


class WeatherService:
    """기상청 단기예보 API 서비스"""

    def __init__(self, api_key: str = None, endpoint: str = None):
        """
        WeatherService 초기화

        Args:
            api_key: 기상청 API 인증키 (기본값: 환경변수 KMA_API_KEY)
            endpoint: API 엔드포인트 (기본값: 환경변수 KMA_API_ENDPOINT)
        """
        self.api_key = api_key or os.environ.get("KMA_API_KEY")
        self.endpoint = endpoint or os.environ.get("KMA_API_ENDPOINT", "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0")

        if not self.api_key:
            raise ValueError("KMA_API_KEY가 설정되지 않았습니다.")

    def _get_base_datetime(self) -> tuple[str, str]:
        """API 호출용 기준 날짜/시간 계산"""
        now = datetime.now()

        # 단기예보 발표시각: 02, 05, 08, 11, 14, 17, 20, 23시
        base_times = [2, 5, 8, 11, 14, 17, 20, 23]

        current_hour = now.hour
        base_time = None
        base_date = now

        for bt in reversed(base_times):
            if current_hour >= bt + 1:  # 발표 후 1시간 뒤부터 사용 가능
                base_time = bt
                break

        if base_time is None:
            # 전날 23시 데이터 사용
            base_date = now - timedelta(days=1)
            base_time = 23

        return base_date.strftime("%Y%m%d"), f"{base_time:02d}00"

    def get_weather(self, city: str = "서울") -> Optional[WeatherInfo]:
        """
        도시의 현재 날씨 조회

        Args:
            city: 도시명 (기본값: 서울)

        Returns:
            WeatherInfo 객체 또는 None (실패시)
        """
        # 도시 좌표 찾기
        coords = CITY_COORDS.get(city)
        if not coords:
            # 기본값 서울
            coords = CITY_COORDS["서울"]
            city = "서울"

        nx, ny = coords
        base_date, base_time = self._get_base_datetime()

        try:
            url = f"{self.endpoint}/getVilageFcst"
            params = {
                "serviceKey": self.api_key,
                "pageNo": 1,
                "numOfRows": 100,
                "dataType": "JSON",
                "base_date": base_date,
                "base_time": base_time,
                "nx": nx,
                "ny": ny
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # 응답 확인
            if "response" not in data:
                print(f"API 응답 오류: {data}")
                return None

            header = data["response"]["header"]
            if header["resultCode"] != "00":
                print(f"API 오류: {header['resultMsg']}")
                return None

            items = data["response"]["body"]["items"]["item"]

            # 데이터 파싱
            weather_data = {}
            for item in items:
                category = item["category"]
                value = item["fcstValue"]
                weather_data[category] = value

            # 기온 (TMP)
            temperature = float(weather_data.get("TMP", 20))

            # 습도 (REH)
            humidity = int(weather_data.get("REH", 50))

            # 풍속 (WSD)
            wind_speed = float(weather_data.get("WSD", 0))

            # 강수형태 (PTY): 0없음, 1비, 2비/눈, 3눈, 4소나기
            pty = int(weather_data.get("PTY", 0))
            rain = pty in [1, 2, 4]
            snow = pty in [2, 3]

            # 하늘상태 (SKY): 1맑음, 3구름많음, 4흐림
            sky = int(weather_data.get("SKY", 1))
            sky_desc = {1: "맑음", 3: "구름많음", 4: "흐림"}.get(sky, "맑음")

            # 강수형태에 따른 설명 추가
            if pty == 1:
                description = "비"
            elif pty == 2:
                description = "비/눈"
            elif pty == 3:
                description = "눈"
            elif pty == 4:
                description = "소나기"
            else:
                description = sky_desc

            # 체감온도 계산 (간단한 공식)
            # 체감온도 = 기온 - (풍속 * 0.7)
            feels_like = round(temperature - (wind_speed * 0.7), 1)

            return WeatherInfo(
                temperature=temperature,
                feels_like=feels_like,
                humidity=humidity,
                description=description,
                wind_speed=wind_speed,
                city=city,
                rain=rain,
                snow=snow
            )

        except requests.RequestException as e:
            print(f"날씨 정보 조회 실패: {e}")
            return None
        except (KeyError, ValueError) as e:
            print(f"날씨 데이터 파싱 실패: {e}")
            return None
