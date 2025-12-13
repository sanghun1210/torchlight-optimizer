#!/usr/bin/env python3
"""
재능 노드 크롤러 테스트 - 샘플만 크롤링
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.crawler.talent_nodes_crawler import TalentNodesCrawler
import json

def test_sample_talent_nodes():
    """샘플 재능 노드 몇 개만 테스트"""
    print("=" * 70)
    print("재능 노드 크롤러 샘플 테스트")
    print("=" * 70)

    with TalentNodesCrawler(delay=0.5) as crawler:
        # 재능 노드 크롤링
        nodes_data = crawler.crawl_talent_nodes()

        if not nodes_data:
            print("No talent nodes data collected")
            return

        print(f"\n총 {len(nodes_data)}개 재능 노드 수집")

        # 코어 노드와 일반 노드 분리
        core_nodes = [n for n in nodes_data if n['node_type'] == 'Core']
        regular_nodes = [n for n in nodes_data if n['node_type'] == 'Regular']

        print(f"  - 코어 노드: {len(core_nodes)}개")
        print(f"  - 일반 노드: {len(regular_nodes)}개")

        # 코어 노드 샘플 3개
        print("\n" + "=" * 70)
        print("코어 재능 노드 샘플 3개:")
        print("=" * 70)

        for i, node in enumerate(core_nodes[:3]):
            print(f"\n[{i+1}] {node['name']}")
            print(f"    타입: {node['node_type']}")
            print(f"    God/클래스: {node.get('god_class', 'N/A')}")
            print(f"    효과: {node['effect'][:150]}...")

        # 일반 노드 샘플 3개
        print("\n" + "=" * 70)
        print("일반 재능 노드 샘플 3개:")
        print("=" * 70)

        for i, node in enumerate(regular_nodes[:3]):
            print(f"\n[{i+1}] {node['name']}")
            print(f"    타입: {node['node_type']}")
            print(f"    Tier: {node.get('tier', 'N/A')}")
            print(f"    God/클래스: {node.get('god_class', 'N/A')}")
            print(f"    효과: {node['effect'][:100]}")

        # 샘플 저장 (코어 3개 + 일반 3개)
        sample_data = core_nodes[:3] + regular_nodes[:3]

        output_file = project_root / "data" / "talent_nodes_sample.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)

        print(f"\n\n✓ 샘플 데이터 저장: {output_file}")
        print("=" * 70)

if __name__ == "__main__":
    test_sample_talent_nodes()
