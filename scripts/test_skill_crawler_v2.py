#!/usr/bin/env python3
"""
스킬 크롤러 v2 테스트 - 샘플만 크롤링
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.crawler.skills_crawler_v2 import SkillsCrawlerV2
import json

def test_sample_skills():
    """샘플 스킬 몇 개만 테스트"""
    print("=" * 70)
    print("스킬 크롤러 v2 샘플 테스트")
    print("=" * 70)

    with SkillsCrawlerV2(delay=0.5) as crawler:
        # Active Skill 몇 개만 테스트
        url = "https://tlidb.com/en/Active_Skill"
        category = "Active"

        print(f"\n{category} 스킬 목록 크롤링...")
        soup = crawler.fetch_page(url)

        if not soup:
            print("Failed to fetch page")
            return

        # 스킬 이미지 찾기
        skill_images = soup.find_all('img', src=lambda x: x and 'Icon_Skill_' in x)
        print(f"Found {len(skill_images)} skill images")

        # 처음 3개만 테스트
        test_count = min(3, len(skill_images))
        print(f"\n처음 {test_count}개 스킬 상세 정보 크롤링...\n")

        skills = []
        for i, img in enumerate(skill_images[:test_count]):
            link = img.find_parent('a')
            if link:
                href = link.get('href', '')
                skill_url = crawler.get_absolute_url(href)

                # 기본 정보
                name = crawler._extract_skill_name(link, img)
                image_url = img.get('src', '')

                print(f"[{i+1}] {name}")
                print(f"    URL: {skill_url}")
                print(f"    이미지: {image_url[-50:]}")

                # 상세 정보
                details = crawler._fetch_skill_details(skill_url)

                print(f"    태그: {details['tags']}")
                print(f"    데미지 타입: {details['damage_type']}")
                print(f"    마나 코스트: {details['mana_cost']}")
                print(f"    쿨다운: {details['cooldown']}")
                print(f"    설명: {details['description'][:100] if details['description'] else 'N/A'}...")
                print()

                skill_data = {
                    'name': name,
                    'type': category,
                    'url': skill_url,
                    'image_url': image_url,
                    **details
                }
                skills.append(skill_data)

        # 결과 저장
        output_file = project_root / "data" / "skills_v2_sample.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(skills, f, ensure_ascii=False, indent=2)

        print(f"\n✓ 샘플 데이터 저장: {output_file}")
        print("=" * 70)

if __name__ == "__main__":
    test_sample_skills()
