#!/usr/bin/env python3
"""
스킬 크롤러 v2 디버그 테스트
"""
import sys
import logging
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 디버그 레벨 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from backend.crawler.skills_crawler_v2 import SkillsCrawlerV2

def test_single_skill():
    """단일 스킬 디버그 테스트"""
    print("=" * 70)
    print("단일 스킬 디버그 테스트")
    print("=" * 70)

    with SkillsCrawlerV2(delay=0.5) as crawler:
        skill_url = "https://tlidb.com/Leap_Attack"

        print(f"\n크롤링: {skill_url}\n")
        details = crawler._fetch_skill_details(skill_url)

        print("\n" + "=" * 70)
        print("추출된 상세 정보:")
        print("=" * 70)
        for key, value in details.items():
            if key == 'description':
                print(f"{key}: {value[:200] if value else '(empty)'}...")
            else:
                print(f"{key}: {value}")

if __name__ == "__main__":
    test_single_skill()
