#!/usr/bin/env python3
"""
재능 레벨 효과 크롤링 스크립트
19개 재능의 레벨별 효과를 크롤링하여 DB에 저장
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.crawler.talent_levels_crawler import TalentLevelsCrawler
from backend.database.db import get_db_session


def main():
    """재능 레벨 크롤링 실행"""
    print("=" * 80)
    print("재능 레벨 효과 크롤링 시작")
    print("=" * 80)
    print("\n19개 재능의 레벨별 효과를 크롤링합니다...")
    print("(Level 1, 45, 60, 75 등)\n")

    try:
        with TalentLevelsCrawler(delay=1.5) as crawler:
            # 모든 재능 레벨 크롤링
            talent_levels_data = crawler.crawl_all_talent_levels()

            if not talent_levels_data:
                print("⚠ 재능 레벨 데이터 수집 실패")
                return

            print(f"\n✓ 총 {len(talent_levels_data)}개의 레벨 효과 수집 완료")

            # JSON 저장
            crawler.export_to_json(talent_levels_data)
            print(f"✓ JSON 저장 완료: data/talent_levels.json")

            # DB 저장
            with get_db_session() as db:
                crawler.save_talent_levels_to_db(talent_levels_data, db)
            print(f"✓ 데이터베이스 저장 완료")

            # 통계 출력
            print("\n" + "=" * 80)
            print("수집된 데이터 통계:")
            print("=" * 80)

            # 재능별 카운트
            from collections import Counter
            talent_counts = Counter(d['talent_name'] for d in talent_levels_data)

            for talent, count in sorted(talent_counts.items()):
                print(f"  • {talent}: {count}개 레벨 효과")

            print("\n" + "=" * 80)
            print("재능 레벨 크롤링 완료!")
            print("=" * 80)

    except Exception as e:
        print(f"\n✗ 크롤링 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
