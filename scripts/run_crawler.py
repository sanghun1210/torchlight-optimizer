#!/usr/bin/env python3
"""
토치라이트 인피니트 데이터 크롤러 실행 스크립트

모든 크롤러(영웅, 스킬, 아이템)를 순차적으로 실행하여
데이터를 수집하고 데이터베이스에 저장합니다.
"""
import sys
import logging
from pathlib import Path

# 프로젝트 루트를 파이썬 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.database.db import create_tables
from backend.crawler.heroes_crawler import HeroesCrawler
from backend.crawler.skills_crawler import SkillsCrawler
from backend.crawler.legendary_items_crawler import LegendaryItemsCrawler
from backend.database.db import get_db_session

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(project_root / 'data' / 'crawler.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def main():
    """크롤러 메인 실행 함수"""
    print("=" * 60)
    print("Torchlight Infinite Data Crawler")
    print("=" * 60)

    # 1. 데이터베이스 초기화
    logger.info("Step 1: Initializing database...")
    try:
        create_tables()
        print("✓ Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return

    # 2. 영웅 데이터 크롤링
    logger.info("\nStep 2: Crawling heroes data...")
    try:
        with HeroesCrawler(delay=1.0) as crawler:
            heroes_data = crawler.crawl_heroes_list()
            if heroes_data:
                crawler.export_to_json(heroes_data, "heroes.json")
                with get_db_session() as db:
                    crawler.save_heroes_to_db(heroes_data, db)
                print(f"✓ Crawled {len(heroes_data)} heroes")
            else:
                print("⚠ No heroes data found")
    except Exception as e:
        logger.error(f"Error during heroes crawling: {e}")
        print(f"✗ Heroes crawling failed: {e}")

    # 3. 스킬 데이터 크롤링
    logger.info("\nStep 3: Crawling skills data...")
    try:
        with SkillsCrawler(delay=1.0) as crawler:
            skills_data = crawler.crawl_all_skills()
            if skills_data:
                crawler.export_to_json(skills_data, "skills.json")
                with get_db_session() as db:
                    crawler.save_skills_to_db(skills_data, db)
                print(f"✓ Crawled {len(skills_data)} skills")
            else:
                print("⚠ No skills data found")
    except Exception as e:
        logger.error(f"Error during skills crawling: {e}")
        print(f"✗ Skills crawling failed: {e}")

    # 4. 레전드 아이템 데이터 크롤링
    logger.info("\nStep 4: Crawling legendary items data...")
    try:
        with LegendaryItemsCrawler(delay=1.0) as crawler:
            items_data = crawler.crawl_legendary_items()
            if items_data:
                crawler.export_to_json(items_data, "legendary_items.json")
                with get_db_session() as db:
                    crawler.save_items_to_db(items_data, db)
                print(f"✓ Crawled {len(items_data)} legendary items")
            else:
                print("⚠ No legendary items data found")
    except Exception as e:
        logger.error(f"Error during legendary items crawling: {e}")
        print(f"✗ Legendary items crawling failed: {e}")

    # 5. 완료
    print("\n" + "=" * 60)
    print("Crawling completed!")
    print("=" * 60)

    # 데이터베이스 통계 출력
    try:
        from backend.database.models import Hero, Skill, Item

        with get_db_session() as db:
            hero_count = db.query(Hero).count()
            skill_count = db.query(Skill).count()
            item_count = db.query(Item).count()

            print(f"\nDatabase Statistics:")
            print(f"  Heroes:          {hero_count}")
            print(f"  Skills:          {skill_count}")
            print(f"  Legendary Items: {item_count}")
            print(f"  Total:           {hero_count + skill_count + item_count}")

    except Exception as e:
        logger.error(f"Error getting database statistics: {e}")


if __name__ == "__main__":
    main()
