#!/usr/bin/env python3
"""
영웅 페이지 HTML 구조 분석
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.crawler.base_crawler import BaseCrawler

def analyze_hero_structure():
    """영웅 페이지 구조 상세 분석"""
    with BaseCrawler(delay=0.5) as crawler:
        # 샘플 URL들
        test_urls = [
            "https://tlidb.com/en/Seething_Silhouette",
            "https://tlidb.com/en/Ranger_of_Glory",
        ]

        for url in test_urls:
            print("=" * 70)
            print(f"분석 중: {url}")
            print("=" * 70)

            soup = crawler.fetch_page(url)
            if not soup:
                print("Failed to fetch page")
                continue

            # 1. 페이지 제목
            title = soup.find('title')
            print(f"\n페이지 제목: {title.get_text(strip=True) if title else 'N/A'}")

            # 2. Hero Portrait 이미지
            print("\n" + "-" * 70)
            print("Hero Portrait 이미지:")
            portraits = soup.find_all('img', src=lambda x: x and 'Portrait' in x)
            for i, img in enumerate(portraits[:3]):
                print(f"  [{i}] {img.get('src', '')}")

            # 3. God Type 찾기
            print("\n" + "-" * 70)
            print("God/Class 타입 정보:")
            # "God of" 패턴 찾기
            god_elements = soup.find_all(string=lambda x: x and 'God of' in str(x))
            if god_elements:
                for elem in god_elements[:3]:
                    print(f"  - '{elem.strip()}'")
                    parent = elem.find_parent() if hasattr(elem, 'find_parent') else None
                    if parent:
                        print(f"    부모: <{parent.name}> class={parent.get('class')}")

            # 4. 영웅 이름
            print("\n" + "-" * 70)
            print("영웅 이름 찾기:")
            # h1, h2 태그에서 영웅 이름 찾기
            headers = soup.find_all(['h1', 'h2'])
            for h in headers[:5]:
                text = h.get_text(strip=True)
                if text and len(text) < 50:
                    print(f"  <{h.name}>: {text}")

            # 5. 설명/Description
            print("\n" + "-" * 70)
            print("설명 찾기:")
            # "Description" 또는 설명으로 보이는 텍스트 찾기
            desc_keywords = ['Description', 'Trait', 'Talent', 'Ability']
            for keyword in desc_keywords:
                elements = soup.find_all(string=lambda x: x and keyword in str(x))
                if elements:
                    print(f"\n  '{keyword}' 포함 요소: {len(elements)}개")
                    elem = elements[0]
                    parent = elem.find_parent() if hasattr(elem, 'find_parent') else None
                    if parent:
                        print(f"    부모: <{parent.name}> class={parent.get('class')}")
                        print(f"    텍스트: {parent.get_text(strip=True)[:150]}")

                        # 다음 형제
                        next_sib = parent.find_next_sibling()
                        if next_sib:
                            print(f"    다음 형제: <{next_sib.name}> class={next_sib.get('class')}")
                            print(f"    텍스트: {next_sib.get_text(strip=True)[:200]}")

            # 6. 태그/스탯 정보
            print("\n" + "-" * 70)
            print("태그/스탯 정보:")
            # span 태그들 확인
            spans = soup.find_all('span', limit=20)
            print(f"  상위 20개 span 태그:")
            for i, span in enumerate(spans):
                text = span.get_text(strip=True)
                if text and len(text) < 30:
                    print(f"    [{i}] {text}")

            print("\n")

if __name__ == "__main__":
    analyze_hero_structure()
