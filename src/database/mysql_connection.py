"""MySQL 데이터베이스 연결 관리"""
import os
from typing import Optional
import mysql.connector
from mysql.connector import pooling


class MySQLConnection:
    """MySQL 연결 풀 관리 클래스"""

    _pool: Optional[pooling.MySQLConnectionPool] = None

    @classmethod
    def get_pool(cls) -> pooling.MySQLConnectionPool:
        """연결 풀 가져오기 (싱글톤)"""
        if cls._pool is None:
            cls._pool = pooling.MySQLConnectionPool(
                pool_name="clothing_pool",
                pool_size=5,
                host=os.environ.get("MYSQL_HOST", "localhost"),
                port=int(os.environ.get("MYSQL_PORT", "3306")),
                user=os.environ.get("MYSQL_USER", "root"),
                password=os.environ.get("MYSQL_PASSWORD", ""),
                database=os.environ.get("MYSQL_DATABASE", "clothing_db"),
                charset="utf8mb4"
            )
        return cls._pool

    @classmethod
    def get_connection(cls):
        """연결 가져오기"""
        return cls.get_pool().get_connection()

    @classmethod
    def init_database(cls):
        """데이터베이스 및 테이블 초기화"""
        # 먼저 데이터베이스 없이 연결
        conn = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),
            port=int(os.environ.get("MYSQL_PORT", "3306")),
            user=os.environ.get("MYSQL_USER", "root"),
            password=os.environ.get("MYSQL_PASSWORD", ""),
            charset="utf8mb4"
        )
        cursor = conn.cursor()

        db_name = os.environ.get("MYSQL_DATABASE", "clothing_db")

        # 데이터베이스 생성
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE {db_name}")

        # 옷 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clothes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL COMMENT '옷 이름',
                category ENUM('아우터', '상의', '하의', '원피스', '신발', '액세서리') NOT NULL COMMENT '카테고리',
                color ENUM('블랙', '화이트', '그레이', '네이비', '베이지', '브라운', '레드', '블루', '그린', '옐로우', '핑크', '퍼플', '오렌지', '멀티컬러') NOT NULL COMMENT '색상',
                season ENUM('봄', '여름', '가을', '겨울', '사계절') NOT NULL COMMENT '계절',
                style ENUM('캐주얼', '포멀', '스포티', '스트릿', '미니멀', '빈티지') NOT NULL COMMENT '스타일',
                description TEXT COMMENT '상세 설명',
                brand VARCHAR(50) COMMENT '브랜드',
                image_url VARCHAR(500) COMMENT '이미지 URL',
                warmth_level TINYINT DEFAULT 3 COMMENT '보온성 (1: 시원 ~ 5: 따뜻)',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_category (category),
                INDEX idx_season (season),
                INDEX idx_style (style)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)

        conn.commit()
        cursor.close()
        conn.close()

        print(f"데이터베이스 '{db_name}' 및 테이블 초기화 완료")
