#!/usr/bin/env python3
"""
아이템 크롤러 v2 테스트 - 샘플만 크롤링
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.crawler.legendary_items_crawler_v2 import LegendaryItemsCrawlerV2
import json

def test_sample_items():
    """샘플 아이템 몇 개만 테스트"""
    print("=" * 70)
    print("아이템 크롤러 v2 샘플 테스트")
    print("=" * 70)

    with LegendaryItemsCrawlerV2(delay=0.5) as crawler:
        # 아이템 목록 페이지 크롤링
        url = crawler.LEGENDARY_GEAR_URL

        print(f"\n아이템 목록 크롤링: {url}")
        soup = crawler.fetch_page(url)

        if not soup:
            print("Failed to fetch page")
            return

        # 아이템 이미지 찾기
        item_images = soup.find_all('img', src=lambda x: x and 'Icon_Equip_' in x)
        print(f"Found {len(item_images)} item images")

        # 처음 5개만 테스트
        test_count = min(5, len(item_images))
        print(f"\n처음 {test_count}개 아이템 정보 크롤링...\n")

        items = []
        for i, img in enumerate(item_images[:test_count]):
            link = img.find_parent('a')
            if link:
                item_data = crawler._parse_item_card(link, img)

                if item_data:
                    print(f"[{i+1}] {item_data['name']}")
                    print(f"    타입: {item_data['type']}")
                    print(f"    슬롯: {item_data['slot']}")
                    print(f"    요구 레벨: {item_data.get('required_level', 'N/A')}")

                    # 특수 효과
                    effects = json.loads(item_data['special_effects'])
                    print(f"    특수 효과 ({len(effects)}개):")
                    for effect in effects[:3]:  # 처음 3개만 표시
                        print(f"      - {effect}")
                    if len(effects) > 3:
                        print(f"      ... 외 {len(effects) - 3}개")
                    print()

                    items.append(item_data)

        # 결과 저장
        output_file = project_root / "data" / "legendary_items_v2_sample.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

        print(f"\n✓ 샘플 데이터 저장: {output_file}")
        print("=" * 70)

if __name__ == "__main__":
    test_sample_items()
