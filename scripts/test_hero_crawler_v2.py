#!/usr/bin/env python3
"""
영웅 크롤러 v2 테스트 - 샘플만 크롤링
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.crawler.heroes_crawler_v2 import HeroesCrawlerV2
import json

def test_sample_heroes():
    """샘플 영웅 몇 개만 테스트"""
    print("=" * 70)
    print("영웅 크롤러 v2 샘플 테스트")
    print("=" * 70)

    with HeroesCrawlerV2(delay=0.5) as crawler:
        # 영웅 목록 페이지 크롤링
        url = crawler.HEROES_URL

        print(f"\n영웅 목록 크롤링: {url}")
        soup = crawler.fetch_page(url)

        if not soup:
            print("Failed to fetch page")
            return

        # 영웅 이미지 찾기
        hero_images = soup.find_all('img', src=lambda x: x and 'Portrait' in x)
        print(f"Found {len(hero_images)} hero images")

        # 처음 3개만 테스트
        test_count = min(3, len(hero_images))
        print(f"\n처음 {test_count}개 영웅 상세 정보 크롤링...\n")

        heroes = []
        for i, img in enumerate(hero_images[:test_count]):
            link = img.find_parent('a')
            if link:
                href = link.get('href', '')
                hero_url = crawler.get_absolute_url(href)
                link_text = crawler.extract_text(link)
                image_url = img.get('src', '')

                print(f"[{i+1}] 링크 텍스트: {link_text}")
                print(f"    URL: {hero_url}")
                print(f"    이미지: {image_url[-50:]}")

                # 상세 정보
                details = crawler._fetch_hero_details(hero_url, link_text)

                print(f"    영웅 이름: {details['name']}")
                print(f"    God/클래스: {details['god_type']}")
                print(f"    재능: {details['talent']}")
                print(f"    설명: {details['description'][:100] if details['description'] else 'N/A'}...")
                print()

                hero_data = {
                    'talent_url': hero_url,
                    'image_url': image_url,
                    'link_text': link_text,
                    **details
                }
                heroes.append(hero_data)

        # 결과 저장
        output_file = project_root / "data" / "heroes_v2_sample.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(heroes, f, ensure_ascii=False, indent=2)

        print(f"\n✓ 샘플 데이터 저장: {output_file}")
        print("=" * 70)

if __name__ == "__main__":
    test_sample_heroes()
