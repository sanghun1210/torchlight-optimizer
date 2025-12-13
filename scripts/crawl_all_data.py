#!/usr/bin/env python3
"""
전체 데이터 크롤링 - 모든 크롤러 실행
"""
import sys
from pathlib import Path
import logging

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.crawler.skills_crawler_v2 import SkillsCrawlerV2
from backend.crawler.heroes_crawler_v2 import HeroesCrawlerV2
from backend.crawler.legendary_items_crawler_v2 import LegendaryItemsCrawlerV2
from backend.crawler.talent_nodes_crawler import TalentNodesCrawler
from backend.crawler.destiny_crawler import DestinyCrawler
from backend.database.db import get_db_session

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def crawl_all_data():
    """모든 데이터 크롤링 및 저장"""

    print("=" * 80)
    print("Torchlight Infinite 전체 데이터 크롤링 시작")
    print("=" * 80)

    statistics = {}

    # 1. 스킬 크롤링
    print("\n[1/5] 스킬 데이터 크롤링...")
    print("-" * 80)
    try:
        with SkillsCrawlerV2(delay=1.0) as skills_crawler:
            skills_data = skills_crawler.crawl_all_skills()
            statistics['skills'] = len(skills_data)

            if skills_data:
                # JSON 저장
                skills_crawler.export_to_json(skills_data)

                # DB 저장
                with get_db_session() as db:
                    skills_crawler.save_skills_to_db(skills_data, db)

                print(f"✓ 스킬 {len(skills_data)}개 수집 완료")
            else:
                print("⚠ 스킬 데이터 수집 실패")
    except Exception as e:
        logger.error(f"스킬 크롤링 실패: {e}")
        statistics['skills'] = 0

    # 2. 영웅 크롤링
    print("\n[2/5] 영웅 데이터 크롤링...")
    print("-" * 80)
    try:
        with HeroesCrawlerV2(delay=1.0) as heroes_crawler:
            heroes_data = heroes_crawler.crawl_all_heroes()
            statistics['heroes'] = len(heroes_data)

            if heroes_data:
                # JSON 저장
                heroes_crawler.export_to_json(heroes_data)

                # DB 저장
                with get_db_session() as db:
                    heroes_crawler.save_heroes_to_db(heroes_data, db)

                print(f"✓ 영웅(재능) {len(heroes_data)}개 수집 완료")
            else:
                print("⚠ 영웅 데이터 수집 실패")
    except Exception as e:
        logger.error(f"영웅 크롤링 실패: {e}")
        statistics['heroes'] = 0

    # 3. 레전더리 아이템 크롤링
    print("\n[3/5] 레전더리 아이템 데이터 크롤링...")
    print("-" * 80)
    try:
        with LegendaryItemsCrawlerV2(delay=1.0) as items_crawler:
            items_data = items_crawler.crawl_legendary_items()
            statistics['items'] = len(items_data)

            if items_data:
                # JSON 저장
                items_crawler.export_to_json(items_data)

                # DB 저장
                with get_db_session() as db:
                    items_crawler.save_items_to_db(items_data, db)

                print(f"✓ 레전더리 아이템 {len(items_data)}개 수집 완료")
            else:
                print("⚠ 아이템 데이터 수집 실패")
    except Exception as e:
        logger.error(f"아이템 크롤링 실패: {e}")
        statistics['items'] = 0

    # 4. 재능 노드 크롤링
    print("\n[4/5] 재능 노드 데이터 크롤링...")
    print("-" * 80)
    try:
        with TalentNodesCrawler(delay=1.0) as talent_crawler:
            talent_nodes_data = talent_crawler.crawl_talent_nodes()
            statistics['talent_nodes'] = len(talent_nodes_data)

            if talent_nodes_data:
                # JSON 저장
                talent_crawler.export_to_json(talent_nodes_data)

                # DB 저장
                with get_db_session() as db:
                    talent_crawler.save_talent_nodes_to_db(talent_nodes_data, db)

                print(f"✓ 재능 노드 {len(talent_nodes_data)}개 수집 완료")
            else:
                print("⚠ 재능 노드 데이터 수집 실패")
    except Exception as e:
        logger.error(f"재능 노드 크롤링 실패: {e}")
        statistics['talent_nodes'] = 0

    # 5. 운명 크롤링
    print("\n[5/5] 운명(Destiny) 데이터 크롤링...")
    print("-" * 80)
    try:
        with DestinyCrawler(delay=1.0) as destiny_crawler:
            destinies_data = destiny_crawler.crawl_destinies()
            statistics['destinies'] = len(destinies_data)

            if destinies_data:
                # JSON 저장
                destiny_crawler.export_to_json(destinies_data)

                # DB 저장
                with get_db_session() as db:
                    destiny_crawler.save_destinies_to_db(destinies_data, db)

                print(f"✓ 운명 {len(destinies_data)}개 수집 완료")
            else:
                print("⚠ 운명 데이터 수집 실패")
    except Exception as e:
        logger.error(f"운명 크롤링 실패: {e}")
        statistics['destinies'] = 0

    # 최종 통계
    print("\n" + "=" * 80)
    print("전체 데이터 크롤링 완료!")
    print("=" * 80)
    print("\n수집된 데이터 통계:")
    print(f"  • 스킬: {statistics.get('skills', 0)}개")
    print(f"  • 영웅(재능): {statistics.get('heroes', 0)}개")
    print(f"  • 레전더리 아이템: {statistics.get('items', 0)}개")
    print(f"  • 재능 노드: {statistics.get('talent_nodes', 0)}개")
    print(f"  • 운명: {statistics.get('destinies', 0)}개")
    print(f"\n총 데이터: {sum(statistics.values())}개")
    print("\n데이터 저장 위치:")
    print(f"  • JSON: {project_root / 'data'}/*.json")
    print(f"  • 데이터베이스: {project_root / 'torchlight.db'}")
    print("=" * 80)


if __name__ == "__main__":
    crawl_all_data()
