#!/usr/bin/env python3
"""
레전더리 아이템 목록 페이지 HTML 구조 분석
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.crawler.base_crawler import BaseCrawler

def analyze_legendary_list():
    """레전더리 아이템 목록 페이지 구조 분석"""
    with BaseCrawler(delay=0.5) as crawler:
        url = "https://tlidb.com/en/Legendary_Gear"

        print("=" * 70)
        print(f"레전더리 아이템 목록 페이지 분석")
        print("=" * 70)

        soup = crawler.fetch_page(url)
        if not soup:
            print("Failed to fetch page")
            return

        # 아이템 이미지 찾기
        item_images = soup.find_all('img', src=lambda x: x and 'Icon_Equip_' in x)
        print(f"\nFound {len(item_images)} item images")

        # 첫 번째 아이템의 주변 구조 상세 분석
        if item_images:
            img = item_images[0]
            print("\n" + "=" * 70)
            print("첫 번째 아이템 주변 구조 분석")
            print("=" * 70)

            # 부모 링크
            link = img.find_parent('a')
            if link:
                print(f"\n링크 href: {link.get('href', '')}")
                print(f"링크 텍스트: '{crawler.extract_text(link)}'")

                # 링크의 부모
                parent = link.parent
                print(f"\n링크의 부모: <{parent.name}> class={parent.get('class')}")

                # 부모의 모든 자식 출력
                print(f"\n부모의 자식 요소들:")
                for i, child in enumerate(parent.children):
                    if hasattr(child, 'name') and child.name:
                        text = child.get_text(strip=True)
                        print(f"  [{i}] <{child.name}> class={child.get('class')}: {text[:80]}")
                    else:
                        text = str(child).strip()
                        if text and text != '\n':
                            print(f"  [{i}] [TEXT]: {text[:80]}")

                # 조부모 확인
                grandparent = parent.parent
                if grandparent:
                    print(f"\n조부모: <{grandparent.name}> class={grandparent.get('class')}")

                    # 조부모의 모든 자식 출력
                    print(f"\n조부모의 자식 요소들:")
                    for i, child in enumerate(grandparent.children):
                        if hasattr(child, 'name') and child.name:
                            text = child.get_text(strip=True)
                            classes = child.get('class', [])
                            print(f"  [{i}] <{child.name}> class={classes}: {text[:120]}")
                        else:
                            text = str(child).strip()
                            if text and text != '\n':
                                print(f"  [{i}] [TEXT]: {text[:120]}")

                # 다음 몇 개 아이템도 비교
                print("\n" + "=" * 70)
                print("두 번째, 세 번째 아이템 이름 확인")
                print("=" * 70)

                for idx in [1, 2]:
                    if idx < len(item_images):
                        img2 = item_images[idx]
                        link2 = img2.find_parent('a')
                        if link2:
                            href = link2.get('href', '')
                            print(f"\n[{idx+1}] href: {href}")

                            # 부모의 형제나 주변 텍스트 확인
                            parent2 = link2.parent
                            if parent2 and parent2.parent:
                                gp = parent2.parent
                                text = gp.get_text(strip=True)
                                print(f"  조부모 텍스트 (처음 200자): {text[:200]}")

if __name__ == "__main__":
    analyze_legendary_list()
