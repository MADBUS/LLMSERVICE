"""데이터베이스 초기화 및 샘플 데이터 삽입"""
import os
from dotenv import load_dotenv
import mysql.connector

# .env.dev 로드
load_dotenv(os.path.join(os.path.dirname(__file__), ".env.dev"))


def run_setup():
    """DB 초기화 및 샘플 데이터 삽입"""

    print(">> MySQL 연결 중...")
    conn = mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "localhost"),
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD", ""),
        charset="utf8mb4"
    )
    cursor = conn.cursor()

    db_name = os.environ.get("MYSQL_DATABASE", "clothing_db")

    print(f">> 데이터베이스 '{db_name}' 생성 중...")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cursor.execute(f"USE {db_name}")

    print(">> 테이블 생성 중...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clothes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            category ENUM('아우터', '상의', '하의', '원피스', '신발', '액세서리') NOT NULL,
            color ENUM('블랙', '화이트', '그레이', '네이비', '베이지', '브라운', '레드', '블루', '그린', '옐로우', '핑크', '퍼플', '오렌지', '멀티컬러') NOT NULL,
            season ENUM('봄', '여름', '가을', '겨울', '사계절') NOT NULL,
            style ENUM('캐주얼', '포멀', '스포티', '스트릿', '미니멀', '빈티지') NOT NULL,
            description TEXT,
            brand VARCHAR(50),
            image_url VARCHAR(500),
            warmth_level TINYINT DEFAULT 3,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_category (category),
            INDEX idx_season (season),
            INDEX idx_style (style)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)

    # 기존 데이터 확인
    cursor.execute("SELECT COUNT(*) FROM clothes")
    count = cursor.fetchone()[0]

    if count > 0:
        print(f">> 이미 {count}개의 옷이 등록되어 있습니다.")
    else:
        print(">> 샘플 데이터 삽입 중...")

        sample_data = [
            # 아우터 (6개)
            ('검정 롱패딩', '아우터', '블랙', '겨울', '캐주얼', '무릎까지 오는 따뜻한 롱패딩', '노스페이스', 5),
            ('베이지 트렌치코트', '아우터', '베이지', '가을', '미니멀', '클래식 트렌치코트', '버버리', 3),
            ('네이비 블레이저', '아우터', '네이비', '사계절', '포멀', '비즈니스 자켓', '지오다노', 2),
            ('카키 야상', '아우터', '그린', '봄', '캐주얼', '밀리터리 야상 점퍼', '유니클로', 3),
            ('그레이 후드집업', '아우터', '그레이', '봄', '스포티', '운동용 후드 집업', '나이키', 2),
            ('브라운 가죽자켓', '아우터', '브라운', '가을', '스트릿', '빈티지 라이더 자켓', '올세인츠', 3),
            # 상의 (8개)
            ('흰색 기본 티셔츠', '상의', '화이트', '여름', '캐주얼', '깔끔한 면 티셔츠', '무인양품', 1),
            ('네이비 옥스포드 셔츠', '상의', '네이비', '사계절', '포멀', '비즈니스 캐주얼 셔츠', '랄프로렌', 2),
            ('스트라이프 셔츠', '상의', '블루', '봄', '캐주얼', '파란 줄무늬 셔츠', '자라', 2),
            ('그레이 캐시미어 니트', '상의', '그레이', '겨울', '미니멀', '캐시미어 스웨터', '유니클로', 4),
            ('검정 터틀넥', '상의', '블랙', '겨울', '미니멀', '따뜻한 터틀넥', 'COS', 4),
            ('베이지 맨투맨', '상의', '베이지', '가을', '캐주얼', '오버핏 맨투맨', '아디다스', 3),
            ('핑크 블라우스', '상의', '핑크', '봄', '포멀', '실크 블라우스', '마시모두띠', 2),
            ('화이트 크롭탑', '상의', '화이트', '여름', '스트릿', '시원한 크롭 티', 'H&M', 1),
            # 하의 (6개)
            ('검정 슬랙스', '하의', '블랙', '사계절', '포멀', '정장 바지', '지오다노', 3),
            ('인디고 청바지', '하의', '블루', '사계절', '캐주얼', '스트레이트핏 데님', '리바이스', 3),
            ('베이지 치노팬츠', '하의', '베이지', '봄', '캐주얼', '면 치노 팬츠', '갭', 2),
            ('화이트 와이드팬츠', '하의', '화이트', '여름', '미니멀', '린넨 와이드 팬츠', '자라', 1),
            ('그레이 조거팬츠', '하의', '그레이', '사계절', '스포티', '운동용 조거', '나이키', 3),
            ('네이비 반바지', '하의', '네이비', '여름', '캐주얼', '여름용 반바지', '폴로', 1),
            # 신발 (5개)
            ('흰색 운동화', '신발', '화이트', '사계절', '캐주얼', '캔버스 스니커즈', '컨버스', 2),
            ('검정 로퍼', '신발', '블랙', '사계절', '포멀', '가죽 로퍼', '콜한', 2),
            ('브라운 첼시부츠', '신발', '브라운', '겨울', '캐주얼', '가죽 앵클부츠', '닥터마틴', 4),
            ('베이지 슬립온', '신발', '베이지', '여름', '미니멀', '캔버스 슬립온', '반스', 1),
            ('네이비 러닝화', '신발', '네이비', '사계절', '스포티', '러닝화', '뉴발란스', 2),
            # 액세서리 (4개)
            ('블랙 가죽벨트', '액세서리', '블랙', '사계절', '포멀', '소가죽 벨트', '몽블랑', 2),
            ('베이지 버킷햇', '액세서리', '베이지', '여름', '캐주얼', '면 버킷햇', '캉골', 1),
            ('그레이 머플러', '액세서리', '그레이', '겨울', '미니멀', '울 머플러', '아크네', 5),
            ('브라운 토트백', '액세서리', '브라운', '사계절', '캐주얼', '가죽 토트백', '코치', 2),
        ]

        sql = """
            INSERT INTO clothes (name, category, color, season, style, description, brand, warmth_level)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.executemany(sql, sample_data)
        conn.commit()
        print(f">> {len(sample_data)}개의 샘플 옷 데이터 추가 완료!")

    # 결과 확인
    cursor.execute("SELECT category, COUNT(*) FROM clothes GROUP BY category")
    print("\n[카테고리별 옷 개수]")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}개")

    cursor.close()
    conn.close()
    print("\n>> 데이터베이스 설정 완료!")


if __name__ == "__main__":
    try:
        run_setup()
    except mysql.connector.Error as e:
        print(f"MySQL 오류: {e}")
        print("\nMySQL이 실행 중인지 확인해주세요.")
