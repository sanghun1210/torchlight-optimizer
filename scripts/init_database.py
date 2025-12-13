#!/usr/bin/env python3
"""
데이터베이스 초기화 스크립트
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.database.models import Base
from backend.database.db import engine


def init_database():
    """데이터베이스 테이블 생성"""
    print("=" * 70)
    print("데이터베이스 초기화")
    print("=" * 70)

    # 모든 테이블 생성
    print("\n테이블 생성 중...")
    Base.metadata.create_all(bind=engine)

    print("✓ 다음 테이블이 생성되었습니다:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")

    print("\n" + "=" * 70)
    print("✓ 데이터베이스 초기화 완료!")
    print("=" * 70)
    print("\n다음 단계:")
    print("  1. 데이터 크롤링: python scripts/crawl_all_data.py")
    print("  2. API 서버 실행: python scripts/run_api_server.py")
    print("=" * 70)


if __name__ == "__main__":
    init_database()
