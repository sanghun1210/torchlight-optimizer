#!/usr/bin/env python3
"""
재능 노드 개별 구조 상세 분석
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.crawler.base_crawler import BaseCrawler

def analyze_talent_node_detail():
    """재능 노드 개별 구조 상세 분석"""
    with BaseCrawler(delay=0.5) as crawler:
        url = "https://tlidb.com/en/Talent"

        print("=" * 70)
        print("재능 노드 개별 구조 분석")
        print("=" * 70)

        soup = crawler.fetch_page(url)
        if not soup:
            print("Failed to fetch page")
            return

        # 코어 재능 노드 이미지 찾기
        print("\n" + "=" * 70)
        print("코어 재능 노드 (CoreTalentIcon)")
        print("=" * 70)

        core_images = soup.find_all('img', src=lambda x: x and 'CoreTalentIcon' in x)
        print(f"Found {len(core_images)} core talent node images")

        if core_images:
            # 첫 번째 코어 재능 노드 분석
            img = core_images[0]
            print(f"\n첫 번째 코어 노드 이미지:")
            print(f"  src: {img.get('src', '')[-80:]}")

            # 부모 구조 확인
            link = img.find_parent('a')
            if link:
                print(f"  링크 href: {link.get('href', '')}")

                parent = link.parent
                print(f"  부모: <{parent.name}> class={parent.get('class')}")

                # 조부모
                if parent and parent.parent:
                    grandparent = parent.parent
                    print(f"  조부모: <{grandparent.name}> class={grandparent.get('class')}")

                    # 조부모의 모든 텍스트
                    text = grandparent.get_text(strip=True)
                    print(f"  조부모 텍스트 (처음 300자):\n    {text[:300]}")

        # 일반 재능 노드 이미지 찾기 (TalentIcon)
        print("\n" + "=" * 70)
        print("일반 재능 노드 (TalentIcon)")
        print("=" * 70)

        # CoreTalentIcon이 아닌 Talent 이미지
        talent_images = soup.find_all('img', src=lambda x: x and 'Talent' in x and 'CoreTalentIcon' not in x)
        print(f"Found {len(talent_images)} regular talent node images")

        if talent_images:
            # 첫 번째 일반 재능 노드 분석
            img = talent_images[0]
            print(f"\n첫 번째 일반 노드 이미지:")
            print(f"  src: {img.get('src', '')[-80:]}")

            # 부모 구조 확인
            link = img.find_parent('a')
            if link:
                print(f"  링크 href: {link.get('href', '')}")

                parent = link.parent
                print(f"  부모: <{parent.name}> class={parent.get('class')}")

                # 조부모
                if parent and parent.parent:
                    grandparent = parent.parent
                    print(f"  조부모: <{grandparent.name}> class={grandparent.get('class')}")

                    # 조부모의 모든 텍스트
                    text = grandparent.get_text(strip=True)
                    print(f"  조부모 텍스트 (처음 300자):\n    {text[:300]}")

        # Border div 구조 분석
        print("\n" + "=" * 70)
        print("Border div 구조 분석")
        print("=" * 70)

        borders = soup.find_all('div', class_=lambda x: x and 'border' in str(x).lower())
        print(f"Total border divs: {len(borders)}")

        # 이미지를 포함한 border div 찾기
        borders_with_talent = []
        for border in borders:
            if border.find('img', src=lambda x: x and 'Talent' in x):
                borders_with_talent.append(border)

        print(f"Border divs with Talent images: {len(borders_with_talent)}")

        # 코어 재능 노드와 일반 재능 노드 분리
        core_borders = []
        regular_borders = []

        for border in borders_with_talent:
            img = border.find('img', src=lambda x: x and 'Talent' in x)
            if img:
                src = img.get('src', '')
                if 'CoreTalentIcon' in src:
                    core_borders.append(border)
                else:
                    regular_borders.append(border)

        print(f"\n코어 재능 노드: {len(core_borders)}개")
        print(f"일반 재능 노드: {len(regular_borders)}개")

        # 코어 재능 노드 샘플
        print("\n" + "=" * 70)
        print("코어 재능 노드 샘플 3개:")
        print("=" * 70)
        for i, border in enumerate(core_borders[:3]):
            print(f"\n[{i+1}]")
            img = border.find('img', src=lambda x: x and 'Talent' in x)
            if img:
                print(f"  이미지: {img.get('src', '')[-60:]}")
            text = border.get_text(strip=True)
            print(f"  텍스트: {text[:250]}")

        # 일반 재능 노드 샘플 (처음 31개는 직업일 가능성)
        print("\n" + "=" * 70)
        print("일반 재능 노드 샘플 (32번째부터 3개):")
        print("=" * 70)
        for i, border in enumerate(regular_borders[31:34]):  # 32, 33, 34번째
            print(f"\n[{i+32}]")
            img = border.find('img', src=lambda x: x and 'Talent' in x)
            if img:
                print(f"  이미지: {img.get('src', '')[-60:]}")
            text = border.get_text(strip=True)
            print(f"  텍스트: {text[:250]}")

if __name__ == "__main__":
    analyze_talent_node_detail()
