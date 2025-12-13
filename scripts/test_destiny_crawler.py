#!/usr/bin/env python3
"""
운명 크롤러 테스트 - 샘플만 크롤링
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.crawler.destiny_crawler import DestinyCrawler
import json

def test_sample_destinies():
    """샘플 운명 몇 개만 테스트"""
    print("=" * 70)
    print("운명 크롤러 샘플 테스트")
    print("=" * 70)

    with DestinyCrawler(delay=0.5) as crawler:
        # 운명 크롤링
        destinies_data = crawler.crawl_destinies()

        if not destinies_data:
            print("No destinies data collected")
            return

        print(f"\n총 {len(destinies_data)}개 운명 수집")

        # Tier별 분류
        tier_counts = {}
        for destiny in destinies_data:
            tier = destiny.get('tier', 'Unknown')
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

        print("\nTier별 통계:")
        for tier, count in sorted(tier_counts.items(), key=lambda x: (x[0] is None, x[0])):
            tier_name = tier if tier else 'Unknown'
            print(f"  - {tier_name}: {count}개")

        # 샘플 5개
        print("\n" + "=" * 70)
        print("운명 샘플 5개:")
        print("=" * 70)

        for i, destiny in enumerate(destinies_data[:5]):
            print(f"\n[{i+1}] {destiny['name']}")
            print(f"    Tier: {destiny.get('tier', 'N/A')}")
            print(f"    Category: {destiny.get('category', 'N/A')}")
            print(f"    Stat Range: {destiny.get('stat_range', 'N/A')}")
            print(f"    효과: {destiny['effect'][:100]}")

        # 샘플 저장 (처음 10개)
        sample_data = destinies_data[:10]

        output_file = project_root / "data" / "destinies_sample.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)

        print(f"\n\n✓ 샘플 데이터 저장: {output_file}")
        print("=" * 70)

if __name__ == "__main__":
    test_sample_destinies()
