#!/usr/bin/env python3
"""
영웅 페이지 원본 HTML 확인
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.crawler.base_crawler import BaseCrawler

def show_raw_html():
    """원본 HTML 내용 확인"""
    with BaseCrawler(delay=0.5) as crawler:
        url = "https://tlidb.com/en/Seething_Silhouette"

        print(f"Fetching: {url}\n")
        soup = crawler.fetch_page(url)

        if not soup:
            print("Failed to fetch page")
            return

        # 전체 텍스트 내용
        print("=" * 70)
        print("페이지 전체 텍스트 (처음 2000자)")
        print("=" * 70)
        all_text = soup.get_text(separator=' ', strip=True)
        print(all_text[:2000])

        print("\n" + "=" * 70)
        print("'Seething' 키워드 검색")
        print("=" * 70)
        seething_elements = soup.find_all(string=lambda x: x and 'Seething' in str(x))
        print(f"Found {len(seething_elements)} elements containing 'Seething'")
        for i, elem in enumerate(seething_elements[:5]):
            print(f"\n[{i}] '{elem.strip()}'")
            parent = elem.find_parent() if hasattr(elem, 'find_parent') else None
            if parent:
                print(f"  부모: <{parent.name}> class={parent.get('class')}")

        print("\n" + "=" * 70)
        print("모든 이미지 확인")
        print("=" * 70)
        images = soup.find_all('img', limit=10)
        for i, img in enumerate(images):
            src = img.get('src', '')
            alt = img.get('alt', '')
            print(f"[{i}] src={src[:80]}, alt={alt}")

if __name__ == "__main__":
    show_raw_html()
