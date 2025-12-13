#!/usr/bin/env python3
"""
운명(Destiny) 페이지 HTML 구조 분석
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.crawler.base_crawler import BaseCrawler

def analyze_destiny_page():
    """운명 페이지 구조 분석"""
    with BaseCrawler(delay=0.5) as crawler:
        url = "https://tlidb.com/en/Destiny"

        print("=" * 70)
        print(f"운명(Destiny) 페이지 분석: {url}")
        print("=" * 70)

        soup = crawler.fetch_page(url)
        if not soup:
            print("Failed to fetch page")
            return

        # 페이지 전체 텍스트 (처음 2000자)
        print("\n페이지 텍스트 (처음 2000자):")
        print("-" * 70)
        all_text = soup.get_text(separator=' ', strip=True)
        print(all_text[:2000])

        # 'Destiny' 키워드 검색
        print("\n" + "=" * 70)
        print("'Destiny' 키워드 검색")
        print("=" * 70)
        destiny_elements = soup.find_all(string=lambda x: x and 'Destiny' in str(x))
        print(f"Found {len(destiny_elements)} 'Destiny' elements")

        # 이미지 검색
        print("\n" + "=" * 70)
        print("이미지 검색")
        print("=" * 70)

        # 다양한 패턴으로 이미지 찾기
        patterns = ['Destiny', 'Icon', 'Fate', 'Fortune']
        for pattern in patterns:
            images = soup.find_all('img', src=lambda x: x and pattern in x)
            if images:
                print(f"\n'{pattern}' 패턴 이미지: {len(images)}개")
                for i, img in enumerate(images[:3]):
                    src = img.get('src', '')
                    print(f"  [{i}] {src[-80:]}")

        # Border div 구조 확인
        print("\n" + "=" * 70)
        print("Border div 구조")
        print("=" * 70)

        borders = soup.find_all('div', class_=lambda x: x and 'border' in str(x).lower())
        print(f"Total border divs: {len(borders)}")

        if borders:
            # 첫 3개 샘플
            print("\n샘플 border div 3개:")
            for i, border in enumerate(borders[:3]):
                print(f"\n[{i+1}] Border div:")
                print(f"  class: {border.get('class')}")

                # 이미지 찾기
                img = border.find('img')
                if img:
                    src = img.get('src', '')
                    print(f"  이미지: {src[-60:]}")

                # 텍스트 내용
                text = border.get_text(strip=True)
                print(f"  텍스트 (처음 200자): {text[:200]}")

        # 링크 검색
        print("\n" + "=" * 70)
        print("Destiny 관련 링크 검색")
        print("=" * 70)
        links = soup.find_all('a', href=True)
        destiny_links = [link for link in links if 'destiny' in link.get('href', '').lower()]
        print(f"Found {len(destiny_links)} destiny-related links")
        for i, link in enumerate(destiny_links[:5]):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            print(f"  [{i}] href={href}, text={text[:50]}")

if __name__ == "__main__":
    analyze_destiny_page()
